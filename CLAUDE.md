# CLAUDE.md

## 프로젝트 개요

Prompt Library — SRE/DevOps 프롬프트 라이브러리. FastAPI 백엔드 + vanilla JS 프론트엔드 + GitHub Pages 정적 배포.

## 기술 스택

- Backend: Python 3.13, FastAPI, aiosqlite, uvicorn
- Frontend: Vanilla HTML/CSS/JS (빌드 스텝 없음)
- DB: SQLite (prompts.db)
- 배포: Docker Compose (self-hosted) / GitHub Pages (static)

## 핵심 명령어

```bash
make dev          # 개발 서버 (uvicorn --reload)
make dev-reset    # rebuild-index + DB 초기화 + 개발 서버
make test         # pytest 실행
make lint         # ruff 린트
make fmt          # ruff 포맷
```

## 디렉토리 구조

```
rca/              # Root Cause Analysis 프롬프트
incident-response/  # 인시던트 대응 런북
application/      # 애플리케이션 에러 진단
infrastructure/   # 인프라 트러블슈팅
security/         # 보안 프롬프트
data-ai/          # 데이터/AI 운영
shared/           # 공통 가드레일, 역할 정의
techniques/       # 프롬프트 기법 (CoT, ReAct 등)
coding/           # AI 코딩 에이전트 규칙
backend/          # FastAPI 서버
web/              # 프론트엔드 SPA
scripts/          # 빌드/유틸 스크립트
```

---

## 프롬프트 파일 규칙

### 파일 명명

```
{name}.ko.md     # 국문 버전 (주 파일)
{name}.en.md     # 영문 버전 (번역본)
{name}.md        # 단일 언어 (레거시, 점진적으로 .ko.md/.en.md로 전환)
```

- rebuild-index.py가 `.ko.md`와 `.en.md`를 하나의 entry로 묶음
- `.ko.md`가 primary (제목, 태그, 메타데이터 기준)
- `.en.md`가 없으면 KO만 표시

### Frontmatter 필수 필드

```yaml
---
category: coding          # 카테고리 (디렉토리명과 일치)
type: prompt              # prompt | concept | guide
tags:                     # 3-5개, kebab-case
- agent
- claude-md
role: Developer           # 대상 역할
origin: custom            # custom | scoutflo | voltagent | extracted
source: 'https://...'     # 출처 URL (없으면 빈 문자열)
---
```

### Type별 파일 구조

**type: prompt** (LLM에 직접 사용하는 지시문)
```markdown
# 제목 — 부제

> 한줄 설명과 출처.

---

## Prompt

```markdown
(영문 또는 국문 프롬프트 — 복사해서 바로 사용 가능)
```

---

## 사용법
## 적용 확인
```

**type: concept** (개념/철학 — LLM에 넣지 않음)
```markdown
# 제목

> 한줄 설명.

---

## 핵심 원칙
(요약 bullet list)

## 상세
(교육 내용)

## 참고
```

**type: guide** (개념 + 실행 혼합)
```markdown
# 제목

> 한줄 설명.

---

## Prompt

```markdown
(액션 가능한 템플릿/체크리스트)
```

---

## 배경
## 사용법
```

### 태그 규칙

- `coding`, `ai-agent` 같은 범용 태그 금지 (카테고리와 중복)
- `agent` 태그: 에이전트 설계/행동에 관한 파일에만
- 파일당 3-5개, 의미 있는 필터링이 가능한 것만
- kebab-case, 단수형 (`rule` not `rules`)
- 명명 패턴 태그 허용 (`karpathy-rules`, `riper-5`)

### 번역 규칙

- 제목: 원어 유지 + 번역 병기
- 기술 용어 원어 유지 (K8s, RBAC, CoT 등)
- XML 태그 구조 유지 (`<Role>`, `<Task>`)
- 프롬프트 본문은 자연스러운 목표 언어 (직역 금지)
- 코드 블록 내 주석만 번역, 코드 자체 유지
- 섹션 헤딩 매핑:
  - KO→EN: 개요→Overview, 사용법→Usage, 적용 확인→Verification, 핵심 원칙→Key Principles, 상세→Details, 참고→References, 배경→Background
  - EN→KO: 역방향

### 번역 불필요 파일

- `type: concept` — 국문 교육 자료, 영문 불필요
- `type: guide` — 국문만으로 충분한 경우 영문 생략 가능
