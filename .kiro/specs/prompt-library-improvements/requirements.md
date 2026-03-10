# Requirements Document

## Introduction

인프라/보안 운영 프롬프트 라이브러리(375개 프롬프트)의 콘텐츠 품질, 분류 체계, 도구 지원을 개선하기 위한 요구사항 정의. 이전 분석에서 식별된 6개 개선 영역을 체계적으로 다룬다.

## Glossary

- **Library**: 인프라/보안 운영 프롬프트 라이브러리 전체 (prompts/ 루트)
- **Index_Builder**: `scripts/rebuild-index.py` 스크립트 — prompts.meta.yaml 및 web/data.json을 자동 생성하는 도구
- **Web_Viewer**: `web/` 폴더의 SPA 기반 프롬프트 검색/열람 웹 뷰어
- **Frontmatter**: 각 마크다운 파일 상단의 YAML 메타데이터 블록 (category, source, origin, tags 등)
- **Tag**: 프롬프트 파일에 부여된 검색용 키워드. Frontmatter의 tags 필드 또는 Index_Builder의 guess_tags()로 자동 생성
- **Proactive_Playbook**: Scoutflo 원본 소스의 13-Proactive 섹션에 포함된 사전 예방적 K8s 운영 플레이북 (56개 파일, 7개 하위 카테고리)
- **Orchestrator_Prompt**: 멀티 에이전트 조정, 작업 분배, 워크플로우 관리 등 범용 오케스트레이션 역할의 프롬프트 파일
- **Schema_Validator**: prompts.meta.yaml 인덱스 파일의 구조적 일관성을 검증하는 스크립트

## Requirements

### Requirement 1: shared/ 범용 개발 에이전트 정리

**User Story:** As a 운영팀원, I want shared/ 폴더의 프롬프트가 인프라/보안 운영 목적에 부합하도록 정리되기를, so that 라이브러리의 정체성이 일관되고 불필요한 프롬프트로 인한 혼란이 줄어든다.

#### Acceptance Criteria

1. THE Library SHALL 분류하여 shared/ 내 각 파일을 "인프라/보안 운영 관련", "범용 개발 에이전트", "재분류 필요" 중 하나로 태깅한 분류 결과를 문서화한다
2. WHEN 파일이 "범용 개발 에이전트"로 분류된 경우, THE Library SHALL 해당 파일의 Frontmatter에 `scope: general-dev` 태그를 추가하여 인프라/보안 운영 프롬프트와 구분한다
3. WHEN 파일이 "재분류 필요"로 분류된 경우, THE Library SHALL 해당 파일을 적절한 카테고리 폴더로 이동하고 Frontmatter의 category 필드를 갱신한다
4. THE Index_Builder SHALL shared/ 폴더 재정리 후 prompts.meta.yaml과 web/data.json을 정상적으로 재생성한다

### Requirement 2: 13-Proactive K8s 플레이북 추출

**User Story:** As a SRE 엔지니어, I want Scoutflo 원본의 13-Proactive 섹션 플레이북이 라이브러리에 통합되기를, so that 사전 예방적 K8s 운영 체크리스트를 활용할 수 있다.

#### Acceptance Criteria

1. THE Library SHALL `.tmp-sources/Scoutflo-SRE-Playbooks/K8s Playbooks/13-Proactive/` 하위 7개 카테고리(Capacity-Performance, Security-Compliance, Backup-DR, Cost-Optimization, Observability, Data-Integrity, Operational-Readiness)의 56개 파일을 `infrastructure/` 폴더로 추출한다
2. WHEN Proactive_Playbook 파일이 추출될 때, THE Library SHALL 파일명을 기존 네이밍 규칙(`k8s-13-Proactive-{하위카테고리}-{장애명}.md`)에 맞게 변환한다
3. WHEN Proactive_Playbook 파일이 추출될 때, THE Library SHALL 각 파일에 `origin: scoutflo`, `category: infrastructure` 를 포함하는 표준 Frontmatter를 추가한다
4. THE Index_Builder SHALL 추출된 Proactive_Playbook 파일을 포함하여 인덱스를 정상적으로 재생성한다
5. THE Library SHALL README.md의 infrastructure/ 섹션 테이블에 `k8s-13-Proactive-*.md` 패턴 항목을 추가한다

### Requirement 3: 태그 품질 보강

**User Story:** As a 운영팀원, I want 태그가 1개뿐인 73개 파일의 태그를 보강하기를, so that 웹 뷰어와 grep 기반 검색의 정확도가 향상된다.

#### Acceptance Criteria

