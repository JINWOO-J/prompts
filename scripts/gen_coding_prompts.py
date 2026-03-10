#!/usr/bin/env python3
"""coding 카테고리 프롬프트 생성 스크립트.

AI 코딩 에이전트 행동 규칙, CLAUDE.md/AGENTS.md 패턴,
코딩 방법론 등을 프롬프트로 생성한다.
"""

from pathlib import Path

OUT = Path(__file__).parent.parent / "coding"
OUT.mkdir(exist_ok=True)

PROMPTS: list[dict] = []


def add(slug: str, tags: list[str], role: str, title: str, body: str):
    PROMPTS.append({
        "slug": slug,
        "tags": tags,
        "role": role,
        "title": title,
        "body": body,
    })


def write_all():
    for p in PROMPTS:
        tag_yaml = "\n".join(f"- {t}" for t in p["tags"])
        content = f"""---
category: coding
tags:
{tag_yaml}
role: {p['role']}
origin: custom
source: ''
---
# {p['title']}

{p['body']}"""
        (OUT / f"{p['slug']}.md").write_text(content, encoding="utf-8")
    print(f"✅ {len(PROMPTS)}개 coding 프롬프트 생성 → {OUT}/")


# ─────────────────────────────────────────────
# 1. Karpathy Rules — AI 코딩 에이전트 4원칙
# ─────────────────────────────────────────────
add("karpathy-rules", ["coding", "ai-agent", "rules", "claude-md", "best-practices"],
    "Developer", "Karpathy Rules — AI 코딩 에이전트 4원칙",
    """## 개요

Andrej Karpathy가 제안한 AI 코딩 에이전트(Claude Code 등)의 행동 가이드라인.
LLM이 코딩할 때 흔히 저지르는 실수를 줄이기 위한 4가지 핵심 원칙이다.
신중함을 속도보다 우선시하는 방향으로 설계되었다.

> 출처: [forrestchang/andrej-karpathy-skills](https://github.com/forrestchang/andrej-karpathy-skills/blob/main/CLAUDE.md)

## 4가지 원칙

### 1. Think Before Coding — 코딩 전에 생각하라

**가정하지 마라. 혼란을 숨기지 마라. 트레이드오프를 드러내라.**

- 가정을 명시적으로 진술하라. 불확실하면 물어라
- 여러 해석이 가능하면 제시하라 — 조용히 하나를 고르지 마라
- 더 단순한 접근이 있으면 말하라. 필요하면 반박하라
- 불명확하면 멈춰라. 무엇이 혼란스러운지 이름 붙여라

### 2. Simplicity First — 단순함 우선

**문제를 해결하는 최소한의 코드. 추측성 코드 금지.**

- 요청받지 않은 기능 추가 금지
- 한 번만 쓰이는 코드에 추상화 금지
- 요청되지 않은 "유연성"이나 "설정 가능성" 금지
- 불가능한 시나리오에 대한 에러 핸들링 금지
- 200줄로 쓴 것이 50줄로 가능하면 다시 써라

> 자문: "시니어 엔지니어가 이걸 보고 과도하게 복잡하다고 할까?" 그렇다면 단순화하라.

### 3. Surgical Changes — 외과적 변경

**건드려야 할 것만 건드려라. 자기가 만든 쓰레기만 치워라.**

기존 코드 편집 시:
- 인접 코드, 주석, 포매팅을 "개선"하지 마라
- 고장나지 않은 것을 리팩터링하지 마라
- 기존 스타일에 맞춰라, 다르게 하고 싶더라도
- 관련 없는 데드 코드를 발견하면 언급만 하라 — 삭제하지 마라

자기 변경이 고아(orphan)를 만들면:
- 자기 변경으로 미사용된 import/변수/함수는 제거하라
- 기존에 있던 데드 코드는 요청 없이 제거하지 마라

> 테스트: 변경된 모든 줄이 사용자 요청에 직접 연결되어야 한다.

### 4. Goal-Driven Execution — 목표 기반 실행

**성공 기준을 정의하라. 검증될 때까지 반복하라.**

작업을 검증 가능한 목표로 변환:
- "유효성 검사 추가" → "잘못된 입력에 대한 테스트 작성, 통과시키기"
- "버그 수정" → "재현 테스트 작성, 통과시키기"
- "X 리팩터링" → "전후로 테스트 통과 확인"

다단계 작업은 간단한 계획을 진술:
```
1. [단계] → 검증: [확인사항]
2. [단계] → 검증: [확인사항]
3. [단계] → 검증: [확인사항]
```

## 적용 확인

이 가이드라인이 작동하고 있다면:
- diff에 불필요한 변경이 줄어든다
- 과도한 복잡성으로 인한 재작성이 줄어든다
- 명확화 질문이 실수 후가 아닌 구현 전에 나온다
""")


# ─────────────────────────────────────────────
# 2. Inevitable Code — 필연적 코드 철학
# ─────────────────────────────────────────────
add("inevitable-code", ["coding", "typescript", "design", "simplicity", "ai-agent"],
    "Developer", "Inevitable Code — 필연적 코드 철학",
    """## 개요

Giselle AI 팀의 ts-coder 에이전트가 따르는 코딩 철학.
"모든 설계 선택이 유일하게 합리적인 옵션처럼 느껴지는 코드"를 작성하는 원칙이다.
개발자가 코드를 만났을 때 "당연히 이렇게 되어야지. 다른 방법이 있겠어?"라고 느끼게 만드는 것이 목표.

> 출처: [giselles-ai/giselle ts-coder agent](https://github.com/giselles-ai/giselle/blob/main/.claude/agents/ts-coder.md)

## 핵심 원리: 표면적 단순함, 내부적 정교함

단순한 인터페이스가 정교한 구현을 숨길 수 있다.
외부 인지 부하를 제거하기 위해 내부 복잡성을 기꺼이 수용한다.

```typescript
// 필연적: 직접적이고 명백함
const user = await getUser(id);
if (!user) return null;

// 과도한 설계: 불필요한 추상화 레이어
const userService = createUserService(dependencies);
const result = await userService.getUser(id);
if (!result.success) handleError(result.error);
```

## 설계 원칙

### 1. 결정 지점 최소화
사용자에게 강제하는 모든 API 선택은 인지 부하를 만든다.
JavaScript의 자연스러운 패턴을 활용하여 결정을 줄여라.

### 2. 목적 뒤에 복잡성 숨기기
내부 복잡성은 수용 가능하다 — 다른 곳의 복잡성을 제거할 때.
복잡성을 한 곳에 집중시켜 다른 곳을 단순하게 만들어라.

### 3. 회상이 아닌 인식을 위한 설계
기존 멘탈 모델을 활용하는 패턴과 이름을 선택하라.
임의의 규칙을 암기하지 않고도 코드가 무엇을 하는지 인식할 수 있어야 한다.

### 4. 클래스보다 함수, 상속보다 합성
클래스는 상태 관리, 생명주기, 상속 계층을 통해 우발적 복잡성을 도입한다.
함수는 자연스럽게 합성된다.

### 5. 에러를 감지 가능하게가 아니라 불가능하게 만들어라
TypeScript의 타입 시스템을 사용하여 명백한 실수를 방지하되, 의식(ceremony)을 만들지 마라.

## 안티패턴 제거 목록

- **과도한 추상화**: 단순한 함수로 충분할 때 복잡한 패턴 생성
- **설정 폭발**: 좋은 기본값으로 결정할 수 있는 것을 사용자에게 떠넘기기
- **타입 의식**: 단순한 타입으로 충분히 소통할 때 복잡한 타입 사용
- **조기 일반화**: 필요한 것을 알기 전에 추상화 구축
- **서비스 레이어**: 실제 문제를 해결하지 않는 간접 참조 추가

## 리트머스 테스트

코드를 내보내기 전에 자문:
1. 이것이 가능한 한 단순한가?
2. 자연스럽게 느껴지는가?
3. 실제 문제를 해결하고 있는가?
4. 깨졌을 때 무슨 일이 일어나는가?
""")


