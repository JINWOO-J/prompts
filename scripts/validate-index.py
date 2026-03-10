#!/usr/bin/env python3
"""
prompts.meta.yaml 스키마 검증 스크립트.
실행: python3 scripts/validate-index.py
"""

import sys
import yaml
from pathlib import Path

ROOT = Path(__file__).parent.parent

REQUIRED_FIELDS = ["id", "file", "title", "category", "origin", "tags"]

ALLOWED_CATEGORIES = [
    "rca", "incident-response", "application", "infrastructure",
    "security", "data-ai", "shared", "techniques",
]

ALLOWED_ORIGINS = ["custom", "scoutflo", "voltagent", "shawnewallace", "extracted"]


def validate_index():
    meta_path = ROOT / "prompts.meta.yaml"
    if not meta_path.exists():
        print(f"❌ prompts.meta.yaml 파일을 찾을 수 없습니다: {meta_path}")
        return 1

    with open(meta_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    prompts = data.get("prompts", [])
    if not prompts:
        print("⚠️  prompts 배열이 비어 있습니다.")
        return 1

    errors = []

    for i, entry in enumerate(prompts):
        entry_id = entry.get("id", f"(index {i})")

        # 필수 필드 존재 여부
        for field in REQUIRED_FIELDS:
            if field not in entry or entry[field] is None:
                errors.append(f"[{entry_id}] 필수 필드 누락: {field}")

        # category 허용값 검증
        category = entry.get("category")
        if category and category not in ALLOWED_CATEGORIES:
            errors.append(
                f"[{entry_id}] 허용되지 않은 category: '{category}' "
                f"(허용: {', '.join(ALLOWED_CATEGORIES)})"
            )

        # origin 허용값 검증
        origin = entry.get("origin")
        if origin and origin not in ALLOWED_ORIGINS:
            errors.append(
                f"[{entry_id}] 허용되지 않은 origin: '{origin}' "
                f"(허용: {', '.join(ALLOWED_ORIGINS)})"
            )

        # file 경로 실존 여부
        file_path = entry.get("file")
        if file_path and not (ROOT / file_path).exists():
            errors.append(f"[{entry_id}] 파일 없음: {file_path}")

    if errors:
        print("=" * 70)
        print(f"❌ 검증 실패 — {len(errors)}건의 오류 발견")
        print("=" * 70)
        for err in errors:
            print(f"  • {err}")
        print("=" * 70)
        return 1

    print(f"✅ 검증 통과 — {len(prompts)}개 엔트리 모두 정상")
    return 0


if __name__ == "__main__":
    sys.exit(validate_index())
