---
category: incident-response
source: '[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/Sentry%20Playbooks/01-Error-Tracking/ProgrammingError-ColumnMissing-Database-Error-application.md)'
role: SRE / Application Error Response
origin: scoutflo
extract_date: 2026-03-05
tags:
- application
- columnmissing
- database
- postgres
- programmingerror
- sentry
---

# ProgrammingError-ColumnMissing-Database-Error-application — 데이터베이스 컬럼 누락 에러

## 의미

데이터베이스 프로그래밍 에러가 발생합니다 (Sentry 에러 이슈 트리거, 예외 유형 ProgrammingError). 데이터베이스 스키마 컬럼이 테이블에서 누락되어 존재하지 않는 컬럼에 접근하려 할 때 SQL 쿼리가 실패합니다. Sentry Issue Details 페이지에 "column does not exist" 패턴의 에러 메시지가 표시되며, 스택 트레이스는 데이터베이스 실행 레이어(sentry/db/postgres/base.py 등)를 가리키고, 에러 레벨은 Error 또는 Fatal 심각도를 나타냅니다. 이는 데이터베이스 레이어에 영향을 미치며, 일반적으로 마이그레이션 누락, 불완전한 스키마 업데이트, 또는 데이터베이스 동기화 실패로 인한 데이터베이스 스키마 문제를 나타냅니다.

## 영향

Sentry 에러 이슈 알림이 발생하고, 데이터베이스 쿼리가 실패하며, 애플리케이션이 데이터베이스 에러를 반환합니다. 사용자에게 영향을 미치고, 이슈는 New 또는 Ongoing 상태로 유지됩니다. 데이터베이스 작업이 실패하고, 영향받는 사용자 수가 증가하며, 에러 카운트가 지속적으로 증가합니다. Sentry 대시보드에서 High 우선순위로 표시되고, 애플리케이션 기능이 저하되며 데이터 접근 작업이 실패합니다.

## 플레이북

1. 이슈 유형(`metadata.type`), 우선순위(`priority`), 영향받는 사용자 수(`userCount`), 에러 메시지(`metadata.value`)를 포함한 이슈 상세 정보를 확인하여 "column does not exist" 패턴의 ProgrammingError를 검증합니다.

2. 이슈 `<issue-id>`의 이벤트를 조회하고 이벤트 패턴을 분석합니다:
   - 최근 이벤트를 조회하여 스택 트레이스 프레임(`entries[].data.values[].stacktrace.frames[]`)을 검사하고 영향받는 데이터베이스 파일을 식별합니다
   - 최근 24시간 동안의 이벤트 빈도(일정, 급증, 점진적 증가)를 분석하고 이벤트 데이터에서 사용자 영향 분포(전체 사용자 vs 특정 세그먼트)를 확인합니다

3. 에러 메시지(`metadata.value`)에서 "column [column_name] does not exist" 패턴과 일치하는 컬럼 이름과 스택 트레이스 또는 에러 컨텍스트에서 테이블 이름을 추출하여 누락된 데이터베이스 스키마 요소를 식별합니다.

4. 이슈 상세 정보의 릴리스 타임라인(firstRelease vs lastRelease)을 비교하여 이슈가 배포와 연관되는지 확인합니다.

5. `firstRelease.lastCommit`이 존재하면 `firstRelease.versionInfo.package`에서 리포지토리 이름을 추출하거나 서비스 매핑을 사용한 후, GitHub 커밋 상세 정보를 조회하고 커밋이 PR에 포함되어 있는지 확인합니다. PR이 발견되면 PR diff를 조회하여 데이터베이스 마이그레이션 또는 스키마 변경 사항을 분석합니다.

6. 에러 타임스탬프 전후의 ELK 로그를 검색합니다:
   - 데이터베이스 마이그레이션 실행 로그 ("migrate", "alembic", "flyway" 또는 사용 중인 마이그레이션 도구 검색)
   - 스키마 초기화 실패를 나타낼 수 있는 애플리케이션 시작 로그
   - 실패한 SQL 구문을 보여주는 데이터베이스 연결 또는 쿼리 로그
   - 불완전한 마이그레이션 실행을 보여줄 수 있는 배포 로그

7. 프로젝트 `<project-name>`의 유사 이슈를 조회하고 공통 릴리스 또는 배포 타임스탬프를 공유하는지 확인하여 광범위한 인시던트를 식별합니다.

8. 이슈 `<issue-id>`의 태그를 조회하여 환경, 배포, 데이터베이스 관련 태그 등 스키마 불일치에 대한 인사이트를 제공할 수 있는 추가 컨텍스트를 확인합니다.

## 진단

1. 플레이북 2단계의 에러 이벤트 패턴을 분석하여 에러 추세를 식별합니다. 이벤트가 배포와 연관된 급격한 급증을 보이면 해당 마이그레이션 없이 배포 관련 스키마 변경을 나타냅니다. 에러가 일정하면 지속적인 스키마 불일치를 나타냅니다. 에러가 간헐적이면 부분적 마이그레이션 롤아웃 또는 환경별 스키마 차이를 나타냅니다.

2. 에러 급증이 배포와 연관되면(플레이북 4단계 릴리스 타임라인), `firstRelease` 타임스탬프와 에러 발생 시점을 비교하여 배포가 트리거인지 확인합니다. `firstRelease`와 `lastRelease`가 다르면 스키마 에러가 초기 릴리스에서 시작되었는지 후속 릴리스에서 나타났는지 분석합니다.

3. `firstRelease.lastCommit`이 존재하고 이벤트가 코드 관련 이슈를 나타내면(플레이북 5단계), GitHub 커밋 변경 사항을 분석하여 해당 마이그레이션 파일 없이 누락된 컬럼을 참조하는 특정 데이터베이스 모델 변경, ORM 필드 추가, 또는 쿼리 수정을 식별합니다.

4. 스택 트레이스가 마이그레이션 관련 코드를 보여주거나 이벤트가 마이그레이션 타이밍 문제를 나타내면, Sentry 이벤트의 에러 타임스탬프 전후의 ELK 로그(플레이북 6단계)에서 연관된 마이그레이션 실행 로그, 마이그레이션 실패, 또는 데이터베이스 스키마 초기화 에러를 검색합니다.

5. 명확한 배포 연관성이 없으면, 플레이북 2단계 이벤트 데이터에서 영향받는 사용자 패턴을 분석합니다. 모든 사용자가 영향받으면 배포 파이프라인에서 마이그레이션이 누락되었을 가능성이 높습니다. 특정 세그먼트가 영향받으면 환경별 스키마 드리프트 또는 부분적 마이그레이션 실행일 가능성이 높습니다.

6. 유사 이슈가 존재하고(플레이북 7단계) 공유된 릴리스 타임스탬프가 있으면, 애플리케이션 코드 배포 전에 마이그레이션이 적용되지 않은 광범위한 배포 인시던트를 나타냅니다.
