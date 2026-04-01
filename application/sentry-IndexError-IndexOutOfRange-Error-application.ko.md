---
category: incident-response
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/Sentry%20Playbooks/01-Error-Tracking/IndexError-IndexOutOfRange-Error-application.md)'
role: SRE / Application Error Response
origin: scoutflo
extract_date: 2026-03-05
tags:
- application
- indexerror
- indexoutofrange
- sentry
- sts
---

# IndexError-IndexOutOfRange-Error-application — 인덱스 범위 초과 에러

## 의미

인덱스 범위 초과 에러가 발생합니다 (Sentry 에러 이슈 트리거, 예외 유형 IndexError). 애플리케이션이 유효하지 않은 인덱스로 리스트 또는 배열 요소에 접근하려 하여, 인덱스가 리스트 또는 배열 범위를 초과할 때 애플리케이션 작업이 실패합니다. Sentry Issue Details 페이지에 "index error", "index out of range" 패턴의 에러 메시지가 표시되며, 스택 트레이스는 애플리케이션 코드 레이어를 가리키고, 에러 레벨은 Error 또는 Warning 심각도를 나타냅니다. 이는 애플리케이션 레이어에 영향을 미치며, 일반적으로 유효하지 않은 인덱스 값, 빈 리스트, 또는 인덱스 계산 에러로 인한 배열 인덱싱 문제를 나타냅니다. 에러가 데이터 변경과 연관되면 데이터 수정 이력에서 배열 크기 문제가 확인될 수 있습니다.

## 영향

Sentry 에러 이슈 알림이 발생하고, 인덱스 범위 초과 에러가 발생하며, 애플리케이션 작업이 실패합니다. 애플리케이션이 인덱스 에러를 반환하고 사용자에게 영향을 미칩니다. 배열 인덱스 접근이 실패하고, 영향받는 사용자 수가 증가하며, 에러 카운트가 지속적으로 증가합니다. Sentry 대시보드에서 Medium 또는 Low 우선순위로 표시되고, 애플리케이션 기능이 저하됩니다.

## 플레이북

1. 이슈 유형(`metadata.type`), 우선순위(`priority`), 영향받는 사용자 수(`userCount`), 에러 메시지(`metadata.value`)를 포함한 이슈 상세 정보를 확인하여 "index error" 또는 "index out of range" 패턴의 IndexError를 검증합니다.

2. 이슈 `<issue-id>`의 이벤트를 조회하고 이벤트 패턴을 분석합니다:
   - 최근 이벤트를 조회하여 스택 트레이스 프레임(`entries[].data.values[].stacktrace.frames[]`)을 검사하고 영향받는 애플리케이션 파일과 인덱스 접근 위치를 식별합니다
   - 최근 24시간 동안의 이벤트 빈도(일정, 급증, 점진적 증가)를 분석하고 이벤트 데이터에서 사용자 영향 분포(전체 사용자 vs 특정 세그먼트)를 확인합니다

3. 에러 메시지(`metadata.value`) 또는 스택 트레이스 컨텍스트에서 인덱스 값을 추출하여 유효하지 않은 배열 인덱스와 예상 vs 실제 배열 크기를 식별합니다.

4. 이슈 상세 정보의 릴리스 타임라인(firstRelease vs lastRelease)을 비교하여 이슈가 배포와 연관되는지 확인합니다.

5. 프로젝트 `<project-name>`의 유사 이슈를 조회하고 공통 릴리스 또는 배포 타임스탬프를 공유하는지 확인하여 광범위한 인시던트를 식별합니다.

## 진단

1. 최근 이벤트의 스택 트레이스 프레임(`entries[].data.values[].stacktrace.frames[]`)과 에러 메시지(`metadata.value`)를 분석하여 정확한 코드 위치, 시도된 인덱스 값, 접근 대상 리스트 또는 배열을 식별합니다. 스택 트레이스가 외부 API 응답이나 데이터베이스 쿼리 결과의 요소 접근에서 에러가 발생함을 보여주면 예상치 못한 빈 컬렉션이나 짧은 컬렉션으로 인한 데이터 의존적 문제일 가능성이 높습니다. 스택 트레이스가 하드코딩된 인덱스 접근을 보여주면 코드 가정 에러일 가능성이 높습니다.

2. 이벤트의 `firstSeen` 타임스탬프와 이슈 상세 정보의 `firstRelease` 배포 시간을 비교합니다. IndexError가 릴리스 배포 후 30분 이내에 처음 나타났다면, 근본 원인은 잘못된 인덱스 계산을 도입하거나, 예상 배열 구조를 변경하거나, 경계 검사를 제거한 코드 변경일 가능성이 높습니다. 에러가 최근 릴리스 이전부터 존재했다면 데이터 소스 변경이나 컬렉션 크기에 영향을 미치는 업스트림 수정을 조사합니다.

3. 이벤트 데이터에서 이벤트 빈도 패턴과 영향받는 데이터 컨텍스트를 검토합니다. 특정 타임스탬프 이후 모든 사용자에서 일관되게 에러가 발생하면 코드 또는 설정 변경이 원인일 가능성이 높습니다. 에러가 간헐적이고 특정 데이터 패턴과 연관되면, 빈 결과 집합, 더 높은 인덱스로 접근하는 단일 요소 컬렉션, 또는 코드가 고정 크기 배열을 가정하는 가변 길이 데이터와 같은 엣지 케이스와 관련됩니다.
