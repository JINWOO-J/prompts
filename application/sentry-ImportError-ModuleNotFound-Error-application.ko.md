---
category: incident-response
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/Sentry%20Playbooks/01-Error-Tracking/ImportError-ModuleNotFound-Error-application.md)'
role: SRE / Application Error Response
origin: scoutflo
extract_date: 2026-03-05
tags:
- application
- importerror
- k8s-deployment
- modulenotfound
- sentry
---

# ImportError-ModuleNotFound-Error-application — 모듈 미발견 에러

## 의미

모듈 임포트 에러가 발생합니다 (Sentry 에러 이슈 트리거, 예외 유형 ImportError). Python 모듈을 찾을 수 없어 사용 불가한 모듈을 임포트하려 할 때 애플리케이션 작업이 실패합니다. Sentry Issue Details 페이지에 "module not found", "import error", "no module named" 패턴의 에러 메시지가 표시되며, 스택 트레이스는 import 구문을 가리키고, 에러 레벨은 Error 또는 Fatal 심각도를 나타냅니다. 이는 애플리케이션 레이어에 영향을 미치며, 일반적으로 의존성 누락, 잘못된 모듈 경로, 또는 패키지 설치 실패로 인한 모듈 의존성 문제를 나타냅니다. 에러가 배포 문제와 연관되면 배포 로그에서 의존성 관리 문제가 확인될 수 있습니다.

## 영향

Sentry 에러 이슈 알림이 발생하고, 모듈 임포트 에러가 발생하며, 애플리케이션 작업이 실패합니다. 애플리케이션이 시작되지 않거나 실행에 실패합니다. 사용자에게 영향을 미치고, 이슈는 New 또는 Ongoing 상태로 유지됩니다. 애플리케이션 시작이 실패하고, 영향받는 사용자 수가 증가하며, 에러 카운트가 지속적으로 증가합니다. Sentry 대시보드에서 Medium 또는 High 우선순위로 표시되고, 애플리케이션 기능이 완전히 저하됩니다. 에러가 배포 문제와 연관되면 의존성 관리 문제가 배포 실패를 유발할 수 있습니다.

## 플레이북

1. 이슈 유형(`metadata.type`), 우선순위(`priority`), 영향받는 사용자 수(`userCount`), 에러 메시지(`metadata.value`)를 포함한 이슈 상세 정보를 확인하여 "module not found", "import error", "no module named" 패턴의 ImportError를 검증합니다.

2. 이슈 `<issue-id>`의 이벤트를 조회하고 이벤트 패턴을 분석합니다:
   - 최근 이벤트를 조회하여 스택 트레이스 프레임(`entries[].data.values[].stacktrace.frames[]`)을 검사하고 영향받는 import 구문과 누락된 모듈 이름을 식별합니다
   - 최근 24시간 동안의 이벤트 빈도(일정, 급증, 점진적 증가)를 분석하고 이벤트 데이터에서 사용자 영향 분포(전체 사용자 vs 특정 세그먼트)를 확인합니다

3. 에러 메시지(`metadata.value`)에서 "no module named [module_name]" 패턴과 일치하는 모듈 이름을 추출하여 누락된 Python 모듈과 자사 또는 서드파티 의존성 여부를 식별합니다.

4. 이슈 상세 정보의 릴리스 타임라인(firstRelease vs lastRelease)을 비교하여 이슈가 배포와 연관되는지 확인합니다.

5. 프로젝트 `<project-name>`의 유사 이슈를 조회하고 공통 릴리스 또는 배포 타임스탬프를 공유하는지 확인하여 광범위한 인시던트를 식별합니다.

## 진단

1. 최근 이벤트의 스택 트레이스 프레임(`entries[].data.values[].stacktrace.frames[]`)과 에러 메시지(`metadata.value`)에서 "no module named [module_name]" 패턴을 분석하여 누락된 모듈과 임포트 컨텍스트를 식별합니다. 누락된 모듈이 서드파티 패키지이면 의존성 누락 또는 비호환 문제일 가능성이 높습니다. 누락된 모듈이 자사 모듈이면 리팩토링 에러, 잘못된 모듈 경로, 또는 패키지 구조 파일 누락 문제일 가능성이 높습니다.

2. 이벤트의 `firstSeen` 타임스탬프와 이슈 상세 정보의 `firstRelease` 배포 시간을 비교합니다. ImportError가 릴리스 배포 후 30분 이내에 처음 나타났다면, 근본 원인은 requirements.txt 항목 누락, 불완전한 Docker 이미지 빌드, 또는 배포 중 패키지 설치 실패와 같은 배포 설정 문제일 가능성이 높습니다. 에러가 최근 릴리스 이전부터 존재했다면 환경별 문제, Python 경로 설정, 또는 조건부 임포트 실패를 조사합니다.

3. 이벤트 데이터에서 이벤트 빈도 패턴과 영향받는 배포 환경을 검토합니다. 특정 타임스탬프 이후 모든 인스턴스에서 일관되게 에러가 발생하면 배포 또는 의존성 설정 변경이 원인일 가능성이 높습니다. 에러가 간헐적이거나 특정 서버 인스턴스에만 영향을 미치면, 부분 배포, 환경별 패키지 설치 실패, 또는 레플리카 간 일관되지 않은 컨테이너 빌드와 연관됩니다.
