---
inclusion: manual
---

# 프롬프트 라이브러리 사용 가이드

431개 인프라/보안 운영 프롬프트를 검색하고 활용하는 방법.

## MCP 도구 (prompt-library 서버)

```
# 키워드 검색
search_prompts(query="kubernetes pod crash", limit=5)

# 카테고리 필터
search_prompts(category="incident-response")

# 태그 필터
search_prompts(tag="lambda")

# 본문 조회
get_prompt(id="rca-01_basic_rca")
```

## CLI 도구

```bash
# 검색
python3 scripts/prompt-cli.py search kubernetes

# 본문 출력
python3 scripts/prompt-cli.py get rca-01_basic_rca

# 클립보드 복사
python3 scripts/prompt-cli.py copy rca-01_basic_rca

# 프롬프트 + 로그 결합
kubectl logs pod-name | python3 scripts/prompt-cli.py pipe rca-01_basic_rca --copy

# 여러 프롬프트 결합
python3 scripts/prompt-cli.py compose guardrails role-definitions rca-01_basic_rca --copy

# fzf 인터랙티브
python3 scripts/prompt-cli.py fzf

# 통계
python3 scripts/prompt-cli.py stats
```

## 카테고리 (8종)

- rca (6) — 근본 원인 분석 (5-Whys, ToT, Diamond Model)
- incident-response (73) — AWS 장애 대응 플레이북
- infrastructure (264) — K8s Proactive 플레이북, 클라우드 아키텍처
- security (29) — 보안 감사, 위협 모델링
- application (25) — 앱 개발 가이드
- data-ai (12) — 데이터/AI 파이프라인
- shared (21) — 범용 오케스트레이터, 가드레일
- techniques (1) — 프롬프트 기법