# ─────────────────────────────────────────────
# 3. Cognitive Readability First — 인지 가독성 우선
# ─────────────────────────────────────────────
add("cognitive-readability", ["coding", "readability", "cognitive-load", "clean-code", "ai-agent"],
    "Developer", "Cognitive Readability First — 인지 가독성 우선 코딩",
    """## 개요

규칙 준수가 아닌 **인간의 이해**를 최적화하는 코딩 원칙.
함수/블록에서 동시에 추적해야 하는 개념 수를 3~4개 이하로 유지하고,
단계별 분석(System 2)이 아닌 패턴 인식(System 1)으로 읽히는 코드를 지향한다.

## 핵심 원칙

- 함수/블록의 동시 추적 개념을 **약 3~4개 이하**로 유지 (데이터/상태, 규칙, 분기 축, 부수효과)
- **패턴 인식(System 1)**으로 읽히는 코드 선호, 단계별 분석(System 2) 아님
- 이름과 구조가 **다음 동작을 예측 가능**하게 만들어야 함
- 문제 자체의 복잡성은 수용 가능. **표현으로 인한 복잡성은 불가**

## 실천 규칙 10가지

### 1. 활성 컨텍스트 최소화
- 흐름이 한눈에 명확하지 않을 때 분리
- 독립적으로 테스트/재사용 가능할 때 분리
- 매우 작은(≈3줄) 단순 로직은 인라인 유지
- "4개 컨텍스트 초과"라고 기계적으로 분리하지 마라

### 2. 점프 비용 경계
- 이해에 함수/파일 간 2회 이상 점프가 필요하면 분리를 재고
- 호출 지점에서 동작을 예측할 수 없으면 재고
- **컨텍스트 감소가 탐색 비용을 초과할 때만** 분리

### 3. 관용적 패턴 선호
- 언어, 프레임워크, 팀 규칙을 따르라
- 영리한 트릭, 이중 부정, 불필요한 추상화 회피

### 4. 선형 흐름 유지
- 가드 절과 조기 반환 선호
- 메인 로직은 위에서 아래로 읽혀야 함

### 5. 이름 = 동작
- 이름은 코드가 실제로 하는 것과 일치해야 함
- 부수효과(DB, 네트워크, 이벤트, 캐시 등)가 이름이나 구조에서 보여야 함

### 6. 시각적 구조
- 관련 로직을 빈 줄로 그룹화
- 유사한 책임을 유사한 형태로 유지

### 7. 지역성
- 핵심 흐름이 단일 파일, 가능하면 단일 화면에서 읽혀야 함
- 헬퍼를 사용처 가까이에 배치

### 8. 대칭성
- 쌍을 이루는 연산(parse/serialize, encode/decode, CRUD 등)의 이름, 시그니처, 에러 처리를 대칭적으로 유지

### 9. 숨겨진 정책 금지
- 전역 변수, 환경 플래그, 싱글톤 뒤에 결정 로직을 숨기지 마라
- 매개변수나 명시적 정책 객체를 통해 정책을 노출

### 10. 예외를 구조적으로 만들어라
- 중요한 예외 규칙은 타입, 결과 객체, 전용 함수로 표현 — 주석만으로는 부족

## 하지 말 것

- 기계적으로 함수 분리
- 작은 일회용 헬퍼 추출
- 기존 팀 규칙 위반
- 메트릭 감소만을 위한 리팩터링
""")


