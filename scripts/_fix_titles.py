#!/usr/bin/env python3
"""rebuild-index.py의 title 추출 로직 수정 + 중복 body 제거"""
import re

path = "scripts/rebuild-index.py"
with open(path, "r") as f:
    src = f.read()

# 1. _title_from_filename 헬퍼 함수 추가 (build_index 바로 위)
helper = '''
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
    m = re.match(r"aws-\\d+-([A-Za-z]+)-(.+)", stem)
    if m:
        section = m.group(1)
        rest = m.group(2).replace("-", " ")
        return f"{section}: {rest}"

    # k8s-NN-Section-Name 패턴
    m = re.match(r"k8s-\\d+-([A-Za-z-]+)-(.+)", stem)
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

'''

# build_index 함수 앞에 헬퍼 삽입
src = src.replace("\ndef build_index():", helper + "\ndef build_index():")

# 2. title 추출 로직 수정: body에서 H1만 찾고, 없으면 _title_from_filename 사용
# 기존: body 선언 → content에서 H1/H2 검색 → body 중복 선언
old_block = """            body = strip_frontmatter(content)

            # 제목 추출: 본문(frontmatter 제거 후)에서 첫 H1만 탐색
            title_m = re.search(r'^#\\s+(.+)$', content, re.MULTILINE)
            title = title_m.group(1).strip() if title_m else f.stem.replace("-", " ").title()

            body = strip_frontmatter(content)"""

new_block = """            body = strip_frontmatter(content)

            # 제목 추출: 본문(frontmatter 제거 후)에서 첫 H1만 탐색
            # H1이 없으면 파일명에서 의미 있는 제목 생성
            title_m = re.search(r'^#\\s+(.+)$', body, re.MULTILINE)
            title = title_m.group(1).strip() if title_m else _title_from_filename(f.stem)"""

if old_block in src:
    src = src.replace(old_block, new_block)
    print("OK: title 추출 로직 수정 완료")
else:
    print("WARN: old_block not found, trying line-by-line approach")
    # 라인 단위로 수정
    lines = src.split("\n")
    new_lines = []
    skip_next_body = False
    for i, line in enumerate(lines):
        # content → body 로 변경
        if "re.search(r'^#\\s+(.+)$', content, re.MULTILINE)" in line:
            line = line.replace("content, re.MULTILINE)", "body, re.MULTILINE)")
            new_lines.append(line)
            continue
        # f.stem.replace → _title_from_filename
        if 'f.stem.replace("-", " ").title()' in line:
            line = line.replace('f.stem.replace("-", " ").title()', '_title_from_filename(f.stem)')
            new_lines.append(line)
            continue
        # 중복 body = strip_frontmatter(content) 제거
        if skip_next_body and "body = strip_frontmatter(content)" in line:
            skip_next_body = False
            continue
        if "title_m = re.search" in line and "body" in line:
            skip_next_body = True
        new_lines.append(line)
    src = "\n".join(new_lines)
    print("OK: line-by-line 수정 완료")

with open(path, "w") as f:
    f.write(src)

print("Done!")