1. THE Index_Builder SHALL 태그가 1개 이하인 파일 목록을 출력하는 `--audit-tags` 옵션을 제공한다
2. WHEN `--audit-tags` 옵션이 실행될 때, THE Index_Builder SHALL 각 파일의 현재 태그 수, 파일 경로, 제안 태그를 포함한 리포트를 출력한다
3. THE Library SHALL 태그가 1개뿐인 파일에 대해 최소 3개 이상의 태그를 Frontmatter에 직접 명시한다
4. WHEN Frontmatter에 tags 필드가 명시된 경우, THE Index_Builder SHALL guess_tags() 자동 추론 결과 대신 Frontmatter의 tags를 우선 사용한다
5. IF 태그 보강 후에도 태그가 2개 이하인 파일이 존재하면, THEN THE Index_Builder SHALL `--audit-tags` 실행 시 해당 파일을 경고로 표시한다

### Requirement 4: incident-response/ 오케스트레이터 파일 재분류

**User Story:** As a 운영팀원, I want 범용 오케스트레이터 성격의 파일이 적절한 폴더에 위치하기를, so that incident-response/는 실제 인시던트 대응 프롬프트만 포함하고 범용 조정 프롬프트는 shared/에서 찾을 수 있다.

#### Acceptance Criteria

1. THE Library SHALL incident-response/ 내 Orchestrator_Prompt 파일(error-coordinator.md, it-ops-orchestrator.md, multi-agent-coordinator.md, task-distributor.md, workflow-orchestrator.md)을 shared/ 폴더로 이동한다
2. WHEN Orchestrator_Prompt 파일이 이동될 때, THE Library SHALL 해당 파일의 Frontmatter category 필드를 `shared`로 갱신한다
3. THE Library SHALL 이동 후 incident-response/ 폴더에 동일 파일명이 남아있지 않음을 확인한다
4. THE Index_Builder SHALL 파일 이동 후 prompts.meta.yaml과 web/data.json을 정상적으로 재생성한다
5. THE Library SHALL README.md의 shared/ 섹션 테이블에 이동된 Orchestrator_Prompt 파일 항목을 추가한다

### Requirement 5: 웹 뷰어 UX 개선

**User Story:** As a 운영팀원, I want 웹 뷰어에서 태그 기반 필터링과 origin 필터를 사용할 수 있기를, so that 375개 이상의 프롬프트 중 원하는 것을 빠르게 찾을 수 있다.

#### Acceptance Criteria

1. THE Web_Viewer SHALL 프롬프트 목록 상단에 태그 기반 필터 UI를 제공하여 선택한 태그를 포함하는 프롬프트만 표시한다
2. THE Web_Viewer SHALL origin(custom, scoutflo, voltagent, shawnewallace) 기반 필터 UI를 제공하여 선택한 origin의 프롬프트만 표시한다
3. WHEN 태그 필터와 origin 필터가 동시에 적용될 때, THE Web_Viewer SHALL 두 조건을 AND로 결합하여 프롬프트를 필터링한다
4. WHEN 카테고리, 태그, origin 필터가 모두 적용된 상태에서 검색어가 입력될 때, THE Web_Viewer SHALL 모든 필터 조건과 검색어를 AND로 결합하여 결과를 표시한다
5. THE Web_Viewer SHALL 현재 필터 조건에 매칭되는 프롬프트 수를 실시간으로 표시한다
6. THE Web_Viewer SHALL 프롬프트 상세 뷰에서 태그를 클릭하면 해당 태그로 필터링되도록 한다

### Requirement 6: prompts.meta.yaml 스키마 검증

**User Story:** As a 기여자, I want 인덱스 파일의 구조적 일관성을 자동으로 검증할 수 있기를, so that 잘못된 메타데이터가 인덱스에 포함되는 것을 사전에 방지할 수 있다.

#### Acceptance Criteria

1. THE Schema_Validator SHALL prompts.meta.yaml의 각 엔트리에 필수 필드(id, file, title, category, origin, tags)가 존재하는지 검증한다
2. THE Schema_Validator SHALL category 필드 값이 허용된 카테고리 목록(rca, incident-response, application, infrastructure, security, data-ai, shared, techniques) 중 하나인지 검증한다
3. THE Schema_Validator SHALL origin 필드 값이 허용된 origin 목록(custom, scoutflo, voltagent, shawnewallace) 중 하나인지 검증한다
4. THE Schema_Validator SHALL file 필드가 가리키는 파일이 실제로 존재하는지 검증한다
5. IF 검증 실패 항목이 존재하면, THEN THE Schema_Validator SHALL 실패 사유와 해당 파일 경로를 포함한 리포트를 출력하고 종료 코드 1을 반환한다
6. THE Schema_Validator SHALL `scripts/validate-index.py` 경로에 독립 스크립트로 제공된다
