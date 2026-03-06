#!/usr/bin/env python3
"""
전체 프롬프트 라이브러리 인덱스 자동 재생성 스크립트.
실행: python3 scripts/rebuild-index.py
결과: prompts.meta.yaml 업데이트
"""

import re
import json
import yaml
from pathlib import Path
from datetime import date

ROOT = Path(__file__).parent.parent
CATEGORIES = ["rca", "incident-response", "application", "infrastructure", "security", "data-ai", "shared", "techniques"]


def extract_frontmatter(content: str) -> dict:
    """YAML frontmatter 파싱"""
    if not content.startswith("---"):
        return {}
    end = content.find("---", 3)
    if end == -1:
        return {}
    try:
        return yaml.safe_load(content[3:end]) or {}
    except Exception:
        return {}


def strip_frontmatter(content: str) -> str:
    """YAML frontmatter를 제거하고 순수 마크다운 본문만 반환"""
    if not content.startswith("---"):
        return content
    end = content.find("---", 3)
    if end == -1:
        return content
    return content[end + 3:].lstrip("\n")


def guess_origin(fname: str, fm: dict) -> str:
    if fm.get("origin"):
        return fm["origin"]
    if fname.startswith("aws-"):
        return "scoutflo"
    if fname.startswith("k8s-"):
        return "scoutflo"
    if fname.startswith("sentry-"):
        return "scoutflo"
    if fname.startswith("agent-"):
        return "voltagent"
    return "custom"


def guess_tags(fname: str, category: str) -> list:
    tags = [category]
    # AWS 서비스
    for svc in ["ec2", "rds", "lambda", "eks", "ecs", "s3", "alb", "elb",
                "cloudwatch", "route53", "iam", "guardduty", "waf", "dynamodb",
                "cloudfront", "vpc", "sg", "codepipeline", "cloudformation"]:
        if svc in fname.lower():
            tags.append(svc)
    # K8s
    for k in ["pod", "node", "ingress", "service", "rbac", "pvc", "namespace", "helm"]:
        if k in fname.lower():
            tags.append(f"k8s-{k}")
    # Sentry
    if "sentry" in fname.lower() or "kafka" in fname.lower():
        tags.append("sentry")
    if "kafka" in fname.lower():
        tags.append("kafka")
    if "redis" in fname.lower():
        tags.append("redis")
    return list(dict.fromkeys(tags))  # 순서 유지 중복 제거


def build_index():
    entries = []
    stats = {}

    for cat in CATEGORIES:
        cat_dir = ROOT / cat
        if not cat_dir.exists():
            continue
        files = sorted(cat_dir.glob("*.md"))
        stats[cat] = len(files)

        for f in files:
            content = f.read_text(encoding="utf-8")
            fm = extract_frontmatter(content)

            # 제목 추출 (첫 번째 H1 또는 H2)
            title_m = re.search(r'^#{1,2}\s+(.+)$', content, re.MULTILINE)
            title = title_m.group(1).strip() if title_m else f.stem.replace("-", " ").title()

            body = strip_frontmatter(content)

            entry = {
                "id": f"{cat[:3]}-{f.stem[:40]}",
                "file": f"{cat}/{f.name}",
                "title": title[:80],
                "category": cat,
                "origin": guess_origin(f.name, fm),
                "tags": guess_tags(f.name, cat),
                "content": body,
            }
            # frontmatter 보완
            for k in ["role", "difficulty", "source"]:
                if fm.get(k):
                    entry[k] = fm[k]

            entries.append(entry)

    total = sum(stats.values())

    result = {
        "_meta": {
            "version": "4.0",
            "generated": str(date.today()),
            "total": total,
            "stats": stats,
            "categories": CATEGORIES,
            "sources": [
                "VoltAgent/awesome-claude-code-subagents",
                "Scoutflo/Scoutflo-SRE-Playbooks",
                "shawnewallace/prompt-library",
                "custom (found.md)",
            ],
        },
        "prompts": entries,
    }

    # --- YAML 출력 (content 제외) ---
    yaml_entries = [{k: v for k, v in e.items() if k != "content"} for e in entries]
    yaml_result = {**result, "prompts": yaml_entries}
    out_path = ROOT / "prompts.meta.yaml"
    with open(out_path, "w", encoding="utf-8") as fh:
        yaml.dump(yaml_result, fh, allow_unicode=True, default_flow_style=False,
                  sort_keys=False, width=120)
    print(f"✅ prompts.meta.yaml 재생성 완료 — 총 {total}개 프롬프트")
    for cat, cnt in stats.items():
        print(f"   {cat}/: {cnt}개")

    # --- JSON 출력 (content 포함, 웹 뷰어용) ---
    web_dir = ROOT / "web"
    web_dir.mkdir(exist_ok=True)
    json_path = web_dir / "data.json"
    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump(result, fh, ensure_ascii=False, indent=2)
    print(f"✅ web/data.json 생성 완료 — {json_path.stat().st_size / 1024:.0f}KB")


if __name__ == "__main__":
    build_index()
