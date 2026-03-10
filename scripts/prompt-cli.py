#!/usr/bin/env python3
"""
프롬프트 라이브러리 CLI.

사용법:
  prompt search <query>              # 키워드 검색
  prompt list [--cat X] [--tag X]    # 필터링 목록
  prompt get <id-or-file>            # 본문 출력
  prompt copy <id-or-file>           # 클립보드 복사
  prompt fzf                         # fzf 인터랙티브 선택 → 복사
"""

import argparse
import subprocess
import sys
import yaml
from pathlib import Path

ROOT = Path(__file__).parent.parent
INDEX = ROOT / "prompts.meta.yaml"


def load_index():
    with open(INDEX, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data.get("prompts", [])


def match(prompt, query):
    """제목, 태그, 카테고리, ID에서 query 매칭"""
    q = query.lower()
    if q in prompt["title"].lower():
        return True
    if q in prompt["id"].lower():
        return True
    if q in prompt.get("category", "").lower():
        return True
    if any(q in t.lower() for t in prompt.get("tags", [])):
        return True
    return False


def read_content(prompt):
    """프롬프트 파일의 본문(frontmatter 제외)을 읽어 반환"""
    path = ROOT / prompt["file"]
    if not path.exists():
        return f"(파일 없음: {prompt['file']})"
    content = path.read_text(encoding="utf-8")
    # strip frontmatter
    if content.startswith("---"):
        end = content.find("---", 3)
        if end != -1:
            return content[end + 3:].lstrip("\n")
    return content


def find_prompt(prompts, key):
    """ID, 파일명, 부분 매칭으로 프롬프트 찾기"""
    # 정확한 ID 매칭
    for p in prompts:
        if p["id"] == key:
            return p
    # 파일 경로 매칭
    for p in prompts:
        if p["file"] == key or p["file"].endswith(key):
            return p
    # 부분 ID 매칭 (하나만 매칭될 때)
    matches = [p for p in prompts if key.lower() in p["id"].lower()]
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        print(f"⚠️  '{key}'에 매칭되는 프롬프트가 {len(matches)}개입니다:", file=sys.stderr)
        for m in matches[:10]:
            print(f"  {m['id']}  {m['title'][:50]}", file=sys.stderr)
        return None
    return None


def pbcopy(text):
    """macOS 클립보드에 복사"""
    try:
        proc = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE)
        proc.communicate(text.encode("utf-8"))
        return True
    except FileNotFoundError:
        # Linux xclip fallback
        try:
            proc = subprocess.Popen(["xclip", "-selection", "clipboard"], stdin=subprocess.PIPE)
            proc.communicate(text.encode("utf-8"))
            return True
        except FileNotFoundError:
            return False


# --- 서브커맨드 ---

def cmd_search(args, prompts):
    query = " ".join(args.query)
    results = [p for p in prompts if match(p, query)]

    if not results:
        print(f"'{query}'에 매칭되는 프롬프트가 없습니다.")
        return

    print(f"🔍 '{query}' — {len(results)}건\n")
    for p in results:
        tags = ", ".join(p.get("tags", [])[:4])
        print(f"  {p['id']:<45} {p['category']:<18} {tags}")


def cmd_list(args, prompts):
    filtered = prompts
    if args.cat:
        filtered = [p for p in filtered if p["category"] == args.cat]
    if args.origin:
        filtered = [p for p in filtered if p.get("origin") == args.origin]
    if args.tag:
        filtered = [p for p in filtered if args.tag in p.get("tags", [])]

    if not filtered:
        print("매칭되는 프롬프트가 없습니다.")
        return

    print(f"📋 {len(filtered)}건\n")
    for p in filtered:
        origin = p.get("origin", "?")
        print(f"  {p['id']:<45} [{origin:<12}] {p['title'][:50]}")


def cmd_get(args, prompts):
    p = find_prompt(prompts, args.key)
    if not p:
        print(f"❌ '{args.key}'를 찾을 수 없습니다.", file=sys.stderr)
        sys.exit(1)

    print(f"# {p['title']}")
    print(f"# category: {p['category']}  origin: {p.get('origin', '?')}")
    print(f"# tags: {', '.join(p.get('tags', []))}")
    print(f"# file: {p['file']}")
    print("---")
    print(read_content(p))


def cmd_copy(args, prompts):
    p = find_prompt(prompts, args.key)
    if not p:
        print(f"❌ '{args.key}'를 찾을 수 없습니다.", file=sys.stderr)
        sys.exit(1)

    content = read_content(p)
    if pbcopy(content):
        print(f"✅ 클립보드에 복사됨: {p['title'][:60]}")
    else:
        print("⚠️  클립보드 도구를 찾을 수 없습니다. stdout으로 출력합니다.\n")
        print(content)


