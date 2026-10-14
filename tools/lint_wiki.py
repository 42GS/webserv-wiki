"""Mechanical lint for the wiki. Run from the repository root.

Usage: python3 -I tools/lint_wiki.py

Checks:
  - broken [[wikilinks]]
  - citations raw/<file>:<a>[-<b>] that fall outside the file or are reversed
  - markdown tables whose rows have a different cell count than the header
  - frontmatter `sources` missing a raw file that the page cites
  - orphan pages (no inbound [[link]]), except log and index
Exit code 1 if any issue is found.
"""
import glob
import os
import re
import sys

CITE = re.compile(r"(raw/[\w.-]+\.(?:md|txt|pod|in)):(\d+)(?:-(\d+))?")
SKIP_FRONTMATTER = {"wiki/log.md", "wiki/index.md", "wiki/source-wishlist.md"}


def table_issues(lines):
    in_code, head = False, None
    for i, line in enumerate(lines, 1):
        if line.startswith("```"):
            in_code = not in_code
        text = re.sub(r"^>\s?", "", line)
        if in_code or not text.startswith("|"):
            head = None
            continue
        cells = len(re.split(r"(?<!\\)\|", text.strip())) - 2
        if head is None:
            head = cells
        elif cells != head:
            yield i, cells, head


def main():
    pages = sorted(glob.glob("wiki/**/*.md", recursive=True))
    names = {p[len("wiki/"):-len(".md")] for p in pages}
    line_counts = {}
    issues = []
    for p in pages:
        s = open(p, encoding="utf-8").read()
        for link in re.findall(r"\[\[([^\]|#]+)", s):
            if link not in names:
                issues.append((p, "broken link", link))
        for f, a, b in CITE.findall(s):
            if not os.path.exists(f):
                issues.append((p, "missing raw file", f))
                continue
            if f not in line_counts:
                line_counts[f] = sum(1 for _ in open(f, encoding="utf-8"))
            start, end = int(a), int(b or a)
            if start < 1 or end < start or end > line_counts[f]:
                issues.append((p, "citation out of range", "%s:%s-%s" % (f, a, b)))
        for i, cells, head in table_issues(s.split("\n")):
            issues.append((p, "table columns", "line %d: %d vs header %d" % (i, cells, head)))
        m = re.search(r"^sources: \[(.*)\]", s, re.M)
        if m and p not in SKIP_FRONTMATTER:
            listed = {x.strip() for x in m.group(1).split(",")}
            cited = {f for f, _, _ in CITE.findall(s)}
            missing = sorted(cited - listed)
            if missing:
                issues.append((p, "frontmatter sources missing", ", ".join(missing)))
    alltext = "".join(open(p, encoding="utf-8").read() for p in pages)
    for n in sorted(names):
        if n not in ("log", "index") and "[[%s]]" % n not in alltext:
            issues.append((n, "orphan page", ""))
    for issue in issues:
        print(" | ".join(issue))
    print("pages: %d, issues: %d" % (len(pages), len(issues)))
    sys.exit(1 if issues else 0)


if __name__ == "__main__":
    main()
