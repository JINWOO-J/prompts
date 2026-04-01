---
category: incident-response
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/Sentry%20Playbooks/01-Error-Tracking/ConsumerError-PartitionError-Kafka-Error-application.md)'
role: SRE / Application Error Response
origin: scoutflo
extract_date: 2026-03-05
tags:
- application
- consumererror
- k8s-service
- kafka
- partitionerror
- pipeline
- sentry
- sts
---

# ConsumerError-PartitionError-Kafka-Error-application — Kafka 파티션 에러

## 의미

Kafka 컨슈머 에러가 발생합니다 (Sentry 에러 이슈 트리거, 예외 유형 ConsumerError). Kafka 파티션 에러가 존재하여 사용 불가하거나 잘못 설정된 파티션에서 소비 시도 시 이벤트 처리 및 메시지 큐 작업이 실패합니다. Sentry Issue Details 페이지에 "partition", "partition error", "partition not found" 패턴의 에러 메시지가 표시되며, 스택 트레이스는 Kafka 컨슈머 레이어(sentry/utils/kafka.py 또는 sentry/consumers/synchronized.py)를 가리키고, 에러 레벨은 Error 또는 Fatal 심각도를 나타냅니다. 이는 메시지 큐 및 이벤트 처리 레이어에 영향을 미치며, 일반적으로 파티션 삭제, 파티션 리밸런싱, 또는 Kafka 브로커 설정 문제로 인한 Kafka 파티션 설정 문제를 나타냅니다.

## 영향

Sentry 에러 이슈 알림이 발생하고, Kafka 컨슈머 작업이 실패하며, 이벤트 처리가 중단됩니다. 메시지 큐 작업이 실패하고 사용자에게 영향을 미칩니다. 이벤트 처리 파이프라인이 중단되고, 다운스트림 서비스에 영향을 미칩니다. 영향받는 사용자 수가 증가하며, 에러 카운트가 지속적으로 증가합니다. Sentry 대시보드에서 High 우선순위로 표시되고, 애플리케이션 기능이 저하됩니다. Kafka 에러가 증가하고, 이벤트 백로그가 형성되며, 데이터 파이프라인 중단이 발생합니다.

## 플레이북

1. 이슈 유형(`metadata.type`), 우선순위(`priority`), 영향받는 사용자 수(`userCount`), 에러 메시지(`metadata.value`)를 포함한 이슈 상세 정보를 확인하여 "partition", "partition error", "partition not found" 패턴의 ConsumerError를 검증합니다.

2. 이슈 `<issue-id>`의 이벤트를 조회하고 이벤트 패턴을 분석합니다:
   - 최근 이벤트를 조회하여 스택 트레이스 프레임(`entries[].data.values[].stacktrace.frames[]`)을 검사하고 영향받는 Kafka 컨슈머 파일을 식별합니다
   - 최근 24시간 동안의 이벤트 빈도(일정, 급증, 점진적 증가)를 분석하고 이벤트 데이터에서 사용자 영향 분포(전체 사용자 vs 특정 세그먼트)를 확인합니다

3. 에러 메시지(`metadata.value`)에서 토픽 이름과 파티션 번호를 포함한 Kafka 파티션 상세 정보를 추출하여 영향받는 파티션을 식별합니다.

4. 이슈 상세 정보의 릴리스 타임라인(firstRelease vs lastRelease)을 비교하여 이슈가 배포와 연관되는지 확인합니다.

5. `firstRelease.lastCommit`이 존재하면 `firstRelease.versionInfo.package`에서 리포지토리 이름을 추출하거나 서비스 매핑을 사용한 후, GitHub 커밋 상세 정보를 조회하고 커밋이 PR에 포함되어 있는지 확인합니다. PR이 발견되면 PR diff를 조회하여 Kafka 파티션 설정 변경 사항을 분석합니다.

6. Sentry의 에러 컨텍스트가 불충분하면, 에러 타임스탬프 전후의 서비스 ELK 로그를 검색하여 Kafka 컨슈머 로그, 파티션 할당 에러, 브로커 연결 문제를 식별합니다.

7. 프로젝트 `<project-name>`의 유사 이슈를 조회하고 공통 릴리스 또는 배포 타임스탬프를 공유하는지 확인하여 광범위한 인시던트를 식별합니다.

8. 이슈 `<issue-id>`의 태그를 조회하여 환경, 배포, Kafka 관련 태그 등 파티션 문제에 대한 인사이트를 제공할 수 있는 추가 컨텍스트를 확인합니다.

## 진단

1. 플레이북 2단계의 에러 이벤트 패턴을 분석하여 에러 추세를 식별합니다. 이벤트가 배포와 연관된 급격한 급증을 보이면 배포 관련 파티션 설정 변경을 나타냅니다. 에러가 일정하면 지속적인 파티션 누락 또는 삭제를 나타냅니다. 에러가 간헐적이면 파티션 리밸런싱 또는 브로커 가용성 문제를 나타냅니다.

2. 에러 급증이 배포와 연관되면(플레이북 4단계 릴리스 타임라인), `firstRelease` 타임스탬프와 에러 발생 시점을 비교하여 배포가 트리거인지 확인합니다. `firstRelease`와 `lastRelease`가 다르면 파티션 에러가 초기 릴리스에서 시작되었는지 후속 릴리스에서 나타났는지 분석합니다.

3. `firstRelease.lastCommit`이 존재하고 이벤트가 코드 관련 이슈를 나타내면(플레이북 5단계), GitHub 커밋 변경 사항을 분석하여 에러를 유발하는 특정 Kafka 파티션 설정 변경, 토픽 구독 수정, 또는 컨슈머 그룹 할당 변경을 식별합니다.

4. 이벤트가 인프라 의존성 문제(파티션 미발견, 브로커 사용 불가 — 플레이북 3단계)를 나타내면, Sentry 이벤트의 에러 타임스탬프 전후의 ELK 로그(플레이북 6단계)에서 연관된 Kafka 파티션 삭제 이벤트, 파티션 리밸런싱 작업, 또는 브로커 설정 변경을 검색합니다.

5. 명확한 배포 또는 인프라 연관성이 없으면, 플레이북 2단계 이벤트 데이터에서 영향받는 사용자 패턴을 분석합니다. 모든 사용자가 영향받으면 클러스터 전체 파티션 문제일 가능성이 높습니다. 특정 세그먼트가 영향받으면 컨슈머 그룹 또는 파티션 할당 설정 문제일 가능성이 높습니다.

6. 유사 이슈가 존재하고(플레이북 7단계) 공유된 릴리스 타임스탬프가 있으면, 여러 서비스에 걸쳐 Kafka 파티션 설정에 영향을 미치는 광범위한 배포 인시던트를 나타냅니다.
