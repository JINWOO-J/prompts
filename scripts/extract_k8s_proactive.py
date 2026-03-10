#!/usr/bin/env python3
"""Extract 13-Proactive K8s playbooks from Scoutflo source into infrastructure/ folder.

Walks .tmp-sources/Scoutflo-SRE-Playbooks/K8s Playbooks/13-Proactive/ subdirectories,
converts filenames to k8s-13-Proactive-{subcategory}-{original}.md pattern,
and prepends standard Frontmatter.
"""

import os
import re
from pathlib import Path

SOURCE_ROOT = Path(".tmp-sources/Scoutflo-SRE-Playbooks/K8s Playbooks/13-Proactive")
DEST_DIR = Path("infrastructure")

FRONTMATTER_TEMPLATE = """---
category: infrastructure
source: "[Scoutflo/Scoutflo-SRE-Playbooks](https://github.com/Scoutflo/Scoutflo-SRE-Playbooks/blob/master/K8s%20Playbooks/13-Proactive/{encoded_subdir}/{encoded_filename})"
role: SRE / K8s Proactive Operations
origin: scoutflo
---

"""


def strip_numeric_prefix(name: str) -> str:
    """Strip leading numeric prefix like '01-' from subcategory name."""
    return re.sub(r"^\d+-", "", name)


def build_github_path(subdir_name: str, filename: str) -> tuple[str, str]:
    """URL-encode directory and filename for GitHub source link."""
    encoded_subdir = subdir_name.replace(" ", "%20")
    encoded_filename = filename.replace(" ", "%20")
    return encoded_subdir, encoded_filename


def extract_files():
    if not SOURCE_ROOT.exists():
        print(f"ERROR: Source directory not found: {SOURCE_ROOT}")
        return 0

    DEST_DIR.mkdir(exist_ok=True)
    count = 0

    for subdir in sorted(SOURCE_ROOT.iterdir()):
        if not subdir.is_dir():
            continue

        subcategory = strip_numeric_prefix(subdir.name)

        for src_file in sorted(subdir.glob("*.md")):
            original_name = src_file.stem  # e.g. "Baseline-Comparison-K8s"
            dest_name = f"k8s-13-Proactive-{subcategory}-{original_name}.md"
            dest_path = DEST_DIR / dest_name

            content = src_file.read_text(encoding="utf-8")

            encoded_subdir, encoded_filename = build_github_path(subdir.name, src_file.name)
            frontmatter = FRONTMATTER_TEMPLATE.format(
                encoded_subdir=encoded_subdir,
                encoded_filename=encoded_filename,
            )

            dest_path.write_text(frontmatter + content, encoding="utf-8")
            count += 1
            print(f"  [{count:2d}] {dest_name}")

    return count


if __name__ == "__main__":
    print(f"Extracting 13-Proactive playbooks from {SOURCE_ROOT}")
    print(f"Destination: {DEST_DIR}/\n")
    total = extract_files()
    print(f"\nDone. Extracted {total} files.")
