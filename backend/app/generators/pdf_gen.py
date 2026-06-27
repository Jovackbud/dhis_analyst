"""PDF generator — WeasyPrint primary, raw PDF fallback.

Full print-optimised CSS with page-break rules, branded colours, headers,
and footers. The fallback generates a minimal valid PDF when WeasyPrint
is not available (e.g. missing system dependencies on Windows).
"""
from __future__ import annotations

import logging

logger = logging.getLogger("dhis2_analyst.pdf_gen")


def html_to_pdf(html: str) -> bytes:
    """Convert report HTML to PDF bytes."""
    try:
        from weasyprint import HTML
        result = HTML(string=_wrap(html)).write_pdf()
        logger.info("pdf_generated_weasyprint", extra={"size": len(result)})
        return result
    except Exception as exc:
        logger.warning("weasyprint_fallback", extra={"error": str(exc)})
        return _fallback_pdf(html)


def _wrap(html: str) -> str:
    """Wrap report HTML in a full document with print-optimised CSS."""
    return f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<style>
@page {{
    size: A4;
    margin: 2.5cm;
    @top-right {{ content: "DHIS2 AI Analyst"; font-size: 8pt; color: #6b7b8d; }}
    @bottom-center {{ content: "Page " counter(page) " of " counter(pages); font-size: 8pt; color: #6b7b8d; }}
}}

body {{
    font-family: Arial, Helvetica, sans-serif;
    font-size: 11pt;
    line-height: 1.5;
    color: #111827;
    margin: 0;
}}

h1 {{
    color: #0b171d;
    font-size: 22pt;
    border-bottom: 2px solid #38bdf8;
    padding-bottom: 8px;
    margin-top: 0;
    page-break-after: avoid;
}}

h2 {{
    color: #164e63;
    font-size: 16pt;
    margin-top: 24px;
    page-break-after: avoid;
}}

h3 {{
    color: #1f3440;
    font-size: 13pt;
    page-break-after: avoid;
}}

p {{
    margin: 6px 0;
    orphans: 3;
    widows: 3;
}}

table {{
    width: 100%;
    border-collapse: collapse;
    margin: 12px 0;
    page-break-inside: auto;
}}

thead {{
    display: table-header-group;
}}

tr {{
    page-break-inside: avoid;
}}

th {{
    background-color: #0f2028;
    color: #f8fafc;
    font-weight: bold;
    text-align: left;
    padding: 8px;
    border: 1px solid #334b5b;
}}

td {{
    border: 1px solid #d1d5db;
    padding: 6px 8px;
}}

tbody tr:nth-child(even) {{
    background-color: #f8fafc;
}}

ul, ol {{
    margin: 8px 0;
    padding-left: 24px;
}}

li {{
    margin: 4px 0;
}}

a {{
    color: #164e63;
    text-decoration: none;
}}

em {{
    color: #6b7b8d;
}}

strong {{
    color: #0b171d;
}}
</style>
</head>
<body>{html}</body>
</html>"""


def _fallback_pdf(html: str) -> bytes:
    """Generate a minimal valid PDF when WeasyPrint is unavailable."""
    # Strip HTML tags for plain text
    import re
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text).strip()
    safe = text[:3000].encode("latin-1", "replace").decode("latin-1")

    # Split into lines for multi-line rendering
    lines = []
    while safe:
        lines.append(safe[:100])
        safe = safe[100:]

    stream_parts = []
    y = 760
    for line in lines[:50]:
        escaped = line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        stream_parts.append(f"BT /F1 10 Tf 50 {y} Td ({escaped}) Tj ET")
        y -= 14
        if y < 50:
            break

    stream = "\n".join(stream_parts)
    objects = [
        "1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj",
        "2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj",
        f"3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] "
        f"/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >> endobj",
        "4 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj",
        f"5 0 obj << /Length {len(stream)} >> stream\n{stream}\nendstream endobj",
    ]
    body = "\n".join(objects)
    return f"%PDF-1.4\n{body}\ntrailer << /Root 1 0 R >>\n%%EOF".encode("latin-1")