# ─────────────────────────────────────────────
# 4. CLAUDE.md 작성 가이드
# ─────────────────────────────────────────────
add("claude-md-guide", ["coding", "claude-md", "agents-md", "context-engineering", "ai-agent"],
    "Developer", "CLAUDE.md / AGENTS.md 작성 가이드",
    """## 개요

AI 코딩 에이전트에게 프로젝트 컨텍스트를 전달하는 CLAUDE.md(또는 AGENTS.md) 파일 작성법.
매 세션마다 반복 설명 없이 에이전트가 프로젝트를 이해하도록 하는 핵심 설정 파일이다.

> 참고: [humanlayer.dev/blog/writing-a-good-claude-md](https://www.humanlayer.dev/blog/writing-a-good-claude-md),
> [josix/awesome-claude-md](https://github.com/josix/awesome-claude-md)

## 핵심 원칙

### 1. 컨텍스트 윈도우는 공유 자원
CLAUDE.md는 시스템 프롬프트, 대화 이력, 기타 컨텍스트와 경쟁한다.
간결하고 핵심적인 정보만 포함하라.

### 2. 포함해야 할 것
- **빌드/테스트 명령어**: `npm run test`, `make lint` 등 정확한 명령어
- **아키텍처 개요**: 디렉토리 구조, 주요 모듈 관계
- **코딩 규칙**: 네이밍, 에러 처리, 로깅 패턴
- **금지 사항**: "sed 사용 금지", "기존 테스트 삭제 금지" 등
- **의존성 정보**: 패키지 매니저, 런타임 버전

### 3. 포함하지 말 것
- 코드 스타일/포매팅 규칙 (linter/formatter에 위임)
- 너무 긴 설명 (500줄 이상은 효과 감소)
- 자주 변하는 정보 (별도 파일로 분리)

## 구조 템플릿

```markdown
# CLAUDE.md

## 프로젝트 개요
[한 문단으로 프로젝트 설명]

## 빌드 & 테스트
- 설치: `pnpm install`
- 테스트: `pnpm test`
- 린트: `pnpm lint`

## 아키텍처
- `src/` — 메인 소스
- `tests/` — 테스트
- `docs/` — 문서

## 코딩 규칙
- [규칙 1]
- [규칙 2]

## 금지 사항
- [금지 1]
- [금지 2]
```

## 5계층 설정 시스템

| 계층 | 파일 | 용도 |
|------|------|------|
| 1 | CLAUDE.md | 프로젝트 컨텍스트 (매 세션 로드) |
| 2 | .claude/settings.json | 도구 권한, 허용 명령어 |
| 3 | .claude/hooks/ | 이벤트 기반 자동화 |
| 4 | .claude/agents/ | 서브에이전트 정의 |
| 5 | .claude/memory/ | 자동 메모리 |

## Progressive Disclosure 패턴

큰 프로젝트에서는 계층적으로 CLAUDE.md를 배치:
- 루트 `CLAUDE.md` — 전체 프로젝트 규칙
- `packages/api/CLAUDE.md` — API 패키지 규칙
- `packages/web/CLAUDE.md` — 웹 패키지 규칙

에이전트가 특정 디렉토리에서 작업할 때 해당 레벨의 규칙이 추가 로드된다.
""")


# ─────────────────────────────────────────────
# 5. Context Engineering — 컨텍스트 엔지니어링
# ─────────────────────────────────────────────
add("context-engineering", ["coding", "context-engineering", "ai-agent", "prompt-engineering", "llm"],
    "Developer", "Context Engineering — AI 코딩 에이전트 컨텍스트 엔지니어링",
    """## 개요

2025년 Andrej Karpathy가 "vibe coding"을 제안한 이후, 업계는 "AI 제안을 그냥 수락"에서
**컨텍스트 엔지니어링**이라는 체계적 접근으로 전환했다.
AI 코딩 에이전트에게 올바른 컨텍스트를 제공하여 출력 품질을 극대화하는 기법이다.

> 참고: [pixelmojo.io — Context Engineering for AI Coding Agents](https://www.pixelmojo.io/blogs/context-engineering-ai-coding-agents-beyond-claude-md)

## 핵심 개념

### 컨텍스트 = 에이전트의 전부
모델은 현재 토큰 스트림에 있는 것만 안다.
CLAUDE.md는 보통 매 세션에 자동 주입되는 유일한 파일이다.

### 컨텍스트의 4가지 레이어

| 레이어 | 설명 | 예시 |
|--------|------|------|
| 시스템 | 에이전트 기본 동작 | 시스템 프롬프트 |
| 프로젝트 | 코드베이스 규칙 | CLAUDE.md, AGENTS.md |
| 세션 | 현재 대화 | 대화 이력, 파일 읽기 |
| 작업 | 현재 태스크 | 사용자 프롬프트 |

### 효과적인 컨텍스트 전략

1. **구체적 명령어 > 일반적 조언**: "pnpm test" > "테스트를 실행하세요"
2. **예시 > 설명**: 코드 예시가 규칙 설명보다 효과적
3. **금지 > 권장**: "sed 사용 금지"가 "sd를 사용하세요"보다 강력
4. **구조 > 산문**: 표, 목록, 코드 블록이 긴 문장보다 효과적

## 실전 패턴

### 4-파일 워킹 메모리 시스템
```
PRD.md          — 제품 요구사항
CLAUDE.md       — 프로젝트 규칙
planning.md     — 아키텍처 결정
tasks.md        — 작업 추적
```

### @import 패턴
CLAUDE.md에서 다른 파일을 참조:
```markdown
See @docs/architecture.md for system design
See @docs/api-spec.yaml for API contracts
```

### 토큰 예산 관리
- CLAUDE.md는 200~500줄이 최적
- 자주 변하는 정보는 별도 파일로 분리
- 서브디렉토리별 CLAUDE.md로 점진적 공개
""")


# ─────────────────────────────────────────────
# 6. Spec-Driven Development — 스펙 기반 개발
# ─────────────────────────────────────────────
add("spec-driven-development", ["coding", "spec-driven", "tdd", "ai-agent", "methodology"],
    "Developer", "Spec-Driven Development — AI 에이전트 스펙 기반 개발",
    """## 개요

AI 에이전트가 "지시를 권장사항으로 취급"하는 경향을 기술적으로 강제하는 방법론.
스펙 문서를 먼저 작성하고, 에이전트가 스펙에 따라 TDD 사이클로 구현하도록 한다.

> 참고: [smartscope.blog — Enforcing Spec-Driven on AI Agents](http://smartscope.blog/en/ai-development/enforcing-spec-driven-development-claude-copilot-2025/)

## 워크플로우

```
1. 스펙 작성 (requirements.md)
2. 설계 문서 작성 (design.md)
3. 태스크 분해 (tasks.md)
4. 각 태스크마다:
   a. 테스트 먼저 작성
   b. 테스트 실패 확인
   c. 최소 구현 코드 작성
   d. 테스트 통과 확인
   e. 태스크 완료 마킹
```

## 핵심 원칙

### 1. 구현 전에 스펙
- 코드를 쓰기 전에 무엇을 만들지 명확히 정의
- 요구사항 → 설계 → 태스크 순서를 강제

### 2. 한 번에 하나의 작은 변경
- 작은 테스트, 작은 구현
- 리팩터링은 모든 테스트 통과 후에만

### 3. 검증 가능한 완료 기준
- 각 태스크에 명확한 성공 기준
- 자동화된 테스트로 검증

### 4. 에이전트 행동 강제
- 스펙 파일을 에이전트 컨텍스트에 항상 포함
- "스펙에 없는 기능 추가 금지" 규칙 명시

## 스펙 파일 구조

### requirements.md
```markdown
## Requirement 1: [기능명]
### User Stories
- As a [역할], I want [기능] so that [이유]
### Acceptance Criteria
- [ ] [검증 가능한 기준 1]
- [ ] [검증 가능한 기준 2]
```

### tasks.md
```markdown
## Task 1: [태스크명]
- [ ] 1.1 [서브태스크] (Req 1.1)
- [ ] 1.2 [서브태스크] (Req 1.2)
```
""")


