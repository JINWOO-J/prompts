# Tasks

## Requirement 1: shared/ 범용 개발 에이전트 정리

- [x] Task 1: shared/ 전체 파일 감사 — 17개 파일을 "인프라/보안 운영 관련", "범용 개발 에이전트", "재분류 필요"로 분류하고 결과를 문서화한다
  - **AC:** `req-1.ac-1`
  - **Files:** `shared/*.md`
  - **Approach:** 각 파일의 내용과 역할을 확인하여 인프라/보안 운영 목적 부합 여부 판단. backend-developer, fullstack-developer, frontend-developer 등이 주요 검토 대상

- [x] Task 2: 범용 개발 에이전트 파일에 `scope: general-dev` 태그 추가 — Task 1에서 "범용 개발 에이전트"로 분류된 파일의 Frontmatter에 scope 태그 추가
  - **AC:** `req-1.ac-2`
  - **Files:** Task 1 분류 결과에 따라 결정

- [x] Task 3: 재분류 필요 파일 이동 — Task 1에서 "재분류 필요"로 분류된 파일을 적절한 카테고리 폴더로 이동하고 Frontmatter category 갱신
  - **AC:** `req-1.ac-3`
  - **Files:** Task 1 분류 결과에 따라 결정

- [x] Task 4: Requirement 1 인덱스 재생성 — `python3 scripts/rebuild-index.py` 실행하여 shared/ 정리 결과가 prompts.meta.yaml과 web/data.json에 반영되는지 확인
  - **AC:** `req-1.ac-4`

## Requirement 2: 13-Proactive K8s 플레이북 추출

- [x] Task 5: 13-Proactive 원본 소스 구조 확인 — `.tmp-sources/Scoutflo-SRE-Playbooks/K8s Playbooks/13-Proactive/` 하위 7개 카테고리와 파일 수 확인
  - **AC:** `req-2.ac-1`
  - **Files:** `.tmp-sources/Scoutflo-SRE-Playbooks/K8s Playbooks/13-Proactive/`

- [x] Task 6: 추출 스크립트 작성 및 실행 — 56개 파일을 `infrastructure/` 폴더로 추출. 파일명을 `k8s-13-Proactive-{하위카테고리}-{장애명}.md` 규칙으로 변환하고 표준 Frontmatter(`origin: scoutflo`, `category: infrastructure`) 추가
  - **AC:** `req-2.ac-1`, `req-2.ac-2`, `req-2.ac-3`
  - **Files:** `scripts/extract_k8s_proactive.py` (신규), `infrastructure/k8s-13-Proactive-*.md` (생성)

- [x] Task 7: README.md infrastructure 섹션 업데이트 — `k8s-13-Proactive-*.md` 패턴 항목 추가 및 통계 갱신
  - **AC:** `req-2.ac-5`
  - **Files:** `README.md`

- [x] Task 8: Requirement 2 인덱스 재생성 — 추출된 Proactive 플레이북 포함하여 인덱스 정상 재생성 확인
  - **AC:** `req-2.ac-4`

## Requirement 3: 태그 품질 보강

- [x] Task 9: `--audit-tags` 옵션 구현 — rebuild-index.py에 태그 1개 이하 파일 목록 출력 기능 추가. 현재 태그 수, 파일 경로, 제안 태그 포함 리포트 출력
  - **AC:** `req-3.ac-1`, `req-3.ac-2`, `req-3.ac-5`
  - **Files:** `scripts/rebuild-index.py`

- [x] Task 10: 태그 1개 파일 73개에 Frontmatter 태그 보강 — `--audit-tags` 리포트 기반으로 각 파일에 최소 3개 이상 태그를 Frontmatter에 직접 명시
  - **AC:** `req-3.ac-3`, `req-3.ac-4`
  - **Files:** 73개 대상 파일 (audit 결과에 따라 결정)
  - **Approach:** 파일명, 내용, 카테고리를 분석하여 적절한 태그 자동 생성 스크립트 작성 후 일괄 적용

- [x] Task 11: 태그 보강 결과 검증 — `--audit-tags` 재실행하여 태그 2개 이하 파일이 0개인지 확인
  - **AC:** `req-3.ac-5`

## Requirement 4: incident-response/ 오케스트레이터 파일 재분류

- [x] Task 12: 오케스트레이터 파일 5개를 shared/로 이동 — error-coordinator.md, it-ops-orchestrator.md, multi-agent-coordinator.md, task-distributor.md, workflow-orchestrator.md를 incident-response/ → shared/로 이동하고 Frontmatter category를 `shared`로 갱신
  - **AC:** `req-4.ac-1`, `req-4.ac-2`, `req-4.ac-3`
  - **Files:** `incident-response/{error-coordinator,it-ops-orchestrator,multi-agent-coordinator,task-distributor,workflow-orchestrator}.md` → `shared/`

- [x] Task 13: README.md shared 섹션 업데이트 — 이동된 오케스트레이터 파일 항목을 shared/ 테이블에 추가
  - **AC:** `req-4.ac-5`
  - **Files:** `README.md`

- [x] Task 14: Requirement 4 인덱스 재생성 — 파일 이동 후 인덱스 정상 재생성 확인
  - **AC:** `req-4.ac-4`

## Requirement 5: 웹 뷰어 UX 개선

- [x] Task 15: 태그 필터 UI 구현 — 프롬프트 목록 상단에 태그 기반 필터 드롭다운/칩 UI 추가. 선택한 태그를 포함하는 프롬프트만 표시
  - **AC:** `req-5.ac-1`
  - **Files:** `web/app.js`, `web/index.html`

- [x] Task 16: origin 필터 UI 구현 — custom, scoutflo, voltagent, shawnewallace 기반 필터 UI 추가
  - **AC:** `req-5.ac-2`
  - **Files:** `web/app.js`, `web/index.html`

- [x] Task 17: 복합 필터 AND 결합 로직 — 카테고리 + 태그 + origin + 검색어를 AND로 결합하는 필터링 로직 구현. 매칭 프롬프트 수 실시간 표시
  - **AC:** `req-5.ac-3`, `req-5.ac-4`, `req-5.ac-5`
  - **Files:** `web/app.js`

- [x] Task 18: 태그 클릭 필터링 — 프롬프트 상세 뷰에서 태그 클릭 시 해당 태그로 필터링되도록 이벤트 핸들러 추가
  - **AC:** `req-5.ac-6`
  - **Files:** `web/app.js`

## Requirement 6: prompts.meta.yaml 스키마 검증

- [x] Task 19: validate-index.py 스크립트 작성 — 필수 필드 존재 여부, category/origin 허용값 검증, file 경로 실존 여부 검증. 실패 시 리포트 출력 + 종료 코드 1
  - **AC:** `req-6.ac-1`, `req-6.ac-2`, `req-6.ac-3`, `req-6.ac-4`, `req-6.ac-5`, `req-6.ac-6`
  - **Files:** `scripts/validate-index.py` (신규)

- [x] Task 20: 전체 검증 실행 — validate-index.py 실행하여 현재 인덱스의 일관성 확인 및 발견된 문제 수정
  - **AC:** `req-6.ac-5`
