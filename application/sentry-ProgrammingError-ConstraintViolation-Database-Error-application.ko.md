---
category: incident-response
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/Sentry%20Playbooks/01-Error-Tracking/ProgrammingError-ConstraintViolation-Database-Error-application.md)'
role: SRE / Application Error Response
origin: scoutflo
extract_date: 2026-03-05
tags:
- application
- constraintviolation
- database
- postgres
- programmingerror
- sentry
- sts
---

# ProgrammingError-ConstraintViolation-Database-Error-application — 데이터베이스 제약 조건 위반 에러

## 의미

데이터베이스 프로그래밍 에러가 발생합니다 (Sentry 에러 이슈 트리거, 예외 유형 ProgrammingError). 데이터베이스 제약 조건 위반이 존재하여 외래 키, 유니크 제약 조건, 체크 제약 조건 등의 데이터베이스 제약 조건을 위반하는 데이터를 삽입하거나 업데이트하려 할 때 SQL 작업이 실패합니다. Sentry Issue Details 페이지에 "constraint violation", "foreign key", "unique constraint" 패턴의 에러 메시지가 표시되며, 스택 트레이스는 데이터베이스 실행 레이어(sentry/db/postgres/base.py 등)를 가리키고, 에러 레벨은 Error 또는 Fatal 심각도를 나타냅니다. 이는 데이터베이스 레이어에 영향을 미치며, 일반적으로 유효하지 않은 데이터 관계, 중복 키 위반, 또는 제약 조건 적용 실패로 인한 데이터 무결성 문제를 나타냅니다.

## 영향

Sentry 에러 이슈 알림이 발생하고, 데이터베이스 작업이 실패하며, 데이터 무결성 위반이 발생합니다. 사용자에게 영향을 미치고, 이슈는 New 또는 Ongoing 상태로 유지됩니다. 데이터베이스 쓰기 작업이 실패하고, 영향받는 사용자 수가 증가하며, 에러 카운트가 지속적으로 증가합니다. Sentry 대시보드에서 High 우선순위로 표시되고, 애플리케이션 기능이 저하되며 데이터 일관성 문제가 발생합니다.

## 플레이북

1. 이슈 유형(`metadata.type`), 우선순위(`priority`), 영향받는 사용자 수(`userCount`), 에러 메시지(`metadata.value`)를 포함한 이슈 상세 정보를 확인하여 "constraint violation", "foreign key", "unique constraint" 패턴의 ProgrammingError를 검증합니다.

2. 이슈 `<issue-id>`의 이벤트를 조회하고 이벤트 패턴을 분석합니다:
   - 최근 이벤트를 조회하여 스택 트레이스 프레임(`entries[].data.values[].stacktrace.frames[]`)을 검사하고 영향받는 데이터베이스 파일을 식별합니다
   - 최근 24시간 동안의 이벤트 빈도(일정, 급증, 점진적 증가)를 분석하고 이벤트 데이터에서 사용자 영향 분포(전체 사용자 vs 특정 세그먼트)를 확인합니다

3. 에러 메시지(`metadata.value`)에서 제약 조건 이름, 테이블 이름, 제약 조건 유형(외래 키, 유니크, 체크)을 포함한 제약 조건 상세 정보를 추출하여 위반된 데이터베이스 제약 조건을 식별합니다.

4. 이슈 상세 정보의 릴리스 타임라인(firstRelease vs lastRelease)을 비교하여 이슈가 배포와 연관되는지 확인합니다.

5. `firstRelease.lastCommit`이 존재하면 `firstRelease.versionInfo.package`에서 리포지토리 이름을 추출하거나 서비스 매핑을 사용한 후, GitHub 커밋 상세 정보를 조회하고 커밋이 PR에 포함되어 있는지 확인합니다. PR이 발견되면 PR diff를 조회하여 데이터베이스 제약 조건 또는 데이터 모델 변경 사항을 분석합니다.

6. 에러 타임스탬프 전후의 ELK 로그를 검색합니다:
   - 데이터베이스 제약 조건 수정 로그 ("ALTER TABLE", "ADD CONSTRAINT" 또는 DDL 작업 검색)
   - 위반 데이터를 도입했을 수 있는 배치 임포트 또는 데이터 마이그레이션 로그
   - 제약 조건 위반을 유발한 데이터 값을 보여주는 애플리케이션 로그
   - 데이터가 외부 소스에서 오는 경우 데이터베이스 복제 또는 동기화 로그

7. 프로젝트 `<project-name>`의 유사 이슈를 조회하고 공통 릴리스 또는 배포 타임스탬프를 공유하는지 확인하여 광범위한 인시던트를 식별합니다.

8. 이슈 `<issue-id>`의 태그를 조회하여 환경, 배포, 데이터베이스 관련 태그 등 제약 조건 위반에 대한 인사이트를 제공할 수 있는 추가 컨텍스트를 확인합니다.

## 진단

1. 플레이북 2단계의 에러 이벤트 패턴을 분석하여 에러 추세를 식별합니다. 이벤트가 배포와 연관된 급격한 급증을 보이면 기존 제약 조건을 위반하는 배포 관련 코드 변경을 나타냅니다. 에러가 일정하면 애플리케이션 로직의 지속적인 데이터 무결성 문제를 나타냅니다. 에러가 간헐적이면 제약 조건 위반을 유발하는 특정 사용자 데이터 또는 입력 패턴을 나타냅니다.

2. 에러 급증이 배포와 연관되면(플레이북 4단계 릴리스 타임라인), `firstRelease` 타임스탬프와 에러 발생 시점을 비교하여 배포가 트리거인지 확인합니다. `firstRelease`와 `lastRelease`가 다르면 제약 조건 에러가 초기 릴리스에서 시작되었는지 후속 릴리스에서 나타났는지 분석합니다.

3. `firstRelease.lastCommit`이 존재하고 이벤트가 코드 관련 이슈를 나타내면(플레이북 5단계), GitHub 커밋 변경 사항을 분석하여 위반을 유발하는 특정 데이터 모델 변경, 삽입/업데이트 로직 수정, 또는 제약 조건 추가를 식별합니다.

4. 스택 트레이스가 배치 임포트 또는 데이터 마이그레이션 코드를 보여주거나 이벤트가 외부 데이터 소스 문제를 나타내면, Sentry 이벤트의 에러 타임스탬프 전후의 ELK 로그(플레이북 6단계)에서 연관된 배치 임포트 로그, 데이터 마이그레이션 실행, 또는 외부 데이터 동기화 작업을 검색합니다.

5. 명확한 배포 연관성이 없으면, 플레이북 2단계 이벤트 데이터에서 영향받는 사용자 패턴을 분석합니다. 모든 사용자가 영향받으면 데이터 유효성 검사의 애플리케이션 로직 문제일 가능성이 높습니다. 특정 세그먼트가 영향받으면 제약 조건 위반을 유발하는 특정 데이터 패턴 또는 사용자 입력일 가능성이 높습니다.

6. 유사 이슈가 존재하고(플레이북 7단계) 공유된 릴리스 타임스탬프가 있으면, 데이터 정리 없이 새 제약 조건이 추가되었거나 적절한 데이터 유효성 검사 없이 코드가 배포된 광범위한 배포 인시던트를 나타냅니다.