# ─────────────────────────────────────────────
# 7. Vibe Coding Playbook — 바이브 코딩 가이드
# ─────────────────────────────────────────────
add("vibe-coding-playbook", ["coding", "vibe-coding", "ai-agent", "methodology", "karpathy"],
    "Developer", "Vibe Coding Playbook — 바이브 코딩 실전 가이드",
    """## 개요

2025년 2월 Andrej Karpathy가 제안한 "vibe coding" 개념의 실전 가이드.
AI에게 결과물을 맡기되, 프롬프트·테스트·가드레일로 품질을 확보하는 방법론이다.

> 참고: [royfactory.net — Vibe Coding Playbook](https://royfactory.net/posts/ai/202512/vibe-coding-playbook/)

## 바이브 코딩이란?

"바이브에 몸을 맡기고, 지수적 성장을 받아들이고, 코드가 작동하는지조차 잊어버리는" 접근.
하지만 실제 프로덕션에서는 가드레일이 필수다.

## 실전 원칙

### 1. 프롬프트가 곧 설계
- 명확하고 구체적인 프롬프트 = 좋은 설계 문서
- 모호한 프롬프트 → 모호한 코드

### 2. 테스트가 곧 스펙
- AI가 생성한 코드의 정확성은 테스트로만 검증 가능
- 테스트 먼저 작성하고 AI에게 구현을 맡겨라

### 3. 가드레일 설정
- CLAUDE.md/AGENTS.md로 행동 규칙 정의
- 린터, 포매터, 타입 체커로 자동 검증
- CI/CD 파이프라인으로 배포 전 검증

### 4. 점진적 복잡성
- 작은 것부터 시작하여 점진적으로 확장
- 한 번에 큰 변경보다 여러 번의 작은 변경

### 5. 컨텍스트 관리
- 세션이 길어지면 컨텍스트 품질이 저하됨
- 주기적으로 새 세션 시작
- 중요한 결정은 파일로 기록

## 워크플로우

```
1. 의도 명확화 (프롬프트 작성)
2. 테스트 작성 (성공 기준 정의)
3. AI에게 구현 위임
4. 테스트 실행 (자동 검증)
5. 코드 리뷰 (수동 검증)
6. 반복
```

## 주의사항

- AI 출력을 무조건 신뢰하지 마라
- 보안 관련 코드는 반드시 수동 리뷰
- 복잡한 비즈니스 로직은 단계별로 검증
- 성능 크리티컬 코드는 벤치마크 필수
""")


# ─────────────────────────────────────────────
# 8. RIPER-5 — AI 개발 방법론
# ─────────────────────────────────────────────
add("riper-5-methodology", ["coding", "riper-5", "methodology", "ai-agent", "workflow"],
    "Developer", "RIPER-5 — AI 에이전트 개발 방법론",
    """## 개요

GoMall 프로젝트에서 사용된 AI 에이전트 개발 방법론.
Research → Implement → Plan → Execute → Review 5단계 사이클로
AI 에이전트의 작업을 구조화한다.

> 출처: [josix/awesome-claude-md — GoMall](https://github.com/josix/awesome-claude-md/blob/main/scenarios/developer-tooling/li0on3_GoMall/README.md)

## 5단계 사이클

### R — Research (조사)
- 기존 코드베이스 분석
- 관련 파일과 의존성 파악
- 기존 패턴과 규칙 이해
- **출력**: 현재 상태 요약

### I — Implement (구현 계획)
- 변경 사항의 영향 범위 분석
- 가능한 접근 방식 비교
- 트레이드오프 명시
- **출력**: 구현 방향 제안

### P — Plan (계획)
- 구체적인 단계별 실행 계획
- 각 단계의 검증 방법 정의
- 의존성 순서 결정
- **출력**: 번호가 매겨진 실행 계획

### E — Execute (실행)
- 계획에 따라 코드 변경
- 각 단계 후 검증
- 문제 발생 시 계획 수정
- **출력**: 변경된 코드

### R — Review (검토)
- 변경 사항 전체 검토
- 테스트 실행 및 확인
- 의도하지 않은 부수효과 확인
- **출력**: 검토 결과 및 개선 제안

## 적용 방법

에이전트에게 현재 단계를 명시적으로 지시:
```
현재 RIPER 단계: Research
[프로젝트]의 인증 모듈을 분석하고 현재 상태를 요약해줘.
```

## 장점

- 에이전트가 "바로 코딩"하는 것을 방지
- 각 단계에서 사용자 확인 가능
- 변경의 영향 범위를 사전에 파악
- 체계적인 검증 프로세스
""")


# ─────────────────────────────────────────────
# 9. 4-File Working Memory — 4파일 워킹 메모리
# ─────────────────────────────────────────────
add("four-file-memory", ["coding", "working-memory", "ai-agent", "session-management", "claude-code"],
    "Developer", "4-File Working Memory — AI 에이전트 워킹 메모리 시스템",
    """## 개요

AI 코딩 에이전트의 세션 간 기억 상실 문제를 해결하는 4파일 프레임워크.
PRD, CLAUDE.md, planning.md, tasks.md 4개 파일로 프로젝트 컨텍스트를 영속화한다.

> 참고: [implicator.ai — Four-File System for Claude Code](https://www.implicator.ai/this-simple-four-file-system-gives-claude-code-a-working-memory/)

## 문제

AI 코딩 에이전트는 세션 간 기억이 없다:
- 매 세션마다 프로젝트 아키텍처를 다시 설명
- 이미 존재하는 파일을 다시 생성
- 완료된 작업을 반복, 새 작업은 누락
- 일관성 없는 결정

## 4파일 구조

### 1. PRD.md — 제품 요구사항
```markdown
# Product Requirements Document
## 목표
[프로젝트의 핵심 목표]
## 기능 목록
- [기능 1]: [설명]
- [기능 2]: [설명]
## 기술 스택
- Backend: [기술]
- Frontend: [기술]
```

### 2. CLAUDE.md — 프로젝트 규칙
```markdown
# Project Rules
## 빌드 명령어
## 코딩 규칙
## 금지 사항
```

### 3. planning.md — 아키텍처 결정
```markdown
# Architecture Decisions
## 결정 1: [제목]
- 선택: [선택한 옵션]
- 이유: [근거]
- 대안: [고려한 대안]
```

### 4. tasks.md — 작업 추적
```markdown
# Tasks
## 완료
- [x] [작업 1]
## 진행 중
- [ ] [작업 2]
## 대기
- [ ] [작업 3]
```

## 세션 시작 프롬프트

```
이 프로젝트의 PRD.md, CLAUDE.md, planning.md, tasks.md를 읽고
현재 상태를 파악한 후, 다음 작업을 진행해줘.
```

## 효과

- 프로젝트 관리 시간 70% 감소
- 컨텍스트 전환 비용 최소화
- 일관된 아키텍처 결정
- 작업 중복/누락 방지
""")


