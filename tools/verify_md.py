"""Verify that a converted markdown file keeps the wording of its source HTML.

Usage: python3 -I tools/verify_md.py <source.html> <converted.md>

The HTML text is extracted independently of the converter: everything
inside div#content, block tags replaced by spaces and inline tags removed. Markdown syntax and the
provenance header ("> " lines) are stripped from the .md.

Two checks, both must pass (exit code 0):
  1. Character check: the two texts with all whitespace removed are identical.
  2. Word check: the word lists are identical. On the HTML side block tags
     count as whitespace and inline tags are removed, so the list matches what
     a browser shows. This catches spaces the converter dropped or added
     between words, which check 1 cannot see.
"""
import sys
import re
import html

BLOCK_TAGS = ("p|div|br|hr|li|ul|ol|dl|dt|dd|h[1-6]|pre|blockquote|"
              "table|thead|tbody|tr|td|th|center|body|html|head|title|meta|link")


def html_words(path):
    s = open(path, encoding="utf-8").read()
    start = s.index('<div id="content">')
    # div#content is closed by the matching </div>; count nesting.
    depth, end = 0, len(s)
    for m in re.finditer(r"<(/?)div\b", s[start:]):
        depth += -1 if m.group(1) else 1
        if depth == 0:
            end = start + m.start()
            break
    s = s[start:end]
    s = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", s)
    # Block-level tags separate words like whitespace does; inline tags
    # (code, a, i, b, span, ...) do not. This keeps the HTML word list equal
    # to what a browser shows, so dropped spaces in the md are detectable.
    s = re.sub(r"(?i)</?(%s)\b[^>]*>" % BLOCK_TAGS, " ", s)
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s)
    return s.split()


def md_words(path):
    lines = open(path, encoding="utf-8").read().split("\n")
    lines = [l for l in lines if not l.startswith("> ")]          # provenance header
    s = "\n".join(lines)
    s = re.sub(r'<a id="[^"]*"></a>', " ", s)
    s = re.sub(r"(?m)^```$", " ", s)          # code fence lines
    s = re.sub(r"(?m)^#+ ", " ", s)
    s = re.sub(r"(?m)^- ", " ", s)
    # Inline markers added by the converter are not part of the text.
    s = s.replace("**", "").replace("`", "")
    return s.split()


def check_chars(a, b):
    x, y = "".join(a), "".join(b)
    print("char check: html %d chars, md %d chars" % (len(x), len(y)))
    if x == y:
        return True
    n = next((i for i in range(min(len(x), len(y))) if x[i] != y[i]), min(len(x), len(y)))
    print("  first difference at char %d" % n)
    print("  html: %r" % x[max(0, n - 60):n + 60])
    print("  md  : %r" % y[max(0, n - 60):n + 60])
    return False


def check_words(a, b):
    """The md word list must equal the browser-visible HTML word list."""
    if a == b:
        print("word check: %d words identical" % len(a))
        return True
    n = next((i for i in range(min(len(a), len(b))) if a[i] != b[i]), min(len(a), len(b)))
    print("word check: FAIL at word %d (html %d words, md %d words)" % (n, len(a), len(b)))
    print("  html: %r" % " ".join(a[max(0, n - 6):n + 6]))
    print("  md  : %r" % " ".join(b[max(0, n - 6):n + 6]))
    return False


def main():
    a = html_words(sys.argv[1])
    b = md_words(sys.argv[2])
    ok_chars = check_chars(a, b)
    ok_words = check_words(a, b)
    print("RESULT:", "PASS" if ok_chars and ok_words else "FAIL")
    sys.exit(0 if ok_chars and ok_words else 1)


if __name__ == "__main__":
    main()
