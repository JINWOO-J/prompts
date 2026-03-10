# Tasks: Prompt Management App

## Task 1: 데이터베이스 레이어 구축

- [x] 1.1 `backend/database.py` 생성: SQLite 연결 관리, `init_db()` 함수 (prompts + versions 테이블 생성, FK 활성화, 인덱스)
- [x] 1.2 `backend/models.py` 생성: Pydantic 모델 (PromptCreate, PromptUpdate, PromptResponse, PromptListItem, PromptListResponse, VersionResponse, ExportSummary, ErrorResponse)
- [x] 1.3 DB 초기화 단위 테스트: 테이블 존재 확인, FK 제약 조건 검증 (Req 1.1, 1.2, 1.3)

## Task 2: 마이그레이션 스크립트

- [x] 2.1 `backend/migrate.py` 생성: .md 파일 스캔, YAML frontmatter 파싱, DB 삽입, 중복 스킵, 요약 출력
- [x] 2.2 마이그레이션 단위 테스트: frontmatter 파싱, 중복 처리, 요약 정합성 (Req 2.1~2.5)
- [x] 2.3 [PBT] Property 1 테스트: 마이그레이션 라운드트립 — 랜덤 .md 파일 import → export → 원본 비교 (Req 2.6)
- [x] 2.4 [PBT] Property 9 테스트: 마이그레이션 요약 정합성 — scanned == imported + skipped (Req 2.5)

## Task 3: REST API — 프롬프트 CRUD

- [x] 3.1 `backend/services/prompt_service.py` 생성: list, get, create, update, delete 비즈니스 로직
- [x] 3.2 `backend/routers/prompts.py` 생성: CRUD 엔드포인트 + 페이지네이션/필터 쿼리 파라미터
- [x] 3.3 `backend/main.py` 생성: FastAPI 앱 엔트리포인트, 라우터 등록, startup 이벤트에서 init_db 호출
- [x] 3.4 CRUD 단위 테스트: 생성/조회/수정/삭제 기본 흐름, 404/422 에러 응답 (Req 3.1~3.10)
- [x] 3.5 [PBT] Property 2 테스트: CRUD 라운드트립 — 랜덤 프롬프트 POST → GET → 필드 비교 (Req 3.5, 3.6)
- [x] 3.6 [PBT] Property 3 테스트: 검색 필터 정확성 — 랜덤 데이터 + 필터 → 결과 검증 (Req 3.2, 3.3, 3.4)
- [x] 3.7 [PBT] Property 4 테스트: 페이지네이션 일관성 — 전체 페이지 순회 → ID 집합 비교 (Req 3.1)
- [x] 3.8 [PBT] Property 8 테스트: 유효하지 않은 요청 거부 — 랜덤 비존재 ID → 404, 빈 필드 → 422 (Req 3.9, 3.10)

## Task 4: 버전 히스토리 API

- [x] 4.1 `backend/services/version_service.py` 생성: create_version, list_versions, get_version, restore_version
- [x] 4.2 `backend/routers/versions.py` 생성: 버전 목록/조회/복원 엔드포인트
- [x] 4.3 버전 관리 단위 테스트: 업데이트 시 버전 생성, 버전 목록 정렬, 복원 동작 (Req 4.1~4.6)
- [x] 4.4 [PBT] Property 5 테스트: 업데이트 시 버전 자동 생성 — 랜덤 업데이트 → 버전 확인 (Req 3.7, 4.1, 4.2)
- [x] 4.5 [PBT] Property 6 테스트: 버전 복원 라운드트립 — 랜덤 버전 복원 → 내용 비교 (Req 4.4, 4.5)
- [x] 4.6 [PBT] Property 7 테스트: 삭제 연쇄 제거 — 버전 있는 프롬프트 삭제 → DB 확인 (Req 3.8)

## Task 5: 익스포트/동기화 API

- [x] 5.1 `backend/services/export_service.py` 생성: export_all_to_md, sync_meta_files, format_prompt_as_md, parse_md_file
- [x] 5.2 `backend/routers/export.py` 생성: /api/export, /api/export/sync 엔드포인트
- [x] 5.3 익스포트 단위 테스트: .md 파일 생성, meta.yaml/data.json 재생성 확인 (Req 5.1~5.5)
- [x] 5.4 [PBT] Property 12 테스트: 익스포트 파일 경로 정확성 — 랜덤 카테고리 → 경로 확인 (Req 5.3)

## Task 6: 프론트엔드 — API 연동 및 목록/필터링

- [x] 6.1 `web/app.js` 수정: data.json 대신 /api/prompts API 호출로 전환, 기존 필터링 로직 유지
- [x] 6.2 `web/index.html` 수정: "새 프롬프트", "편집", "삭제" 버튼 추가, 편집 폼 마크업 추가
- [x] 6.3 `web/styles.css` 수정: 편집 폼, 에디터, 버전 히스토리 패널 스타일 추가

## Task 7: 프론트엔드 — 마크다운 에디터

- [x] 7.1 `web/editor.js` 생성: CodeMirror 6 초기화, 마크다운 구문 강조, 실시간 미리보기 (200ms 디바운스)
- [x] 7.2 에디터를 편집 폼에 통합: 생성/편집 모드에서 CodeMirror 에디터 + 미리보기 패널 렌더링

## Task 8: 프론트엔드 — CRUD 연동

- [x] 8.1 생성 기능: "새 프롬프트" 폼 → POST /api/prompts → 목록 갱신
- [x] 8.2 편집 기능: "편집" 버튼 → 에디터 모드 전환 → PUT /api/prompts/{id} → 뷰어 갱신
- [x] 8.3 삭제 기능: "삭제" 버튼 → 확인 다이얼로그 → DELETE /api/prompts/{id} → 목록에서 제거
- [x] 8.4 에러 처리: API 에러 시 토스트 알림, 422 에러 시 폼 필드 옆 에러 메시지 표시

## Task 9: 프론트엔드 — 버전 히스토리 UI

- [x] 9.1 `web/versions.js` 생성: 버전 목록 로드, 버전 내용 표시, 복원 기능
- [x] 9.2 버전 히스토리 패널을 뷰어에 통합: "히스토리" 버튼 → 버전 목록 패널 → 버전 선택/복원

## Task 10: 통합 및 마무리

- [x] 10.1 `web/index.html`에 CodeMirror CDN 스크립트 추가, editor.js/versions.js 로드
- [x] 10.2 FastAPI 앱에서 `web/` 디렉토리를 정적 파일로 서빙 설정
- [x] 10.3 전체 통합 테스트: 마이그레이션 → API CRUD → 버전 관리 → 익스포트 → 동기화 흐름 검증