# ─────────────────────────────────────────────
# 10. Agent Behavior Patterns — 에이전트 행동 패턴
# ─────────────────────────────────────────────
add("agent-behavior-patterns", ["coding", "ai-agent", "behavior", "agents-md", "patterns"],
    "Developer", "Agent Behavior Patterns — 실제로 에이전트 행동을 바꾸는 패턴",
    """## 개요

AGENTS.md/CLAUDE.md에서 실제로 AI 에이전트의 행동을 변화시키는 패턴과
효과가 없는 패턴을 구분하는 실증적 가이드.

> 참고: [blakecrosley.com — What Actually Changes Agent Behavior](https://blakecrosley.com/blog/agents-md-patterns),
> [dair.ai — Does AGENTS.md Actually Help?](https://academy.dair.ai/blog/agents-md-evaluation)

## 효과적인 패턴

### 1. 구체적 명령어
```markdown
# ✅ 효과적
테스트: `pnpm vitest --run`
린트: `pnpm eslint . --fix`

# ❌ 비효과적
테스트와 린트를 실행하세요.
```

### 2. 명시적 금지
```markdown
# ✅ 효과적
- sed 사용 금지. sd를 사용하라.
- python -c 사용 금지. 임시 파일에 작성 후 실행.
- 기존 테스트 삭제 금지.

# ❌ 비효과적
- 좋은 코드를 작성하세요.
- 베스트 프랙티스를 따르세요.
```

### 3. 예시 코드
```markdown
# ✅ 효과적
에러 처리 패턴:
\\`\\`\\`typescript
try {
  const result = await operation();
  return { ok: true, data: result };
} catch (e) {
  logger.error('operation failed', { error: e });
  return { ok: false, error: e.message };
}
\\`\\`\\`

# ❌ 비효과적
에러를 적절히 처리하세요.
```

### 4. 디렉토리 구조 명시
```markdown
# ✅ 효과적
src/
  routes/     — API 라우트 핸들러
  services/   — 비즈니스 로직
  models/     — 데이터 모델
  utils/      — 유틸리티 함수
```

## 효과 없는 패턴

- 일반적인 코딩 조언 ("클린 코드를 작성하세요")
- 코드 스타일 규칙 (linter에 위임)
- 너무 긴 설명 (500줄 이상)
- 모호한 지시 ("적절히 처리하세요")

## DAIR.AI 연구 결과

- AGENTS.md가 있을 때 에이전트 성능이 향상되는 경우가 있지만
- 효과는 **구체성**에 비례
- 일반적 조언은 거의 효과 없음
- 명령어, 금지사항, 예시 코드가 가장 효과적
""")


# ─────────────────────────────────────────────
# 11. Sub-Agent Architecture — 서브에이전트 아키텍처
# ─────────────────────────────────────────────
add("sub-agent-architecture", ["coding", "sub-agent", "ai-agent", "architecture", "claude-code"],
    "Developer", "Sub-Agent Architecture — AI 코딩 서브에이전트 설계",
    """## 개요

AI 코딩 에이전트를 역할별로 분리하여 전문화된 서브에이전트로 구성하는 아키텍처.
각 서브에이전트는 고유한 시스템 프롬프트, 도구 접근 권한, 전문 영역을 가진다.

> 참고: [hesreallyhim/awesome-claude-code-agents](https://github.com/hesreallyhim/awesome-claude-code-agents),
> [blog.saurav.io — AI Coding Stack](https://blog.saurav.io/ai-coding-stack-explained/)

## 서브에이전트 유형

### 역할 기반 분류

| 에이전트 | 역할 | 전문 영역 |
|----------|------|-----------|
| ts-coder | TypeScript 개발 | 타입 안전성, 함수형 패턴 |
| react-coder | React 개발 | 컴포넌트, 훅, 상태 관리 |
| backend-architect | 백엔드 설계 | API, DB, 스케일링 |
| code-reviewer | 코드 리뷰 | 보안, 성능, 아키텍처 |
| ui-engineer | UI 개발 | 접근성, 반응형, 컴포넌트 |

### 에이전트 파일 구조

```markdown
---
name: ts-coder
description: TypeScript 코드 작성 및 리팩터링
model: opus
color: green
---

[에이전트 시스템 프롬프트]
```

## 설계 원칙

### 1. 단일 책임
각 에이전트는 하나의 명확한 역할만 수행.
"풀스택 에이전트"보다 전문화된 에이전트가 효과적.

### 2. 명확한 인터페이스
에이전트 간 소통은 명확한 입출력으로 정의.
메인 에이전트가 서브에이전트에게 구체적 태스크를 위임.

### 3. 컨텍스트 격리
각 에이전트는 자신의 역할에 필요한 컨텍스트만 로드.
불필요한 정보로 컨텍스트 윈도우를 낭비하지 않음.

## 오케스트레이션 패턴

```
메인 에이전트 (오케스트레이터)
  ├── context-gatherer → 코드베이스 분석
  ├── ts-coder → TypeScript 구현
  ├── code-reviewer → 코드 리뷰
  └── test-writer → 테스트 작성
```
""")


