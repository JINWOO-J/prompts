#!/usr/bin/env python3
"""
프롬프트 라이브러리 MCP 서버.

AI 에이전트가 프롬프트를 검색/조회할 수 있는 MCP 도구 제공.
도구: search_prompts, get_prompt

실행: python3 scripts/prompt-mcp-server.py (stdio transport)
"""

import json
import sys
import yaml
from pathlib import Path

ROOT = Path(__file__).parent.parent
INDEX = ROOT / "prompts.meta.yaml"

# --- 데이터 로드 ---

_prompts = None

def load_prompts():
    global _prompts
    if _prompts is not None:
        return _prompts
    with open(INDEX, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    _prompts = data.get("prompts", [])
    return _prompts


def read_content(prompt):
    path = ROOT / prompt["file"]
    if not path.exists():
        return f"(파일 없음: {prompt['file']})"
    content = path.read_text(encoding="utf-8")
    if content.startswith("---"):
        end = content.find("---", 3)
        if end != -1:
            return content[end + 3:].lstrip("\n")
    return content


# --- MCP 도구 핸들러 ---

def handle_search_prompts(args):
    prompts = load_prompts()
    query = args.get("query", "").lower()
    category = args.get("category")
    tag = args.get("tag")
    limit = args.get("limit", 10)

    results = prompts
    if category:
        results = [p for p in results if p["category"] == category]
    if tag:
        results = [p for p in results if tag in p.get("tags", [])]
    if query:
        results = [p for p in results if (
            query in p["title"].lower() or
            query in p["id"].lower() or
            query in p.get("category", "").lower() or
            any(query in t.lower() for t in p.get("tags", []))
        )]

    results = results[:limit]
    items = []
    for p in results:
        items.append({
            "id": p["id"],
            "title": p["title"],
            "category": p["category"],
            "origin": p.get("origin", "?"),
            "tags": p.get("tags", []),
            "file": p["file"],
        })

    return json.dumps({"count": len(items), "results": items}, ensure_ascii=False)


def handle_get_prompt(args):
    prompt_id = args.get("id", "")
    prompts = load_prompts()

    # 정확한 ID 매칭
    found = None
    for p in prompts:
        if p["id"] == prompt_id:
            found = p
            break

    # 부분 매칭 fallback
    if not found:
        matches = [p for p in prompts if prompt_id.lower() in p["id"].lower()]
        if len(matches) == 1:
            found = matches[0]
        elif len(matches) > 1:
            ids = [m["id"] for m in matches[:10]]
            return json.dumps({"error": f"여러 프롬프트 매칭: {ids}"}, ensure_ascii=False)

    if not found:
        return json.dumps({"error": f"'{prompt_id}' 프롬프트를 찾을 수 없습니다"}, ensure_ascii=False)

    content = read_content(found)
    return json.dumps({
        "id": found["id"],
        "title": found["title"],
        "category": found["category"],
        "origin": found.get("origin", "?"),
        "tags": found.get("tags", []),
        "file": found["file"],
        "content": content,
    }, ensure_ascii=False)


# --- MCP 프로토콜 (JSON-RPC over stdio) ---

TOOLS = [
    {
        "name": "search_prompts",
        "description": "인프라/보안 운영 프롬프트 라이브러리 검색. 431개 프롬프트에서 키워드, 카테고리, 태그로 검색합니다.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "검색 키워드 (제목, ID, 태그에서 매칭)"},
                "category": {"type": "string", "description": "카테고리 필터 (rca, incident-response, infrastructure, security, application, data-ai, shared, techniques, coding)"},
                "tag": {"type": "string", "description": "태그 필터 (예: kubernetes, lambda, rds)"},
                "limit": {"type": "integer", "description": "최대 결과 수 (기본 10)", "default": 10},
            },
        },
    },
    {
        "name": "get_prompt",
        "description": "프롬프트 ID로 본문 전체를 조회합니다. search_prompts로 ID를 먼저 찾은 뒤 사용하세요.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "id": {"type": "string", "description": "프롬프트 ID (예: rca-01_basic_rca)"},
            },
            "required": ["id"],
        },
    },
]

TOOL_HANDLERS = {
    "search_prompts": handle_search_prompts,
    "get_prompt": handle_get_prompt,
}


def make_response(req_id, result):
    return {"jsonrpc": "2.0", "id": req_id, "result": result}


def make_error(req_id, code, message):
    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}}


def handle_request(req):
    method = req.get("method", "")
    req_id = req.get("id")
    params = req.get("params", {})

    if method == "initialize":
        return make_response(req_id, {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "prompt-library", "version": "1.0.0"},
        })

    if method == "notifications/initialized":
        return None  # 알림 — 응답 불필요

    if method == "tools/list":
        return make_response(req_id, {"tools": TOOLS})

    if method == "tools/call":
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})
        handler = TOOL_HANDLERS.get(tool_name)
        if not handler:
            return make_error(req_id, -32601, f"Unknown tool: {tool_name}")
        try:
            result_text = handler(arguments)
            return make_response(req_id, {
                "content": [{"type": "text", "text": result_text}],
            })
        except Exception as e:
            return make_error(req_id, -32603, str(e))

    # 알 수 없는 메서드
    if req_id is not None:
        return make_error(req_id, -32601, f"Method not found: {method}")
    return None


def main():
    """stdio JSON-RPC 루프"""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            resp = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "Parse error"}}
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()
            continue

        resp = handle_request(req)
        if resp is not None:
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
