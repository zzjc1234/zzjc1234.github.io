"""Run with python3 checks.py; no third-party packages required."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = set()
        self.links = []
        self.headings = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            assert attrs["id"] not in self.ids, "Duplicate section ID"
            self.ids.add(attrs["id"])
        self.headings += tag == "h1"
        for attr in ("href", "src"):
            if attr in attrs:
                self.links.append(attrs[attr])
        if tag == "img":
            assert attrs.get("alt"), "Image needs descriptive alt text"


def check():
    root = Path(__file__).resolve().parent
    html = (root / "index.html").read_text()
    page = Page()
    page.feed(html)
    assert page.headings == 1, "Expected one primary heading"
    for link in page.links:
        url = urlsplit(link)
        if not url.scheme and not url.netloc:
            if url.path:
                assert (root / url.path.lstrip("/")).exists(), f"Missing asset: {link}"
            elif url.fragment:
                assert url.fragment in page.ids, f"Missing section: {link}"
    assert "NeurIPS 2026 · Poster" in html
    assert "EMNLP 2026 · Findings" in html
    assert "Third author" in html
    assert "John Doe" not in html and "example.com" not in html
    print("PASS: local links, section anchors, image alt text, and publication statuses")


if __name__ == "__main__":
    check()