# ─────────────────────────────────────────────
# 12. Ralph Loop — 자율 반복 실행 패턴
# ─────────────────────────────────────────────
add("ralph-loop", ["coding", "ralph-loop", "autonomous", "ai-agent", "testing"],
    "Developer", "Ralph Loop — AI 에이전트 자율 반복 실행 패턴",
    """## 개요

Geoffrey Huntley가 만든 "Ralph Wiggum 기법". AI 코딩 에이전트를 스펙에 대해
자율적으로 반복 실행하여 기대 결과가 충족될 때까지 돌리는 방법론.
2026년 초 AI 코딩 커뮤니티에서 가장 많이 논의된 개발 방법론이다.

> 참고: [learndevrel.com — The Ralph Loop](https://learndevrel.com/blog/ralph-loop-ai-coding)

## 핵심 개념

```bash
while ! tests_pass; do
  ai_agent fix_failing_tests
done
```

스펙(테스트)을 먼저 작성하고, AI 에이전트가 모든 테스트를 통과할 때까지
자율적으로 코드를 수정하게 한다.

## 워크플로우

### 1. 스펙 정의
- 기대 동작을 테스트로 작성
- 엣지 케이스 포함
- 성능 기준 포함 (필요시)

### 2. 에이전트 실행
- 에이전트에게 테스트 통과를 목표로 지시
- 실패 시 자동으로 수정 시도
- 성공할 때까지 반복

### 3. 검증
- 모든 테스트 통과 확인
- 코드 리뷰 (사람)
- 의도하지 않은 부수효과 확인

## 전제 조건

- 명확하고 포괄적인 테스트 스위트
- 에이전트의 파일 시스템 접근 권한
- 테스트 실행 명령어가 CLAUDE.md에 명시
- 적절한 타임아웃 설정

## 주의사항

- 테스트가 불완전하면 "테스트만 통과하는" 나쁜 코드가 생길 수 있음
- 무한 루프 방지를 위한 최대 반복 횟수 설정 필요
- 보안 관련 코드에는 부적합 — 수동 리뷰 필수
""")

# ─────────────────────────────────────────────
# 13. Agentic Coding Manifests — 에이전트 매니페스트
# ─────────────────────────────────────────────
add("agentic-manifests", ["coding", "manifest", "agents-md", "claude-md", "convention"],
    "Developer", "Agentic Coding Manifests — 에이전트 매니페스트 표준",
    """## 개요

AI 코딩 에이전트에게 프로젝트 컨텍스트, 정체성, 운영 규칙을 제공하는
설정 파일(CLAUDE.md, AGENTS.md 등)의 표준과 패턴.
2026년 1월 기준 GitHub에서 60,000개 이상의 오픈소스 프로젝트가 이 형식을 사용한다.

> 참고: [arxiv.org — On the Use of Agentic Coding Manifests](https://arxiv.org/html/2509.14744v1),
> [emergentmind.com — Agentic Coding Manifests](https://www.emergentmind.com/topics/agentic-coding-manifests)

## 매니페스트 유형

| 파일명 | 도구 | 범위 |
|--------|------|------|
| CLAUDE.md | Claude Code | Claude 전용 |
| AGENTS.md | 범용 | Cursor, Copilot, Codex 등 |
| .cursorrules | Cursor | Cursor 전용 |
| copilot-instructions.md | GitHub Copilot | Copilot 전용 |
| GEMINI.md | Gemini | Gemini 전용 |

## AGENTS.md — 범용 표준

Linux Foundation 산하 Agentic AI Foundation이 관리.
모든 AI 코딩 도구에서 작동하는 범용 형식.

### 필수 섹션

```markdown
# AGENTS.md

## Project Overview
[프로젝트 설명]

## Commands
- build: `npm run build`
- test: `npm test`
- lint: `npm run lint`

## Architecture
[디렉토리 구조 및 모듈 관계]

## Conventions
[코딩 규칙]

## Constraints
[금지 사항]
```

## 연구 결과 (arxiv)

- 매니페스트는 얕은 계층 구조와 명시적 섹션 분할을 가짐
- 빠른 컨텍스트 획득과 재현 가능한 워크플로우 실행을 지원
- 구체적 명령어와 금지사항이 가장 효과적
- 일반적 조언은 효과가 제한적
""")


# ─────────────────────────────────────────────
# 14. Security-First Agent Rules — 보안 우선 에이전트 규칙
# ─────────────────────────────────────────────
add("security-first-agent", ["coding", "security", "ai-agent", "defi", "rules"],
    "Security Engineer", "Security-First Agent Rules — 보안 우선 AI 에이전트 규칙",
    """## 개요

보안이 최우선인 프로젝트(DeFi, 금융, 인프라 등)에서 AI 코딩 에이전트가 따라야 할 규칙.
Citadel Protocol 등 보안 크리티컬 프로젝트의 CLAUDE.md 패턴에서 추출.

> 참고: [josix/awesome-claude-md — Citadel Protocol](https://github.com/josix/awesome-claude-md/blob/main/scenarios/complex-projects/Citadel-Protocol_contracts/analysis.md)

## 핵심 규칙

### 1. 보안 검토 필수
- 모든 외부 입력에 대한 유효성 검사
- SQL 인젝션, XSS, CSRF 등 OWASP Top 10 체크
- 인증/인가 로직 변경 시 반드시 수동 리뷰

### 2. 비밀 정보 관리
- 하드코딩된 시크릿 절대 금지
- 환경 변수 또는 시크릿 매니저 사용
- 로그에 민감 정보 출력 금지
- 코드 예시에서 PII는 플레이스홀더 사용

### 3. 의존성 보안
- 새 의존성 추가 시 보안 감사 필요
- 알려진 취약점이 있는 버전 사용 금지
- 최소 권한 원칙 적용

### 4. 에러 처리
- 내부 에러 상세를 외부에 노출 금지
- 스택 트레이스를 사용자에게 보여주지 않음
- 에러 로깅은 내부 시스템에만

### 5. 코드 변경 제한
- 보안 관련 파일 변경 시 명시적 승인 필요
- 인증 미들웨어, 권한 체크 로직은 자동 변경 금지
- 암호화 관련 코드는 검증된 라이브러리만 사용

## CLAUDE.md 보안 섹션 템플릿

```markdown
## Security Rules
- NEVER hardcode secrets, API keys, or credentials
- NEVER log sensitive data (PII, tokens, passwords)
- ALWAYS validate external input before processing
- ALWAYS use parameterized queries for database access
- NEVER modify auth middleware without explicit approval
- NEVER disable security headers or CORS restrictions
```

## 보안 체크리스트

- [ ] 입력 유효성 검사
- [ ] 출력 인코딩
- [ ] 인증/인가 확인
- [ ] 세션 관리
- [ ] 에러 처리 (정보 누출 방지)
- [ ] 로깅 (민감 정보 제외)
- [ ] 의존성 취약점 스캔
""")

