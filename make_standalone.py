#!/usr/bin/env python3
"""
make_standalone.py — bundle index.html, the vendored D3, and every data/*.json
into ONE self-contained HTML file that opens from file:// (double-click), so
the dashboards can be sent as a single attachment.

This is a share artifact, not a build step: the site itself stays a plain
static page served from the repo root. Re-run this after any change you want
reflected in the shared copy.

Output: two-listeners.html in the repo root (gitignored).
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent
DATA_FILES = ["meta", "monthly", "heatmap", "daylength", "headlines", "artists"]
OUT = ROOT / "two-listeners.html"


def main() -> None:
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    d3 = (ROOT / "lib" / "d3.v7.min.js").read_text(encoding="utf-8")
    # a literal "</script" inside inlined JS would terminate the tag early
    assert "</script" not in d3, "d3 source cannot be inlined verbatim"

    embedded = {name: json.loads((ROOT / "data" / f"{name}.json")
                                 .read_text(encoding="utf-8"))
                for name in DATA_FILES}
    payload = json.dumps(embedded, ensure_ascii=False)
    payload = payload.replace("</", "<\\/")  # same early-termination guard

    tag = '<script src="lib/d3.v7.min.js"></script>'
    assert tag in html, "expected the vendored d3 script tag in index.html"
    html = html.replace(
        tag,
        "<script>\n" + d3 + "\n</script>\n"
        "<script>const EMBEDDED_DATA = " + payload + ";</script>")

    # swap every d3.json fetch for its embedded copy
    html, n = re.subn(r'd3\.json\("data/(\w+)\.json"\)',
                      lambda m: f'Promise.resolve(EMBEDDED_DATA["{m.group(1)}"])',
                      html)
    assert n == len(DATA_FILES), f"expected {len(DATA_FILES)} d3.json calls, found {n}"

    OUT.write_text(html, encoding="utf-8")
    print(f"wrote {OUT} ({OUT.stat().st_size / 1024:.0f} KB) — "
          "self-contained, opens from file://")


if __name__ == "__main__":
    main()
