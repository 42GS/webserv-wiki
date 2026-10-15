"""Cut out one element by id and wrap it in <div id="content"> so that
nginx2md.py / verify_md.py can process it. Used for pages whose main text
sits in a uniquely identified element (e.g. php.net manual pages: <div>,
peps.python.org: <section id="pep-content">).

Usage: python3 -I tools/extract_div.py <page.html> <element-id> [tag] > wrapped.html

tag defaults to "div". The element is taken from its opening tag to the
matching closing tag (nesting of the same tag is counted). Everything else on the page (navigation,
user-contributed notes, footer) is excluded.
"""
import sys
import re


def main():
    s = open(sys.argv[1], encoding="utf-8").read()
    elem_id = sys.argv[2]
    tag = sys.argv[3] if len(sys.argv) > 3 else "div"
    m = re.search(r'<%s\b[^>]*\bid="%s"[^>]*>' % (re.escape(tag), re.escape(elem_id)), s)
    if not m:
        sys.exit("element id not found: %s" % elem_id)
    depth, end = 0, None
    for t in re.finditer(r"<(/?)%s\b[^>]*>" % re.escape(tag), s[m.start():]):
        depth += -1 if t.group(1) else 1
        if depth == 0:
            end = m.start() + t.end()
            break
    if end is None:
        sys.exit("closing </%s> not found for: %s" % (tag, elem_id))
    sys.stdout.write('<html><body><div id="content">' + s[m.start():end] + "</div></body></html>\n")


if __name__ == "__main__":
    main()
