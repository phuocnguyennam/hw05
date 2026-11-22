# -*- coding: utf-8 -*-
"""Export HW05_23120073/Report.md and AI Audit Report.md to PDF."""
import os
import re
import sys
import markdown
from playwright.sync_api import sync_playwright

sys.path.insert(0, r"C:\Users\PC\eshop-sut\.agents\skills\ai-audit-extractor\scripts")
from export_pdfs import CSS_STYLE

HW_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def md_to_pdf(md_name: str, pdf_name: str, landscape: bool = True):
    md_path = os.path.join(HW_DIR, md_name)
    pdf_path = os.path.join(HW_DIR, pdf_name)
    with open(md_path, "r", encoding="utf-8") as f:
        text = f.read()

    text = re.sub(
        r"```mermaid\s*\n(.*?)```",
        lambda m: f'<div class="mermaid">\n{m.group(1)}\n</div>',
        text,
        flags=re.S,
    )
    html_body = markdown.markdown(
        text, extensions=["tables", "fenced_code", "sane_lists"]
    )
    full_html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="utf-8">
<style>{CSS_STYLE}
.mermaid {{ text-align: center; margin: 14px 0; }}
</style>
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<script>mermaid.initialize({{startOnLoad: true, theme: 'default'}});</script>
</head>
<body>
{html_body}
</body>
</html>"""

    temp_html = md_path + ".temp.html"
    with open(temp_html, "w", encoding="utf-8") as f:
        f.write(full_html)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("file:///" + temp_html.replace("\\", "/"), wait_until="networkidle")
        page.wait_for_timeout(1500)
        page.pdf(
            path=pdf_path,
            format="A4",
            landscape=landscape,
            print_background=True,
            margin={"top": "12mm", "bottom": "12mm", "left": "12mm", "right": "12mm"},
        )
        browser.close()

    if os.path.exists(temp_html):
        os.remove(temp_html)
    print(f"[OK] Generated PDF: {pdf_path} ({os.path.getsize(pdf_path)} bytes)")


if __name__ == "__main__":
    md_to_pdf("Report.md", "Report.pdf", landscape=True)
    md_to_pdf("AI Audit Report.md", "AI Audit Report.pdf", landscape=False)
