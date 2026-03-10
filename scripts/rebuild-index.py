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


def guess_tags(fname: str, category: str, fm: dict) -> list:
    """frontmatter tags 우선, 없으면 파일명에서 추론"""
    if fm.get("tags") and isinstance(fm["tags"], list):
        tags = list(fm["tags"])
        if category not in tags:
            tags.insert(0, category)
        return list(dict.fromkeys(tags))

    tags = [category]
    lower = fname.lower()

    # AWS 서비스
    for svc in ["ec2", "rds", "lambda", "eks", "ecs", "s3", "alb", "elb",
                "cloudwatch", "route53", "iam", "guardduty", "waf", "dynamodb",
                "cloudfront", "vpc", "sg", "codepipeline", "cloudformation",
                "fargate", "kms", "cognito", "shield", "sts", "acm"]:
        if svc in lower:
            tags.append(svc)

    # K8s 리소스
    for k in ["pod", "node", "ingress", "service", "rbac", "pvc", "namespace",
              "helm", "configmap", "secret", "deployment", "daemonset", "statefulset"]:
        if k in lower:
            tags.append(f"k8s-{k}")

    # 인프라 도구/영역
    for tool in ["kubernetes", "docker", "terraform", "terragrunt", "dns",
                 "storage", "networking", "monitoring", "database", "compute",
                 "autoscal", "cicd", "ci-cd", "pipeline"]:
        if tool in lower:
            tags.append(tool)

    # 앱 레이어
    if "sentry" in lower:
        tags.append("sentry")
    if "kafka" in lower:
        tags.append("kafka")
    if "redis" in lower:
        tags.append("redis")

    return list(dict.fromkeys(tags))


def suggest_tags(fname: str, category: str, content: str) -> list:
    """파일명, 카테고리, 본문 키워드 기반으로 태그 제안"""
    tags = set()
    lower = fname.lower()
    body_lower = content.lower()

    # 카테고리 자체
    tags.add(category)

    # AWS 서비스
    for svc in ["ec2", "rds", "lambda", "eks", "ecs", "s3", "alb", "elb",
                "cloudwatch", "route53", "iam", "guardduty", "waf", "dynamodb",
                "cloudfront", "vpc", "sg", "codepipeline", "cloudformation",
                "fargate", "kms", "cognito", "shield", "sts", "acm"]:
        if svc in lower or svc in body_lower[:2000]:
            tags.add(svc)

    # K8s 리소스
    for k in ["pod", "node", "ingress", "service", "rbac", "pvc", "namespace",
              "helm", "configmap", "secret", "deployment", "daemonset", "statefulset"]:
        if k in lower or k in body_lower[:2000]:
            tags.add(f"k8s-{k}")

    # 인프라 도구/영역
    for tool in ["kubernetes", "docker", "terraform", "terragrunt", "dns",
                 "storage", "networking", "monitoring", "database", "compute",
                 "autoscal", "cicd", "ci-cd", "pipeline", "security", "compliance",
                 "backup", "disaster-recovery", "cost", "observability", "performance",
                 "capacity", "scaling", "alerting", "logging"]:
        if tool in lower or tool in body_lower[:2000]:
            tags.add(tool)

    # 앱 레이어
    for app in ["sentry", "kafka", "redis", "nginx", "postgres", "mysql", "mongodb"]:
        if app in lower or app in body_lower[:2000]:
            tags.add(app)

    # 파일명 키워드 (하이픈 분리)
    parts = fname.replace(".md", "").split("-")
    for p in parts:
        if len(p) >= 4 and p not in ("proactive", "playbook", "agent", "prompt"):
            tags.add(p)

    return sorted(tags)


