---
category: incident-response
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/Sentry%20Playbooks/01-Error-Tracking/ValidationError-DataValidation-Error-application.md)'
role: SRE / Application Error Response
origin: scoutflo
extract_date: 2026-03-05
tags:
- application
- datavalidation
- monitoring
- sentry
- validationerror
---

# ValidationError-DataValidation-Error-application — 데이터 유효성 검사 에러

## 의미

데이터 유효성 검사 에러가 발생합니다 (Sentry 에러 이슈 트리거, 예외 유형 ValidationError). 데이터 유효성 검사가 실패하여 입력 데이터가 유효성 검사 요구사항을 충족하지 못할 때 애플리케이션 작업이 실패합니다. Sentry Issue Details 페이지에 "validation error", "invalid data", "validation failed" 패턴의 에러 메시지가 표시되며, 스택 트레이스는 애플리케이션 유효성 검사 레이어를 가리키고, 에러 레벨은 Error 또는 Warning 심각도를 나타냅니다. 이는 애플리케이션 레이어에 영향을 미치며, 일반적으로 유효하지 않은 입력 데이터, 필수 필드 누락, 또는 유효성 검사 규칙 위반으로 인한 데이터 무결성 문제를 나타냅니다. 에러가 사용자 입력과 연관되면 사용자 행동 모니터링에서 데이터 품질 문제가 확인될 수 있습니다.

## 영향

Sentry 에러 이슈 알림이 발생하고, 데이터 유효성 검사 에러가 발생하며, 애플리케이션 작업이 실패합니다. 애플리케이션이 유효성 검사 에러를 반환하고 사용자에게 영향을 미칩니다. 사용자 입력 유효성 검사가 실패하고, 영향받는 사용자 수가 증가하며, 에러 카운트가 지속적으로 증가합니다. Sentry 대시보드에서 Medium 또는 Low 우선순위로 표시되고, 애플리케이션 기능이 저하되며 사용자 경험 문제가 발생합니다.

## 플레이북

1. 이슈 유형(`metadata.type`), 우선순위(`priority`), 영향받는 사용자 수(`userCount`), 에러 메시지(`metadata.value`)를 포함한 이슈 상세 정보를 확인하여 "validation error", "invalid data", "validation failed" 패턴의 ValidationError를 검증합니다.

2. 이슈 `<issue-id>`의 이벤트를 조회하고 이벤트 패턴을 분석합니다:
   - 최근 이벤트를 조회하여 스택 트레이스 프레임(`entries[].data.values[].stacktrace.frames[]`)을 검사하고 영향받는 유효성 검사 파일을 식별합니다
   - 최근 24시간 동안의 이벤트 빈도(일정, 급증, 점진적 증가)를 분석하고 이벤트 데이터에서 사용자 영향 분포(전체 사용자 vs 특정 세그먼트)를 확인합니다

3. 에러 메시지(`metadata.value`)에서 유효성 검사 필드, 위반된 유효성 검사 규칙, 수신된 유효하지 않은 값을 포함한 유효성 검사 에러 상세 정보를 추출합니다.

4. 이슈 상세 정보의 릴리스 타임라인(firstRelease vs lastRelease)을 비교하여 이슈가 배포와 연관되는지 확인합니다.

5. 프로젝트 `<project-name>`의 유사 이슈를 조회하고 공통 릴리스 또는 배포 타임스탬프를 공유하는지 확인하여 광범위한 인시던트를 식별합니다.

## 진단

1. 이벤트 스택 트레이스 프레임(`entries[].data.values[].stacktrace.frames[]`)과 에러 메시지(`metadata.value`)에서 유효성 검사 에러 상세 정보를 분석하여 실패한 특정 유효성 검사 규칙, 필드 이름, 수신된 유효하지 않은 값을 식별합니다. 에러 메시지가 스키마 유효성 검사 실패(예: 필수 필드 누락, 타입 불일치)를 나타내면 업스트림 데이터 품질 문제일 가능성이 높습니다. 에러가 비즈니스 규칙 위반(예: 범위 초과 값)을 나타내면 사용자 입력 또는 유효성 검사 규칙 변경 문제일 수 있습니다.

2. 이벤트의 `firstSeen` 타임스탬프와 이슈 상세 정보의 `firstRelease` 배포 시간을 비교합니다. ValidationError가 릴리스 배포 후 30분 이내에 처음 나타났다면, 근본 원인은 릴리스에서 도입된 유효성 검사 규칙 변경, 새 필수 필드, 또는 더 엄격한 유효성 검사 로직일 가능성이 높습니다. 에러가 최근 릴리스 이전부터 존재했다면 데이터 소스 변경, 사용자 입력 패턴, 또는 서드파티 통합 변경을 조사합니다.

3. 이벤트 데이터에서 영향받는 사용자 분포와 이벤트 빈도를 검토합니다. 특정 타임스탬프 이후 모든 사용자에게 균일하게 유효성 검사 에러가 영향을 미치면 유효성 검사 규칙 또는 스키마 변경이 원인일 가능성이 높습니다. 에러가 특정 사용자 세그먼트에 집중되거나 특정 입력 소스와 연관되면 해당 특정 소스 또는 사용자 행동의 데이터 품질 문제와 관련됩니다.