# ─────────────────────────────────────────────
# 15. Monorepo Agent Rules — 모노레포 에이전트 규칙
# ─────────────────────────────────────────────
add("monorepo-agent-rules", ["coding", "monorepo", "ai-agent", "architecture", "turborepo"],
    "Developer", "Monorepo Agent Rules — 모노레포 AI 에이전트 규칙",
    """## 개요

모노레포 환경에서 AI 코딩 에이전트가 효과적으로 작업하기 위한 규칙.
Cloudflare Workers SDK 등 대규모 모노레포 프로젝트의 패턴에서 추출.

> 참고: [josix/awesome-claude-md — Cloudflare Workers SDK](https://github.com/josix/awesome-claude-md/blob/main/scenarios/developer-tooling/cloudflare_workers-sdk/README.md)

## 핵심 규칙

### 1. 패키지 경계 존중
- 다른 패키지의 내부 구현에 직접 접근 금지
- 공개 API를 통해서만 패키지 간 소통
- 순환 의존성 생성 금지

### 2. 변경 범위 제한
- 한 번에 하나의 패키지만 변경 (가능한 경우)
- 크로스 패키지 변경 시 영향 범위 명시
- 공유 패키지 변경 시 모든 소비자 테스트 실행

### 3. 빌드 시스템 이해
```markdown
## Build Commands
- 전체 빌드: `turbo build`
- 단일 패키지: `turbo build --filter=@scope/package`
- 테스트: `turbo test --filter=@scope/package`
- 의존성 그래프: `turbo graph`
```

### 4. Progressive Disclosure
```
root/
  CLAUDE.md              ← 전체 프로젝트 규칙
  packages/
    api/CLAUDE.md        ← API 패키지 규칙
    web/CLAUDE.md        ← 웹 패키지 규칙
    shared/CLAUDE.md     ← 공유 패키지 규칙
```

### 5. 변경 로그
- 사용자 영향이 있는 변경은 changeset 생성
- 내부 변경은 changeset 불필요
- 버전 범프는 자동화 도구에 위임

## 모노레포 CLAUDE.md 템플릿

```markdown
# CLAUDE.md

## Monorepo Structure
- `packages/api` — REST API 서버
- `packages/web` — 프론트엔드 앱
- `packages/shared` — 공유 유틸리티

## Rules
- 패키지 간 직접 import 금지 (공개 API만 사용)
- 변경 시 해당 패키지의 테스트만 실행
- 공유 패키지 변경 시 전체 테스트 실행
```
""")


# ─────────────────────────────────────────────
# 16. MCP Integration — MCP 통합 패턴
# ─────────────────────────────────────────────
add("mcp-integration", ["coding", "mcp", "model-context-protocol", "ai-agent", "tools"],
    "Developer", "MCP Integration — Model Context Protocol 통합 패턴",
    """## 개요

Model Context Protocol(MCP)을 활용하여 AI 코딩 에이전트의 능력을 확장하는 패턴.
외부 도구, 데이터베이스, API를 에이전트에 연결하여 실시간 정보 접근과 작업 자동화를 가능하게 한다.

> 참고: [blog.saurav.io — AI Coding Stack](https://blog.saurav.io/ai-coding-stack-explained/)

## MCP란?

AI 모델이 외부 도구와 데이터 소스에 접근하기 위한 표준 프로토콜.
에이전트가 파일 시스템, 데이터베이스, API 등과 상호작용할 수 있게 한다.

## 설정 구조

```json
{
  "mcpServers": {
    "server-name": {
      "command": "uvx",
      "args": ["package-name@latest"],
      "env": { "KEY": "value" },
      "disabled": false,
      "autoApprove": ["tool-name"]
    }
  }
}
```

## 활용 패턴

### 1. 문서 검색
```json
{
  "aws-docs": {
    "command": "uvx",
    "args": ["awslabs.aws-documentation-mcp-server@latest"]
  }
}
```

### 2. 데이터베이스 접근
```json
{
  "postgres": {
    "command": "uvx",
    "args": ["mcp-server-postgres", "--connection-string", "..."]
  }
}
```

### 3. 메모리 시스템
```json
{
  "memory": {
    "command": "uvx",
    "args": ["mem-mesh-mcp-server@latest"]
  }
}
```

## 보안 고려사항

- autoApprove는 신뢰할 수 있는 도구에만 사용
- 데이터베이스 접근은 읽기 전용 권한 권장
- 민감한 환경 변수는 별도 관리
- MCP 서버의 네트워크 접근 범위 제한
""")

# ─────────────────────────────────────────────
# 17. Code Review Agent — 코드 리뷰 에이전트
# ─────────────────────────────────────────────
add("code-review-agent", ["coding", "code-review", "ai-agent", "quality", "security"],
    "Senior Developer", "Code Review Agent — AI 코드 리뷰 에이전트 설계",
    """## 개요

15년 이상 경험의 시니어 개발자 관점에서 코드를 분석하는 AI 코드 리뷰 에이전트 설계.
보안 취약점, 성능 병목, 아키텍처 결정을 종합적으로 검토한다.

> 참고: [hesreallyhim/awesome-claude-code-agents — senior-code-reviewer](https://github.com/hesreallyhim/awesome-claude-code-agents)

## 리뷰 관점 5가지

### 1. 보안 (Critical)
- 입력 유효성 검사 누락
- 인증/인가 우회 가능성
- 민감 정보 노출
- 인젝션 취약점

### 2. 성능 (High)
- N+1 쿼리 문제
- 불필요한 메모리 할당
- 블로킹 I/O
- 캐싱 기회 누락

### 3. 아키텍처 (High)
- 단일 책임 원칙 위반
- 순환 의존성
- 레이어 경계 침범
- 과도한 결합

### 4. 유지보수성 (Medium)
- 매직 넘버/스트링
- 중복 코드
- 불명확한 네이밍
- 누락된 에러 처리

### 5. 테스트 (Medium)
- 테스트 커버리지 부족
- 엣지 케이스 누락
- 깨지기 쉬운 테스트
- 테스트 격리 부족

## 리뷰 출력 형식

```markdown
## 🔴 Critical
- [파일:줄] [설명] — [수정 제안]

## 🟡 Warning
- [파일:줄] [설명] — [수정 제안]

## 🟢 Suggestion
- [파일:줄] [설명] — [수정 제안]

## ✅ Good Practices
- [칭찬할 점]
```
""")


