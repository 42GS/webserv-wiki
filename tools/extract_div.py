"""Cut out one element by id and wrap it in <div id="content"> so that
nginx2md.py / verify_md.py can process it. Used for pages whose main text
sits in a uniquely identified <div> (e.g. php.net manual pages).

Usage: python3 -I tools/extract_div.py <page.html> <element-id> > wrapped.html

The element is taken from its opening tag to the matching closing </div>
(nesting of <div> is counted). Everything else on the page (navigation,
user-contributed notes, footer) is excluded.
"""
import sys
import re


def main():
    s = open(sys.argv[1], encoding="utf-8").read()
    elem_id = sys.argv[2]
    m = re.search(r'<div\b[^>]*\bid="%s"[^>]*>' % re.escape(elem_id), s)
    if not m:
        sys.exit("element id not found: %s" % elem_id)
    depth, end = 0, None
    for t in re.finditer(r"<(/?)div\b[^>]*>", s[m.start():]):
        depth += -1 if t.group(1) else 1
        if depth == 0:
            end = m.start() + t.end()
            break
    if end is None:
        sys.exit("closing </div> not found for: %s" % elem_id)
    sys.stdout.write('<html><body><div id="content">' + s[m.start():end] + "</div></body></html>\n")


if __name__ == "__main__":
    main()
