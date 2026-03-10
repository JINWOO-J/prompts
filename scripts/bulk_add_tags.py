#!/usr/bin/env python3
"""
Frontmatter 태그 일괄 보강 스크립트.
태그가 3개 미만인 파일에 suggest_tags() 기반으로 태그를 추가한다.

실행: python3 scripts/bulk_add_tags.py [--dry-run]
"""

import re
import yaml
from pathlib import Path

ROOT = Path(__file__).parent.parent
CATEGORIES = [
    "rca", "incident-response", "application", "infrastructure",
    "security", "data-ai", "shared", "techniques",
]

# suggest_tags()에서 사용하는 키워드 사전 (rebuild-index.py와 동일)
AWS_SERVICES = [
    "ec2", "rds", "lambda", "eks", "ecs", "s3", "alb", "elb",
    "cloudwatch", "route53", "iam", "guardduty", "waf", "dynamodb",
    "cloudfront", "vpc", "sg", "codepipeline", "cloudformation",
    "fargate", "kms", "cognito", "shield", "sts", "acm",
]
K8S_RESOURCES = [
    "pod", "node", "ingress", "service", "rbac", "pvc", "namespace",
    "helm", "configmap", "secret", "deployment", "daemonset", "statefulset",
]
INFRA_TOOLS = [
    "kubernetes", "docker", "terraform", "terragrunt", "dns",
    "storage", "networking", "monitoring", "database", "compute",
    "autoscal", "cicd", "ci-cd", "pipeline", "security", "compliance",
    "backup", "disaster-recovery", "cost", "observability", "performance",
    "capacity", "scaling", "alerting", "logging",
]
APP_TOOLS = ["sentry", "kafka", "redis", "nginx", "postgres", "mysql", "mongodb"]

# 태그로 부적절한 노이즈 단어 (파일명 분리 시 제외)
NOISE_WORDS = {
    "proactive", "playbook", "agent", "prompt", "md", "the", "and", "for",
    "not", "error", "application", "instructions",
}


def suggest_tags(fname: str, category: str, content: str) -> list[str]:
    """파일명, 카테고리, 본문 키워드 기반으로 태그 제안 (rebuild-index.py 동일 로직)"""
    tags = {category}
    lower = fname.lower()
    body_lower = content.lower()[:2000]

    for svc in AWS_SERVICES:
        if svc in lower or svc in body_lower:
            tags.add(svc)

    for k in K8S_RESOURCES:
        if k in lower or k in body_lower:
            tags.add(f"k8s-{k}")

    for tool in INFRA_TOOLS:
        if tool in lower or tool in body_lower:
            tags.add(tool)

    for app in APP_TOOLS:
        if app in lower or app in body_lower:
            tags.add(app)

    # 파일명 키워드 (하이픈 분리, 4글자 이상, 노이즈 제외)
    parts = fname.replace(".md", "").split("-")
    for p in parts:
        if len(p) >= 4 and p.lower() not in NOISE_WORDS:
            tags.add(p.lower())

    return sorted(tags)


def extract_frontmatter(content: str) -> tuple[dict, str]:
    """Frontmatter dict와 본문을 분리하여 반환"""
    if not content.startswith("---"):
        return {}, content
    end = content.find("---", 3)
    if end == -1:
        return {}, content
    try:
        fm = yaml.safe_load(content[3:end]) or {}
    except Exception:
        fm = {}
    body = content[end + 3:]
    return fm, body


def rebuild_frontmatter(fm: dict, body: str) -> str:
    """Frontmatter dict + 본문을 다시 합쳐서 파일 내용 생성"""
    fm_str = yaml.dump(fm, allow_unicode=True, default_flow_style=False,
                       sort_keys=False, width=120)
    return f"---\n{fm_str}---{body}"


def process_file(filepath: Path, category: str, dry_run: bool) -> bool:
    """파일 하나를 처리. 변경했으면 True 반환."""
    content = filepath.read_text(encoding="utf-8")
    fm, body = extract_frontmatter(content)

    existing_tags = fm.get("tags", [])
    if not isinstance(existing_tags, list):
        existing_tags = []

    if len(existing_tags) >= 3:
        return False

    # 본문에서 태그 제안
    body_text = body.lstrip("\n")
    suggested = suggest_tags(filepath.name, category, body_text)

    # 기존 태그 + 제안 태그 병합 (기존 우선)
    merged = list(existing_tags)
    for t in suggested:
        if t not in merged:
            merged.append(t)

    # 최소 3개 보장
    if len(merged) < 3:
        return False  # 제안할 태그가 부족한 경우 (거의 없음)

    fm["tags"] = merged
    new_content = rebuild_frontmatter(fm, body)

    if dry_run:
        print(f"  [DRY] {category}/{filepath.name}: {len(existing_tags)} → {len(merged)} tags")
    else:
        filepath.write_text(new_content, encoding="utf-8")
        print(f"  [OK]  {category}/{filepath.name}: {len(existing_tags)} → {len(merged)} tags")

    return True


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Frontmatter 태그 일괄 보강")
    parser.add_argument("--dry-run", action="store_true", help="실제 파일 수정 없이 미리보기")
    args = parser.parse_args()

    updated = 0
    skipped = 0

    for cat in CATEGORIES:
        cat_dir = ROOT / cat
        if not cat_dir.exists():
            continue
        for f in sorted(cat_dir.glob("*.md")):
            if process_file(f, cat, args.dry_run):
                updated += 1
            else:
                skipped += 1

    mode = "DRY-RUN" if args.dry_run else "COMPLETE"
    print(f"\n{'=' * 50}")
    print(f"📊 {mode}: 수정 {updated}개, 스킵 {skipped}개 (이미 3개 이상)")
    print("=" * 50)


if __name__ == "__main__":
    main()