# ─────────────────────────────────────────────
# 18. Hooks & Automation — 훅과 자동화 패턴
# ─────────────────────────────────────────────
add("hooks-automation", ["coding", "hooks", "automation", "ai-agent", "ci-cd"],
    "Developer", "Hooks & Automation — AI 에이전트 훅과 자동화 패턴",
    """## 개요

AI 코딩 에이전트의 동작을 이벤트 기반으로 자동화하는 훅(Hook) 시스템.
파일 변경, 도구 실행, 태스크 완료 등의 이벤트에 반응하여 자동으로 작업을 수행한다.

## 훅 유형

| 이벤트 | 트리거 시점 | 용도 |
|--------|------------|------|
| fileEdited | 파일 저장 시 | 린트, 포맷, 테스트 |
| fileCreated | 파일 생성 시 | 보일러플레이트 검증 |
| preToolUse | 도구 실행 전 | 권한 체크, 검증 |
| postToolUse | 도구 실행 후 | 결과 검증, 로깅 |
| promptSubmit | 프롬프트 전송 시 | 컨텍스트 주입 |
| postTaskExecution | 태스크 완료 후 | 테스트 실행 |

## 실전 패턴

### 1. 저장 시 린트
```json
{
  "name": "Lint on Save",
  "version": "1.0.0",
  "when": {
    "type": "fileEdited",
    "patterns": ["*.ts", "*.tsx"]
  },
  "then": {
    "type": "runCommand",
    "command": "npm run lint"
  }
}
```

### 2. 쓰기 작업 검증
```json
{
  "name": "Review Write Operations",
  "version": "1.0.0",
  "when": {
    "type": "preToolUse",
    "toolTypes": ["write"]
  },
  "then": {
    "type": "askAgent",
    "prompt": "이 쓰기 작업이 코딩 표준을 따르는지 확인하라"
  }
}
```

### 3. 태스크 후 테스트
```json
{
  "name": "Test After Task",
  "version": "1.0.0",
  "when": {
    "type": "postTaskExecution"
  },
  "then": {
    "type": "runCommand",
    "command": "npm test"
  }
}
```

## 설계 원칙

- 훅은 빠르게 실행되어야 함 (60초 타임아웃 기본)
- preToolUse 훅이 접근을 거부하면 도구 실행 금지
- 순환 의존성 주의 (훅 A → 도구 X → 훅 A)
- 훅은 보조적 — 핵심 로직을 훅에 넣지 마라
""")

# ─────────────────────────────────────────────
# 19. Progressive Disclosure — 점진적 공개 패턴
# ─────────────────────────────────────────────
add("progressive-disclosure", ["coding", "progressive-disclosure", "claude-md", "architecture", "ai-agent"],
    "Developer", "Progressive Disclosure — CLAUDE.md 점진적 공개 패턴",
    """## 개요

대규모 프로젝트에서 AI 에이전트에게 컨텍스트를 계층적으로 제공하는 패턴.
에이전트가 작업하는 디렉토리에 따라 관련 규칙만 로드하여 컨텍스트 윈도우를 효율적으로 사용한다.

> 참고: [greeto.me — CLAUDE.md Progressive Disclosure](https://greeto.me/blog/claude-md-progressive-disclosure-for-fast-teams),
> [potapov.dev — The Definitive Guide to CLAUDE.md](https://potapov.dev/blog/claude-md-guide)

## 계층 구조

```
project/
  CLAUDE.md                    ← L0: 전체 프로젝트 규칙
  packages/
    api/
      CLAUDE.md                ← L1: API 패키지 규칙
      src/
        auth/
          CLAUDE.md            ← L2: 인증 모듈 규칙
    web/
      CLAUDE.md                ← L1: 웹 패키지 규칙
```

## 각 레벨의 역할

### L0 — 프로젝트 루트
- 빌드/테스트 명령어
- 전체 아키텍처 개요
- 공통 코딩 규칙
- 금지 사항

### L1 — 패키지/모듈
- 패키지별 빌드 명령어
- 패키지 내부 아키텍처
- 패키지별 의존성 규칙

### L2 — 기능/도메인
- 도메인 특화 규칙
- 보안 요구사항
- 특수한 테스트 패턴

## 규칙 배치 원칙

| 규칙 유형 | 배치 레벨 | 예시 |
|-----------|----------|------|
| 빌드 명령어 | L0 | `pnpm test` |
| 패키지 매니저 | L0 | "pnpm만 사용" |
| API 규칙 | L1 | "REST 규칙 준수" |
| 인증 규칙 | L2 | "JWT 검증 필수" |

## 토큰 예산 가이드

- L0: 100~200줄 (매 세션 로드)
- L1: 50~100줄 (해당 패키지 작업 시)
- L2: 20~50줄 (해당 모듈 작업 시)
- 총합이 500줄을 넘지 않도록 관리
""")


# ─────────────────────────────────────────────
# 20. Self-Learning Agents — 자기 학습 에이전트
# ─────────────────────────────────────────────
add("self-learning-agents", ["coding", "self-learning", "ai-agent", "memory", "patterns"],
    "Developer", "Self-Learning Agents — 자기 학습 AI 에이전트 패턴",
    """## 개요

AI 코딩 에이전트가 실행 이력을 추적하고 패턴을 인식하여
시간이 지남에 따라 개선되는 자기 학습 시스템 설계.

> 참고: [Equilateral Agents Open Core](https://github.com/Equilateral-AI/equilateral-agents-open-core)

## 핵심 구성요소

### 1. 에이전트 메모리
- 최근 100회 실행 이력 추적
- 성공/실패 패턴 기록
- 자주 사용되는 명령어 학습

### 2. 패턴 인식
- 반복되는 에러 패턴 감지
- 효과적인 해결 방법 기억
- 프로젝트별 관용구 학습

### 3. 워크플로우 최적화
- 자주 수행하는 작업 순서 최적화
- 불필요한 단계 제거
- 병렬 실행 가능한 작업 식별

## 메모리 시스템 설계

```
memory/
  decisions.md     — 아키텍처 결정 기록
  patterns.md      — 발견된 코드 패턴
  errors.md        — 해결된 에러와 해결법
  preferences.md   — 사용자 선호도
```

## 학습 사이클

```
1. 작업 수행
2. 결과 평가 (성공/실패)
3. 패턴 추출
4. 메모리에 저장
5. 다음 작업에 적용
```

## 실전 적용

### 에러 학습
```markdown
## Error: ModuleNotFoundError
- 원인: 가상환경 미활성화
- 해결: `source .venv/bin/activate` 후 재실행
- 빈도: 3회 (최근 7일)
```

### 선호도 학습
```markdown
## User Preferences
- 테스트 프레임워크: pytest (vitest 아님)
- 패키지 매니저: pnpm (npm 아님)
- 에러 처리: Result 패턴 (try-catch 아님)
```
""")

# ─────────────────────────────────────────────
# main
# ─────────────────────────────────────────────
if __name__ == "__main__":
    write_all()
