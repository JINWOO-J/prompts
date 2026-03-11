"""data.json이 최신 상태인지 확인"""
import json, pathlib

data = json.loads(pathlib.Path("web/data.json").read_text())
prompts = data.get("prompts", [])
meta = data.get("_meta", {})

# 1. agent 태그 확인
agent_count = sum(1 for p in prompts if "agent" in p.get("tags", []))
print(f"1. data.json agent 태그 프롬프트: {agent_count}개 (기대: 26개)")

# 2. 전체 프롬프트 수
print(f"2. 전체 프롬프트: {meta.get('total', len(prompts))}개")

# 3. coding 카테고리 존재 확인
coding_count = sum(1 for p in prompts if p.get("category") == "coding")
print(f"3. coding 카테고리: {coding_count}개")

# 4. 샘플 agent 프롬프트 태그 확인
for p in prompts:
    if p.get("id") == "inc-agent-devops-incident-responder":
        print(f"4. inc-agent-devops-incident-responder tags: {p['tags']}")
        break
