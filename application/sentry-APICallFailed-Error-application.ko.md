---
category: incident-response
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/Sentry%20Playbooks/01-Error-Tracking/APICallFailed-Error-application.md)'
role: SRE / Application Error Response
origin: scoutflo
extract_date: 2026-03-05
tags:
- apicallfailed
- application
- k8s-service
- sentry
---

# APICallFailed-Error-application — API 호출 실패 에러

## 의미

외부 API 호출 실패가 발생합니다 (Sentry 에러 이슈 트리거). 외부 API 요청이 실패하여 외부 서비스와 통신 시 API 작업이 중단됩니다. Sentry Issue Details 페이지에 "API call failed", "HTTP error", "request failed" 패턴의 에러 메시지가 표시되며, 스택 트레이스는 API 클라이언트 레이어를 가리키고, 에러 레벨은 Error 또는 Fatal 심각도를 나타냅니다. 이는 외부 API 통합 레이어에 영향을 미치며, 일반적으로 외부 서비스 장애, HTTP 에러, 또는 API 클라이언트 설정 문제로 인한 API 통합 이슈를 나타냅니다.

## 영향

Sentry 에러 이슈 알림이 발생하고, 외부 API 호출이 실패하며, API 작업이 중단됩니다. 애플리케이션이 API 에러를 반환하고 사용자에게 영향을 미칩니다. 이슈는 New 또는 Ongoing 상태로 유지되며, 에러 레벨은 Error 또는 Fatal 심각도를 표시합니다. 스택 트레이스는 API 호출 실패를 나타내고, Sentry Issue Details 페이지에 에러 이벤트가 표시됩니다. 외부 API 통합이 중단되고, 영향받는 사용자 수가 증가하며, 에러 카운트가 지속적으로 증가합니다. Sentry 대시보드에서 High 또는 Medium 우선순위로 표시되고, 애플리케이션 기능이 저하되며 기능 장애가 발생합니다.

## 플레이북

1. 이슈 유형(`metadata.type`), 우선순위(`priority`), 영향받는 사용자 수(`userCount`), 에러 메시지(`metadata.value`)를 포함한 이슈 상세 정보를 확인하여 "API call failed", "HTTP error", "request failed" 패턴의 API 호출 실패를 검증합니다.

2. 이슈 `<issue-id>`의 이벤트를 조회하고 이벤트 패턴을 분석합니다:
   - 최근 이벤트를 조회하여 스택 트레이스 프레임(`entries[].data.values[].stacktrace.frames[]`)을 검사하고 영향받는 API 클라이언트 파일을 식별합니다
   - 최근 24시간 동안의 이벤트 빈도(일정, 급증, 점진적 증가)를 분석하고 이벤트 데이터에서 사용자 영향 분포(전체 사용자 vs 특정 세그먼트)를 확인합니다

3. 에러 메시지(`metadata.value`) 또는 스택 트레이스 컨텍스트에서 API URL과 HTTP 상태 코드를 포함한 API 엔드포인트 상세 정보를 추출하여 대상 외부 API 서비스와 실패 유형을 식별합니다.

4. 이슈 상세 정보의 릴리스 타임라인(firstRelease vs lastRelease)을 비교하여 이슈가 배포와 연관되는지 확인합니다.

5. `firstRelease.lastCommit`이 존재하면 `firstRelease.versionInfo.package`에서 리포지토리 이름을 추출하거나 서비스 매핑을 사용한 후, GitHub 커밋 상세 정보를 조회하고 커밋이 PR에 포함되어 있는지 확인합니다. PR이 발견되면 PR diff를 조회하여 API 통합 또는 설정 변경 사항을 분석합니다.

6. 에러 타임스탬프 전후의 ELK 로그를 검색합니다:
   - 전체 요청 상세 정보와 응답 코드를 보여주는 API 요청/응답 로그
   - 외부 서비스 연결 에러 또는 타임아웃
   - 서킷 브레이커 상태 변경(open/closed/half-open) — 구현된 경우
   - 외부 API의 속도 제한 또는 스로틀링 로그
   - DNS 해석 또는 네트워크 연결 문제

7. 프로젝트 `<project-name>`의 유사 이슈를 조회하고 공통 릴리스 또는 배포 타임스탬프를 공유하는지 확인하여 광범위한 인시던트를 식별합니다.

8. 이슈 `<issue-id>`의 태그를 조회하여 환경, 외부 API 엔드포인트, HTTP 상태 코드, 타임아웃 기간 등 API 실패에 대한 인사이트를 제공할 수 있는 추가 컨텍스트를 확인합니다.

## 진단

1. 플레이북 2단계의 에러 이벤트 패턴을 분석하여 에러 추세를 식별합니다. 이벤트가 배포와 연관된 급격한 급증을 보이면 배포 관련 API 통합 변경을 나타냅니다. 에러가 일정하면 지속적인 외부 서비스 장애 또는 설정 오류를 나타냅니다. 에러가 간헐적이면 외부 서비스 불안정 또는 네트워크 연결 변동을 나타냅니다.

2. 에러 급증이 배포와 연관되면(플레이북 4단계 릴리스 타임라인), `firstRelease` 타임스탬프와 에러 발생 시점을 비교하여 배포가 트리거인지 확인합니다. `firstRelease`와 `lastRelease`가 다르면 API 실패가 초기 릴리스에서 시작되었는지 후속 릴리스에서 증가했는지 분석합니다.

3. `firstRelease.lastCommit`이 존재하고 이벤트가 코드 관련 이슈를 나타내면(플레이북 5단계), GitHub 커밋 변경 사항을 분석하여 실패를 유발하는 특정 API 엔드포인트 변경, 인증 수정, 또는 요청 페이로드 변경을 식별합니다.

4. Sentry 이벤트 데이터에서 HTTP 상태 코드를 추출하고(플레이북 3단계) 패턴을 분석합니다. 4xx 에러이면 클라이언트 측 문제(인증, 요청 형식)일 가능성이 높습니다. 5xx 에러이면 외부 서비스 문제일 가능성이 높습니다. 혼합 코드이면 설정과 외부 서비스 문제의 조합일 가능성이 높습니다.

5. 이벤트가 인프라 의존성 문제(연결 에러, 속도 제한 — 플레이북 6단계)를 나타내면, Sentry 이벤트의 에러 타임스탬프 전후의 ELK 로그에서 연관된 외부 서비스 장애, 서킷 브레이커 활성화, 또는 네트워크 문제를 검색합니다.

6. 명확한 배포 또는 인프라 연관성이 없으면, 플레이북 2단계 이벤트 데이터에서 영향받는 사용자 패턴을 분석합니다. 모든 사용자가 영향받으면 외부 서비스 다운 또는 API 설정 문제일 가능성이 높습니다. 특정 세그먼트가 영향받으면 특정 API 엔드포인트 실패 또는 특정 사용자의 인증 문제일 가능성이 높습니다.

7. 유사 이슈가 존재하고(플레이북 7단계) 공유된 릴리스 타임스탬프가 있으면, 여러 서비스에 걸쳐 API 통합에 영향을 미치는 광범위한 배포 인시던트를 나타냅니다.
