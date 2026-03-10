#!/usr/bin/env python3
"""Agent: 패턴 프롬프트에 agent 태그 추가 (md + DB)"""
import sqlite3, json, pathlib, re

DB = pathlib.Path("prompts.db")
DIRS = ["rca", "incident-response", "application", "infrastructure", "security", "data-ai", "shared", "techniques", "coding"]

# 1. DB 업데이트
conn = sqlite3.connect(DB)
cur = conn.cursor()
rows = cur.execute("SELECT id, tags FROM prompts WHERE title LIKE 'Agent:%'").fetchall()
updated_db = 0
for pid, tags_json in rows:
    tags = json.loads(tags_json)
    if "agent" not in tags:
        tags.append("agent")
        cur.execute("UPDATE prompts SET tags = ? WHERE id = ?", (json.dumps(tags), pid))
        updated_db += 1
        print(f"  DB: {pid} += agent")
conn.commit()
conn.close()
print(f"DB 업데이트: {updated_db}건")

# 2. md 파일 업데이트
updated_md = 0
for d in DIRS:
    dp = pathlib.Path(d)
    if not dp.exists():
        continue
    for f in dp.glob("agent-*.md"):
        text = f.read_text()
        # frontmatter에서 tags 블록 찾기
        m = re.match(r"(---\n.*?)(tags:\n)(.*?)(---)", text, re.DOTALL)
        if not m:
            continue
        tag_block = m.group(3)
        if "- agent\n" in tag_block:
            continue
        # tags: 바로 뒤에 - agent 추가
        new_text = text.replace(m.group(2) + m.group(3), m.group(2) + "- agent\n" + m.group(3))
        f.write_text(new_text)
        updated_md += 1
        print(f"  MD: {f}")

print(f"MD 업데이트: {updated_md}건")
