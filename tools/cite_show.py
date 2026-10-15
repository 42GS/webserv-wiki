"""Show the raw text behind every citation added since the last commit, so each
new claim can be compared with its source before committing.

Usage: python3 -I tools/cite_show.py            (run from the repository root)
       python3 -I tools/cite_show.py --all PAGE...

Without arguments, looks at lines added to wiki/ in the working tree and index
(git diff HEAD) and at untracked wiki/ files. With --all, looks at every line of
the given pages instead, for auditing citations that are already committed.
For each citation raw/<file>:<a>[-<b>] it prints the page, the text before the
citation in that line, and the cited raw lines (ranges longer than MAX_LINES,
or MAX_LINES_ALL with --all, show the first and last lines only).
"""
import re
import subprocess
import sys

CITE = re.compile(r"(raw/[\w.-]+\.(?:md|txt|pod|in)):(\d+)(?:-(\d+))?")
MAX_LINES = 6
MAX_LINES_ALL = 30
CONTEXT = 90


def git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True, check=True).stdout


def added_lines():
    """Yield (page, text) for each line added in wiki/ since HEAD."""
    page = None
    for line in git("diff", "HEAD", "-U0", "--", "wiki/").splitlines():
        if line.startswith("+++ "):
            page = line[len("+++ b/"):]
        elif line.startswith("+") and page:
            yield page, line[1:]
    for page in git("ls-files", "--others", "--exclude-standard", "--", "wiki/").splitlines():
        for text in open(page, encoding="utf-8"):
            yield page, text.rstrip("\n")


def all_lines(pages):
    """Yield (page, text) for every line of the given pages."""
    for page in pages:
        for text in open(page, encoding="utf-8"):
            yield page, text.rstrip("\n")


def cited_text(path, start, end, cache, max_lines):
    if path not in cache:
        try:
            cache[path] = [l.rstrip("\n") for l in open(path, encoding="utf-8")]
        except FileNotFoundError:
            cache[path] = None
    lines = cache[path]
    if lines is None:
        return ["!! file not found"]
    if start < 1 or end < start or end > len(lines):
        return ["!! out of range (file has %d lines)" % len(lines)]
    numbered = ["%6d  %s" % (n, lines[n - 1]) for n in range(start, end + 1)]
    if len(numbered) > max_lines:
        numbered = numbered[:2] + ["        ..."] + numbered[-2:]
    return numbered


def main():
    if sys.argv[1:2] == ["--all"]:
        lines, max_lines = all_lines(sys.argv[2:]), MAX_LINES_ALL
    else:
        lines, max_lines = added_lines(), MAX_LINES
    cache, count = {}, 0
    for page, text in lines:
        for m in CITE.finditer(text):
            path, a, b = m.group(1), int(m.group(2)), int(m.group(3) or m.group(2))
            before = text[:m.start()].rstrip(" (")
            print("== %s  %s" % (page, m.group(0)))
            print("   claim: ...%s" % before[-CONTEXT:])
            for row in cited_text(path, a, b, cache, max_lines):
                print("   " + row)
            print()
            count += 1
    print("citations: %d" % count)


if __name__ == "__main__":
    main()
