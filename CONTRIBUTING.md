# 기여 가이드 (CONTRIBUTING.md)

> 이 문서는 프롬프트 라이브러리에 새 파일을 추가하거나 기존 파일을 수정할 때의 절차와 기준을 정의합니다.
> 현재 **480개 프롬프트**, **9개 카테고리**로 구성되어 있다.

---

## 카테고리 기준

| 카테고리 | 용도 | 파일 유형 |
|---------|------|----------|
| `rca/` | 근본 원인 분석 방법론 프롬프트 | 자체 제작 (`NN_이름.md`) |
| `incident-response/` | 인시던트 초기 대응, AWS 서비스 장애 트리아지 | `agent-*.md`, `aws-*.md` |
| `application/` | 앱 레이어 에러 추적 (Sentry 에러 패턴) | `sentry-*.md` |
| `infrastructure/` | K8s, CI/CD, 인프라 트러블슈팅 | `agent-*.md`, `k8s-*.md`, `aws-07-*.md` |
| `security/` | 보안 침해, IAM, WAF, RBAC | `agent-*.md`, `aws-05-*.md`, `k8s-07-*.md` |
| `data-ai/` | Data/ML 엔지니어링, 데이터베이스 최적화 | `agent-*.md` |
| `shared/` | 공통 페르소나 정의, 가드레일, 범용 에이전트 | `*.md`, `*.agent.md` |
| `coding/` | AI 에이전트 코딩 패턴, 개발 방법론 | `*.md` |
| `techniques/` | 프롬프트 기법 참고 문서 (31개, `gen_techniques_v2.py`로 생성) | `*.md` |

---

## 파일 네이밍 규칙

```
agent-{역할명}.md           → AI 에이전트 역할 정의
aws-{섹션}-{장애명}.md      → AWS 서비스별 플레이북
k8s-{섹션}-{장애명}.md      → K8s 플레이북
sentry-{에러타입}.md         → 앱 레이어 에러 플레이북
playbook-{주제}.md          → 기타 운영 체크리스트
NN_{주제}.md                → RCA 단계별 프롬프트 (번호 고정)
```

---

## 필수 Frontmatter

모든 파일은 반드시 YAML frontmatter로 시작해야 한다:

```yaml
---
category: incident-response          # 카테고리 (위 표 참조, 필수)
source: "[레포명](URL)"               # 출처 (자체 제작이면 "custom")
role: SRE Engineer                   # 대상 역할
origin: custom                       # custom | voltagent | scoutflo | shawnewallace | extracted
tags:                                # 태그 목록 (필수, 3~6개 권장)
  - incident-response
  - aws
  - ec2
---
```

### 필드 설명

| 필드 | 필수 | 설명 |
|------|------|------|
| `category` | 필수 | 9개 카테고리 중 하나 |
| `source` | 필수 | 출처 URL 또는 `"custom"` |
| `origin` | 필수 | 원본 출처 식별자 |
| `tags` | 필수 | 검색/필터용 태그 배열. 기법, 대상 시스템, 역할 등을 포함 |
| `role` | 권장 | 대상 역할 (SRE, DevOps 등) |

> `origin` 필드는 frontmatter에 유지하지만, 웹 뷰어에서는 필터로 사용하지 않는다.

---

## 새 파일 추가 절차

### 자체 제작 프롬프트

1. 적절한 카테고리 폴더에 파일 생성
2. Frontmatter 작성 (`origin: custom`, `tags` 포함)
3. 내용 작성 후 인덱스 재생성 및 검증 실행:

```bash
python3 scripts/rebuild-index.py
python3 scripts/validate-index.py
```

4. PR 제출 (실제 인시던트 적용 결과 첨부 권장)

### 외부 레포에서 통합

1. `.tmp-sources/` 폴더에 레포 클론 (gitignore됨)
2. `extract_all.py` 스크립트 또는 수동으로 파일 복사
3. Frontmatter에 `source`, `origin`, `tags` 명시
4. 인덱스 재생성 및 검증 실행

---

## 인덱스 관리

파일을 추가/수정/삭제한 후 반드시 실행:

```bash
# 인덱스 재생성
python3 scripts/rebuild-index.py

# 인덱스 무결성 검증 (필수 필드 누락, 파일 경로 오류, 허용값 위반 확인)
python3 scripts/validate-index.py
```

`prompts.meta.yaml`이 자동으로 업데이트된다. `validate-index.py`는 다음을 검증한다:

- 필수 필드 존재 여부 (`id`, `file`, `title`, `category`, `origin`, `tags`)
- `category` 허용값 (9개 카테고리)
- `origin` 허용값
- 파일 경로 실존 여부

---

## 품질 기준

- [ ] 파일명이 네이밍 규칙을 따르는가?
- [ ] Frontmatter가 완전한가? (`category`, `source`, `origin`, `tags`)
- [ ] `tags`가 3개 이상 포함되어 있는가?
- [ ] 실제 인시던트에 적용 가능한 구체적인 내용인가?
- [ ] 기존 파일과 내용이 80% 이상 중복되지 않는가?
- [ ] `scripts/rebuild-index.py` 실행 후 `scripts/validate-index.py` 통과하는가?

---

## 포함하지 않는 것

- 비즈니스 로직, 마케팅, UI/UX 관련 프롬프트
- 특정 언어(Java, Python 등) 코딩 스타일 가이드 → 팀 레포에서 관리
- 1회성 임시 프롬프트 → 개인 노트에 보관
