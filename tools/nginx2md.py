"""Convert an nginx.org documentation page (div#content) to markdown.

Usage: python3 -I tools/nginx2md.py <input.html> <source-url> <retrieved-date> > out.md
Only structure is converted; wording is kept as-is so the result can be
verified against the HTML text.
"""
import sys
import re
from html.parser import HTMLParser


class Converter(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.depth_in_content = 0   # div nesting depth inside div#content
        self.out = []
        self.buf = []
        self.in_pre = False
        self.in_th = False
        self.list_depth = 0
        self.heading = None
        self.code_depth = 0

    # --- helpers -------------------------------------------------------
    def flush(self, prefix=""):
        text = "".join(self.buf)
        self.buf = []
        text = re.sub(r"[ \t\r\n]+", " ", text).strip()
        if text:
            self.out.append(prefix + text)
            self.out.append("")

    def active(self):
        return self.depth_in_content > 0

    # --- parser callbacks ---------------------------------------------
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "div":
            if self.depth_in_content:
                self.depth_in_content += 1
            elif attrs.get("id") == "content":
                self.depth_in_content = 1
            return
        if not self.active():
            return
        if tag in ("h1", "h2", "h3", "h4"):
            self.flush()
            self.heading = tag
        elif tag == "a" and "name" in attrs and not attrs.get("href"):
            self.flush()
            self.out.append('<a id="%s"></a>' % attrs["name"])
            self.out.append("")
        elif tag == "pre":
            self.flush()
            self.in_pre = True
        elif tag in ("ul", "ol", "dl"):
            self.flush()
            self.list_depth += 1
        elif tag in ("li", "dt", "dd"):
            self.flush()
        elif tag in ("p", "blockquote", "table", "tr"):
            self.flush()
        elif tag == "th":
            self.flush()
            self.in_th = True
        elif tag == "td":
            pass
        elif tag == "br":
            self.buf.append(" ")
        elif tag == "code" and not self.in_pre:
            # Only the outermost <code> becomes an inline code span.
            if self.code_depth == 0:
                self.buf.append("`")
            self.code_depth += 1

    def handle_endtag(self, tag):
        if tag == "div":
            if self.depth_in_content:
                self.flush()
                self.depth_in_content -= 1
            return
        if not self.active():
            return
        if tag in ("h1", "h2", "h3", "h4"):
            level = {"h1": "# ", "h2": "## ", "h3": "### ", "h4": "#### "}[tag]
            self.flush(level)
            self.heading = None
        elif tag == "pre":
            code = "".join(self.buf).strip("\n")
            self.buf = []
            self.out.append("```")
            self.out.append(code)
            self.out.append("```")
            self.out.append("")
            self.in_pre = False
        elif tag in ("ul", "ol", "dl"):
            self.flush("- ")
            self.list_depth -= 1
        elif tag in ("li", "dt", "dd"):
            self.flush("- ")
        elif tag == "th":
            text = re.sub(r"\s+", " ", "".join(self.buf)).strip()
            self.buf = ["**%s** " % text]
            self.in_th = False
        elif tag == "tr":
            self.flush()
        elif tag in ("p", "blockquote", "table"):
            self.flush()
        elif tag == "code" and not self.in_pre:
            self.code_depth -= 1
            if self.code_depth == 0:
                self.buf.append("`")

    def handle_data(self, data):
        if self.active():
            self.buf.append(data)


def main():
    path, url, date = sys.argv[1], sys.argv[2], sys.argv[3]
    conv = Converter()
    with open(path, encoding="utf-8") as f:
        conv.feed(f.read())
    conv.flush()
    body = "\n".join(conv.out)
    body = re.sub(r"(?<!`)``(?!`)", "", body)   # empty inline code spans
    body = re.sub(r"\n{3,}", "\n\n", body).strip() + "\n"
    header = (
        "> Source: <%s>\n"
        "> Retrieved: %s. Original HTML: kept next to this file as `.source.html`.\n"
        "> Converted to markdown by text extraction of `div#content`; wording is unchanged,\n"
        "> whitespace, list markup and code fences were normalized.\n\n" % (url, date)
    )
    sys.stdout.write(header + body)


if __name__ == "__main__":
    main()
