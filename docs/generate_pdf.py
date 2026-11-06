"""Generate polished HTML and PDF versions of the final project report."""

import os
import subprocess
import markdown

docs_dir = os.path.dirname(os.path.abspath(__file__))
md_path = os.path.join(docs_dir, "FINAL_PROJECT_REPORT.md")
html_path = os.path.join(docs_dir, "FINAL_PROJECT_REPORT.html")
pdf_path = os.path.join(docs_dir, "FINAL_PROJECT_REPORT.pdf")

with open(md_path, "r", encoding="utf-8") as f:
    text = f.read()

# Convert markdown to html with table and code fences
html_content = markdown.markdown(text, extensions=["extra", "tables", "toc"])

styled_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Final Technical Report - Agentic Open-Source Web Research Engine</title>
    <style>
        @page {{
            size: A4;
            margin: 20mm 15mm 20mm 15mm;
        }}
        body {{
            font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif;
            font-size: 10pt;
            line-height: 1.55;
            color: #23131E;
            background: #FFFFFF;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
        }}
        h1, h2, h3, h4 {{
            color: #23131E;
            font-family: Georgia, serif;
            page-break-after: avoid;
        }}
        h1 {{
            font-size: 18pt;
            border-bottom: 2px solid #FC9A64;
            padding-bottom: 6px;
            margin-top: 24px;
        }}
        h2 {{
            font-size: 13pt;
            border-bottom: 1px solid #FDE0B8;
            padding-bottom: 4px;
            margin-top: 20px;
        }}
        h3 {{
            font-size: 11pt;
            margin-top: 14px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 12px 0;
            font-size: 8.5pt;
            page-break-inside: avoid;
        }}
        th, td {{
            border: 1px solid #FDE0B8;
            padding: 5px 7px;
            text-align: left;
            vertical-align: top;
        }}
        th {{
            background-color: #23131E;
            color: #FFFFFF;
            font-weight: 600;
        }}
        tr:nth-child(even) {{
            background-color: #FEF4E6;
        }}
        code {{
            font-family: 'Consolas', 'Courier New', monospace;
            font-size: 8.5pt;
            background-color: #FEF4E6;
            padding: 1px 4px;
            border-radius: 3px;
            border: 1px solid #FDE0B8;
        }}
        pre {{
            background-color: #23131E;
            color: #FFF7EC;
            padding: 10px 12px;
            border-radius: 6px;
            overflow-x: auto;
            font-size: 8pt;
            page-break-inside: avoid;
        }}
        pre code {{
            background: transparent;
            border: none;
            color: #FFF7EC;
            padding: 0;
        }}
        blockquote {{
            border-left: 4px solid #FC9A64;
            background-color: #FEF4E6;
            margin: 10px 0;
            padding: 8px 12px;
            font-style: italic;
        }}
        hr {{
            border: none;
            border-top: 1px solid #FDE0B8;
            margin: 18px 0;
        }}
        p strong {{
            color: #23131E;
        }}
    </style>
</head>
<body>
{html_content}
</body>
</html>"""

with open(html_path, "w", encoding="utf-8") as f:
    f.write(styled_html)

print("HTML report successfully generated at:", html_path)

edge_exe = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
if os.path.exists(edge_exe):
    cmd = [
        edge_exe,
        "--headless",
        "--disable-gpu",
        "--run-all-compositor-stages-before-draw",
        "--print-to-pdf-no-header",
        f"--print-to-pdf={pdf_path}",
        f"file:///{html_path.replace(os.sep, '/')}",
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 0:
        print(f"PDF report successfully generated at: {pdf_path} ({os.path.getsize(pdf_path)} bytes)")
    else:
        print("PDF generation failed. Output:", res.stderr)
else:
    print("Microsoft Edge not found at expected location.")
