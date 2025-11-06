# helpers/markdown_to_html.py
import re
import os
from html import escape

import markdown2
from pygments import highlight
from pygments.lexers import get_lexer_by_name, TextLexer
from pygments.formatters import HtmlFormatter


# CSS used for code blocks (Pygments + small github-like tweaks)
PYGMENTS_CSS = HtmlFormatter(nowrap=True).get_style_defs(".codehilite")
EXTRA_CSS = """
/* Overall body */
body {
    background: #0f1720;   /* matches editor background */
    color: #d6deeb;        /* matches editor text color */
    font-family: "Segoe UI", Arial, sans-serif;
    font-size: 12pt;
    padding: 10px;
    margin: 0;
}

/* Links */
a {
    color: #58a6ff;
    text-decoration: none;
}
a:hover {
    text-decoration: underline;
}

/* Code blocks */
pre, .codehilite {
    background: #0f1720;   /* match editor panel */
    color: #d6deeb;        /* match editor text */
    border-radius: 6px;
    padding: 10px;
    overflow: auto;
    font-family: "Fira Code", monospace;
    font-size: 11pt;
}

pre.codehilite {
    background: #0f1720 !important;
    color: #d6deeb !important;
    border-radius: 6px;
    padding: 10px;
    overflow: auto;
    font-family: "Fira Code", monospace;
    font-size: 11pt;
}

/* Inline code */
code.inline {
    background: #0f1720;   
    color: #d6deeb;
    padding: 2px 6px;
    border-radius: 4px;
    font-family: "Fira Code", monospace;
}

/* Tables */
table {
    border-collapse: collapse;
    margin: 6px 0;
}
th, td {
    border: 1px solid #222;
    padding: 6px 8px;
}
th {
    background: #0b1220;
}

/* Blockquotes */
blockquote {
    border-left: 4px solid #58a6ff;
    padding-left: 10px;
    color: #9aa5b1;
    margin: 6px 0;
}

/* Lists */
ul, ol {
    margin: 6px 0;
    padding-left: 20px;
}

/* Headings */
h1, h2, h3, h4, h5, h6 {
    color: #d6deeb;
    margin: 8px 0;
    font-weight: bold;
}
""" + PYGMENTS_CSS


def _highlight_code_blocks(html: str) -> str:
    """
    Find <pre><code class="language-...">...</code></pre> and replace with pygments-highlighted HTML.
    Works with markdown2's fenced-code-blocks output.
    """
    def repl(m):
        lang = m.group("lang") or ""
        code = m.group("code") or ""
        code = code.rstrip("\n")
        try:
            lexer = get_lexer_by_name(lang) if lang else TextLexer()
        except Exception:
            lexer = TextLexer()
        formatter = HtmlFormatter(nowrap=True, noclasses=True)
        highlighted = highlight(code, lexer, formatter)
        # embed in <pre><code class="codehilite"> for consistent CSS
        return f'<pre><code class="codehilite">{highlighted}</code></pre>'

    pattern = re.compile(
        r'<pre><code(?: class="language-(?P<lang>[\w+-]+)")?>(?P<code>.*?)</code></pre>',
        flags=re.DOTALL
    )
    return pattern.sub(repl, html)


def render_markdown_to_html(md_text: str) -> str:
    """
    Render markdown -> full HTML snippet styled for QTextBrowser.
    Uses markdown2 extras and applies Pygments to code blocks.
    """
    # extras: fenced code blocks, tables, autolink, strike, task lists (checkboxes supported by markdown2 via 'extras' isn't native,
    # we'll keep checkboxes as "- [ ]" -> show as text; you can post-process if you want real checkboxes)
    html = markdown2.markdown(
        md_text,
        extras=[
            "fenced-code-blocks",
            "tables",
            "autolink",
            "strike",
            "cuddled-lists",
            "metadata",
        ],
    )

    # Convert HTML entities inside code blocks from markdown2 (usually safe)
    html = _highlight_code_blocks(html)

    full = f"""<html><head><meta charset="utf-8"><style>{EXTRA_CSS}</style></head>
    <body>{html}</body></html>"""
    return full


# Optional utility for saving an image (used by EditorPanel)
def save_dropped_image(bytes_data: bytes, filename_hint: str = "pasted") -> str:
    """
    Save bytes_data to data/images under project root. Returns relative path (forward slashes).
    """
    base = os.path.abspath(os.path.join(os.getcwd(), "data", "images"))
    os.makedirs(base, exist_ok=True)
    # try to determine extension from hint, else default .png
    name = f"{filename_hint}".replace(" ", "_")
    ext = ".png"
    if "." in filename_hint and len(filename_hint.split(".")[-1]) <= 4:
        ext = "." + filename_hint.split(".")[-1]
    i = 0
    while True:
        candidate = os.path.join(base, f"{name}_{i}{ext}")
        if not os.path.exists(candidate):
            break
        i += 1
    with open(candidate, "wb") as f:
        f.write(bytes_data)
    # return relative path for markdown link
    rel = os.path.relpath(candidate, os.getcwd()).replace("\\", "/")
    return rel