def cmd_fzf(args, prompts):
    """fzf 인터랙티브 선택 → 클립보드 복사"""
    try:
        subprocess.run(["fzf", "--version"], capture_output=True, check=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("❌ fzf가 설치되어 있지 않습니다. brew install fzf", file=sys.stderr)
        sys.exit(1)

    lines = []
    for p in prompts:
        origin = p.get("origin", "?")
        lines.append(f"{p['id']}\t[{p['category']}] [{origin}] {p['title'][:60]}")

    input_text = "\n".join(lines)
    result = subprocess.run(
        ["fzf", "--delimiter=\t", "--with-nth=2", "--preview-window=wrap",
         "--header=Select a prompt (Enter to copy)"],
        input=input_text, capture_output=True, text=True,
    )

    if result.returncode != 0:
        return  # 사용자가 ESC

    selected_id = result.stdout.strip().split("\t")[0]
    p = find_prompt(prompts, selected_id)
    if p:
        content = read_content(p)
        if pbcopy(content):
            print(f"✅ 클립보드에 복사됨: {p['title'][:60]}")
        else:
            print(content)


def cmd_pipe(args, prompts):
    """프롬프트 + stdin 컨텍스트 결합 출력"""
    p = find_prompt(prompts, args.key)
    if not p:
        print(f"❌ '{args.key}'를 찾을 수 없습니다.", file=sys.stderr)
        sys.exit(1)

    content = read_content(p)

    # stdin에서 컨텍스트 읽기
    if not sys.stdin.isatty():
        context = sys.stdin.read()
    else:
        context = "(컨텍스트 없음 — stdin으로 로그/에러를 파이프하세요)"

    output = f"{content}\n\n---\n## 분석 대상 컨텍스트\n\n```\n{context}\n```"

    if args.copy:
        if pbcopy(output):
            print(f"✅ 프롬프트+컨텍스트 클립보드 복사됨: {p['title'][:50]}", file=sys.stderr)
            return
    print(output)


def cmd_compose(args, prompts):
    """여러 프롬프트를 순서대로 결합 출력"""
    parts = []
    for key in args.keys:
        p = find_prompt(prompts, key)
        if not p:
            print(f"⚠️  '{key}' 스킵 (찾을 수 없음)", file=sys.stderr)
            continue
        parts.append(f"# === {p['title']} ===\n# file: {p['file']}\n\n{read_content(p)}")

    if not parts:
        print("❌ 결합할 프롬프트가 없습니다.", file=sys.stderr)
        sys.exit(1)

    output = "\n\n---\n\n".join(parts)

    if args.copy:
        if pbcopy(output):
            print(f"✅ {len(parts)}개 프롬프트 결합 → 클립보드 복사됨", file=sys.stderr)
            return
    print(output)


def cmd_stats(args, prompts):
    """라이브러리 현황 통계"""
    from collections import Counter

    total = len(prompts)
    print(f"📊 프롬프트 라이브러리 통계 — 총 {total}개\n")

    # 카테고리별
    cats = Counter(p["category"] for p in prompts)
    print("카테고리별:")
    for cat, cnt in cats.most_common():
        bar = "█" * (cnt // 5) or "▏"
        print(f"  {cat:<20} {cnt:>4}  {bar}")

    # origin별
    origins = Counter(p.get("origin", "?") for p in prompts)
    print("\nOrigin별:")
    for origin, cnt in origins.most_common():
        print(f"  {origin:<20} {cnt:>4}")

    # 태그 빈도 top 15
    tag_counts = Counter()
    for p in prompts:
        tag_counts.update(p.get("tags", []))
    print("\n태그 Top 15:")
    for tag, cnt in tag_counts.most_common(15):
        print(f"  {tag:<25} {cnt:>4}")


def main():
    parser = argparse.ArgumentParser(
        prog="prompt",
        description="프롬프트 라이브러리 CLI (431개 인프라/보안 운영 프롬프트)",
    )
    sub = parser.add_subparsers(dest="command")

    # search
    sp = sub.add_parser("search", aliases=["s"], help="키워드 검색")
    sp.add_argument("query", nargs="+", help="검색어")

    # list
    sp = sub.add_parser("list", aliases=["ls"], help="목록 출력")
    sp.add_argument("--cat", help="카테고리 필터")
    sp.add_argument("--origin", help="origin 필터")
    sp.add_argument("--tag", help="태그 필터")

    # get
    sp = sub.add_parser("get", aliases=["g"], help="프롬프트 본문 출력")
    sp.add_argument("key", help="프롬프트 ID 또는 파일명")

    # copy
    sp = sub.add_parser("copy", aliases=["cp"], help="클립보드에 복사")
    sp.add_argument("key", help="프롬프트 ID 또는 파일명")

    # fzf
    sub.add_parser("fzf", help="fzf 인터랙티브 선택")

    # pipe
    sp = sub.add_parser("pipe", help="프롬프트 + stdin 컨텍스트 결합")
    sp.add_argument("key", help="프롬프트 ID")
    sp.add_argument("--copy", "-c", action="store_true", help="결과를 클립보드에 복사")

    # compose
    sp = sub.add_parser("compose", help="여러 프롬프트 결합 출력")
    sp.add_argument("keys", nargs="+", help="프롬프트 ID 목록")
    sp.add_argument("--copy", "-c", action="store_true", help="결과를 클립보드에 복사")

    # stats
    sub.add_parser("stats", help="라이브러리 현황 통계")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(0)

    prompts = load_index()

    commands = {
        "search": cmd_search, "s": cmd_search,
        "list": cmd_list, "ls": cmd_list,
        "get": cmd_get, "g": cmd_get,
        "copy": cmd_copy, "cp": cmd_copy,
        "fzf": cmd_fzf,
        "pipe": cmd_pipe,
        "compose": cmd_compose,
        "stats": cmd_stats,
    }
    commands[args.command](args, prompts)


if __name__ == "__main__":
    main()
