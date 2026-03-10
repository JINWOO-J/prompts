---
inclusion: fileMatch
fileMatchPattern: "*.yaml,*.yml,Dockerfile*,*.tf,*.hcl,*.sh,*.bash"
---

# SRE/인프라 운영 프롬프트 가이드

인프라 파일을 편집 중입니다. 프롬프트 라이브러리 MCP 서버(`prompt-library`)를 활용하세요.

## 사용 가능한 도구

- `search_prompts` — 키워드/카테고리/태그로 431개 운영 프롬프트 검색
- `get_prompt` — ID로 프롬프트 본문 조회

## 추천 워크플로우

1. 장애 대응 시: `search_prompts(category="incident-response", query="<서비스명>")`
2. RCA 작성 시: `search_prompts(category="rca")`
3. 보안 점검 시: `search_prompts(category="security")`
4. K8s 이슈: `search_prompts(tag="kubernetes")`
5. AWS 서비스별: `search_prompts(query="lambda")`, `search_prompts(query="rds")`

## 주요 카테고리

| 카테고리 | 설명 | 수량 |
|----------|------|------|
| infrastructure | K8s Proactive 플레이북 등 | 264 |
| incident-response | AWS 장애 대응 플레이북 | 73 |
| security | 보안 점검/감사 | 29 |
| rca | 근본 원인 분석 | 6 |
