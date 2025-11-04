import markdown2

def render_markdown_to_html(md_text: str) -> str:
    """
    Convert Markdown text to GitHub-style dark HTML for QTextBrowser preview.
    """
    html = markdown2.markdown(
        md_text,
        extras=[
            "fenced-code-blocks",
            "tables",
            "autolink",
            "strike",
            "nofollow",
            "cuddled-lists",
            "metadata",
        ]
    )

    full_html = f"""<html>
<head>
<style>
body {{
    background-color: #1e1e1e;
    color: #ffffff;
    font-family: "Segoe UI", "Arial", sans-serif;
    padding: 10px;
}}
a {{
    color: #58a6ff;
    text-decoration: underline;
}}
pre {{
    background-color: #0d1117;
    color: #c9d1d9;
    padding: 8px;
    border-radius: 6px;
    overflow-x: auto;
}}
code {{
    background-color: #161b22;
    color: #c9d1d9;
    padding: 2px 4px;
    border-radius: 4px;
}}
table {{
    border-collapse: collapse;
    margin: 6px 0;
}}
th, td {{
    border: 1px solid #30363d;
    padding: 4px 8px;
}}
th {{
    background-color: #21262d;
}}
</style>
</head>
<body>
{html}
</body>
</html>"""
    return full_html
