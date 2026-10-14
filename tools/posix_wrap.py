"""Wrap the body of a pubs.opengroup.org page in <div id="content"> so that
nginx2md.py / verify_md.py can process it.

Usage: python3 -I tools/posix_wrap.py <page.html> > wrapped.html
Body = everything after the first NAVHEADER div up to the
"return to top of page" link (footer and bottom navigation excluded).
"""
import sys

START_MARK = '<hr align="left" width="100%"></div>'
END_MARK = '<a href="#top"><span class="topOfPage">return to top of page</span></a>'


def main():
    s = open(sys.argv[1], encoding="utf-8").read()
    start = s.index(START_MARK) + len(START_MARK)
    end = s.index(END_MARK, start)
    # The page has no nested <div id="content">; the only inner divs are
    # "box" notes, which the converter handles as nested divs.
    sys.stdout.write('<html><body><div id="content">' + s[start:end] + "</div></body></html>\n")


if __name__ == "__main__":
    main()