def audit_tags():
    """태그가 부족한 파일을 감사하고 리포트 출력"""
    low_tag_files = []   # 태그 ≤1
    warn_tag_files = []  # 태그 ≤2 (경고)

    for cat in CATEGORIES:
        cat_dir = ROOT / cat
        if not cat_dir.exists():
            continue
        for f in sorted(cat_dir.glob("*.md")):
            content = f.read_text(encoding="utf-8")
            fm = extract_frontmatter(content)
            tags = guess_tags(f.name, cat, fm)
            tag_count = len(tags)
            rel_path = f"{cat}/{f.name}"

            if tag_count <= 2:
                body = strip_frontmatter(content)
                suggested = suggest_tags(f.name, cat, body)
                # 기존 태그 제외
                new_suggestions = [t for t in suggested if t not in tags]

                entry = {
                    "path": rel_path,
                    "tag_count": tag_count,
                    "current_tags": tags,
                    "suggested_tags": new_suggestions,
                }

                if tag_count <= 1:
                    low_tag_files.append(entry)
                if tag_count <= 2:
                    warn_tag_files.append(entry)

    # --- 리포트 출력 ---
    print("=" * 70)
    print("📋 태그 감사 리포트 (--audit-tags)")
    print("=" * 70)

    if low_tag_files:
        print(f"\n🔴 태그 1개 이하 파일: {len(low_tag_files)}개")
        print("-" * 70)
        for e in low_tag_files:
            print(f"  [{e['tag_count']}개] {e['path']}")
            print(f"         현재: {', '.join(e['current_tags']) or '(없음)'}")
            if e["suggested_tags"]:
                print(f"         제안: {', '.join(e['suggested_tags'])}")
    else:
        print("\n✅ 태그 1개 이하 파일 없음")

    # 경고: 태그 2개 이하 (1개 이하 제외한 나머지)
    warn_only = [e for e in warn_tag_files if e["tag_count"] == 2]
    if warn_only:
        print(f"\n⚠️  태그 2개 이하 파일 (경고): {len(warn_only)}개")
        print("-" * 70)
        for e in warn_only:
            print(f"  [{e['tag_count']}개] {e['path']}")
            print(f"         현재: {', '.join(e['current_tags'])}")
            if e["suggested_tags"]:
                print(f"         제안: {', '.join(e['suggested_tags'])}")

    print(f"\n{'=' * 70}")
    print(f"📊 요약: 태그 ≤1 = {len(low_tag_files)}개, 태그 ≤2 경고 = {len(warn_tag_files)}개")
    print("=" * 70)


def _title_from_filename(stem: str) -> str:
    """파일명에서 의미 있는 제목 생성.
    agent-debugger        → Agent: Debugger
    agent-sre-engineer    → Agent: SRE Engineer
    k8s-01-Control-Plane-Timeout → K8s Control Plane Timeout
    aws-01-Compute-High-CPU-Utilization-EC2 → Compute: High CPU Utilization (EC2)
    """
    # agent-* 패턴
    if stem.startswith("agent-"):
        role = stem[6:].replace("-", " ").title()
        return f"Agent: {role}"

    # aws-NN-Section-Name 패턴
    m = re.match(r"aws-\d+-([A-Za-z]+)-(.+)", stem)
    if m:
        section = m.group(1)
        rest = m.group(2).replace("-", " ")
        return f"{section}: {rest}"

    # k8s-NN-Section-Name 패턴
    m = re.match(r"k8s-\d+-([A-Za-z-]+)-(.+)", stem)
    if m:
        section = m.group(1).replace("-", " ")
        rest = m.group(2).replace("-", " ")
        return f"K8s {section}: {rest}"

    # sentry-ErrorType-Name 패턴
    if stem.startswith("sentry-"):
        rest = stem[7:].replace("-", " ")
        return f"Sentry: {rest}"

    # 기본 fallback
    return stem.replace("-", " ").replace("_", " ").title()


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

            body = strip_frontmatter(content)

            # 제목 추출: 본문(frontmatter 제거 후)에서 첫 H1만 탐색
            # H1이 없으면 파일명에서 의미 있는 제목 생성
            title_m = re.search(r'^#\s+(.+)$', body, re.MULTILINE)
            title = title_m.group(1).strip() if title_m else _title_from_filename(f.stem)

            entry = {
                "id": f"{cat[:3]}-{f.stem[:40]}",
                "file": f"{cat}/{f.name}",
                "title": title[:80],
                "category": cat,
                "origin": guess_origin(f.name, fm),
                "tags": guess_tags(f.name, cat, fm),
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
    import argparse
    parser = argparse.ArgumentParser(description="프롬프트 라이브러리 인덱스 관리")
    parser.add_argument("--audit-tags", action="store_true",
                        help="태그 1개 이하 파일 목록 출력 (제안 태그 포함)")
    args = parser.parse_args()

    if args.audit_tags:
        audit_tags()
    else:
        build_index()
