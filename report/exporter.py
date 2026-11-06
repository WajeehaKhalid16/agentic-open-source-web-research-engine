"""Exports research results into Markdown, sanitized HTML, JSON, and JSONL formats."""

import html
import json
import os
import re
from typing import Dict, List, Optional
from evidence.schemas import Passage, ResearchReport


class ReportExporter:
    """Handles rendering and persistence of research outputs across multiple formats."""

    @staticmethod
    def to_markdown(report: ResearchReport) -> str:
        """Render report into clean, referenced Markdown."""
        lines: List[str] = [
            f"# {report.title}\n",
            f"**Research Query:** {report.query}  ",
            f"**Generated:** {report.created_at}  ",
            f"**Run ID:** `{report.run_id}`\n",
            "## Executive Summary\n",
            report.executive_summary,
            "\n## Key Findings by Theme\n",
        ]

        for section in report.thematic_findings:
            theme_title = section.get("theme", "Findings")
            lines.append(f"### {theme_title}\n")
            content = section.get("content")
            if content:
                lines.append(f"{content}\n")
            findings = section.get("findings", [])
            for point in findings:
                lines.append(f"- {point}")
            lines.append("")

        if report.disagreements_and_uncertainty:
            lines.append("## Disagreements and Uncertainty\n")
            for item in report.disagreements_and_uncertainty:
                lines.append(f"- {item}")
            lines.append("")

        if report.conclusion:
            lines.append("## Conclusion\n")
            lines.append(f"{report.conclusion}\n")

        if report.limitations:
            lines.append("## Limitations & Scope Bounds\n")
            for limit in report.limitations:
                lines.append(f"- {limit}")
            lines.append("")

        if report.warnings:
            lines.append("## Research & Source Warnings\n")
            for warn in report.warnings:
                lines.append(f"- ⚠️ {warn}")
            lines.append("")

        lines.append("## References\n")
        if not report.citations:
            lines.append("*No citations recorded.*\n")
        else:
            for cit in report.citations:
                meta = cit.display_metadata or {}
                title = meta.get("title") or "Source"
                domain = meta.get("domain") or cit.url
                author = f", by {meta['author']}" if meta.get("author") else ""
                pub_date = f" ({meta['published_at']})" if meta.get("published_at") else ""
                lines.append(f"[^{cit.citation_id}]: [{title}]({cit.url}) - *{domain}*{author}{pub_date}")

        return "\n".join(lines)

    @staticmethod
    def to_html(report: ResearchReport) -> str:
        """Render report into a self-contained, sanitized HTML document."""
        safe_title = html.escape(report.title)
        safe_query = html.escape(report.query)
        safe_summary = html.escape(report.executive_summary)

        findings_html = []
        for section in report.thematic_findings:
            theme = html.escape(section.get("theme", "Findings"))
            findings_html.append(f"<h3>{theme}</h3>")
            if section.get("content"):
                findings_html.append(f"<p>{html.escape(section['content'])}</p>")
            if section.get("findings"):
                findings_html.append("<ul>")
                for f in section["findings"]:
                    findings_html.append(f"<li>{html.escape(f)}</li>")
                findings_html.append("</ul>")

        citations_html = []
        for cit in report.citations:
            meta = cit.display_metadata or {}
            c_title = html.escape(meta.get("title") or "Source")
            c_domain = html.escape(meta.get("domain") or "")
            c_url = html.escape(cit.url)
            citations_html.append(
                f'<li id="{html.escape(cit.citation_id)}">'
                f'<a href="{c_url}" target="_blank" rel="noopener noreferrer">{c_title}</a> '
                f'<span class="source-domain">({c_domain})</span>'
                f'</li>'
            )

        warnings_html = ""
        if report.warnings:
            w_items = "".join([f"<li>⚠️ {html.escape(w)}</li>" for w in report.warnings])
            warnings_html = f"<h2>Warnings & Observations</h2><ul>{w_items}</ul>"

        html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{safe_title}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.6;
            color: #1a202c;
            max-width: 860px;
            margin: 40px auto;
            padding: 0 20px;
            background-color: #f8fafc;
        }}
        .card {{
            background: white;
            border-radius: 8px;
            padding: 32px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        h1 {{ color: #0f172a; margin-top: 0; font-size: 1.85rem; }}
        h2 {{ color: #1e293b; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px; margin-top: 32px; }}
        .badge {{ background: #e0f2fe; color: #0369a1; padding: 4px 8px; border-radius: 4px; font-size: 0.85rem; }}
        .source-domain {{ color: #64748b; font-size: 0.9rem; }}
        a {{ color: #0284c7; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        footer {{ margin-top: 40px; font-size: 0.85rem; color: #64748b; text-align: center; }}
    </style>
</head>
<body>
    <div class="card">
        <h1>{safe_title}</h1>
        <p><strong>Query:</strong> {safe_query} | <span class="badge">Run: {html.escape(report.run_id)}</span></p>
        
        <h2>Executive Summary</h2>
        <p>{safe_summary}</p>

        <h2>Key Findings</h2>
        {''.join(findings_html)}

        {warnings_html}

        <h2>References & Sources</h2>
        <ol>
            {''.join(citations_html)}
        </ol>
    </div>
    <footer>Generated by Agentic Open-Source Web Research Engine</footer>
</body>
</html>"""
        return html_template

    def export_all(
        self,
        report: ResearchReport,
        passages: Optional[List[Passage]] = None,
        output_dir: str = "reports",
    ) -> Dict[str, str]:
        """Export report.md, report.html, report.json, sources.json, evidence.jsonl, and run_manifest.json."""
        # Sanitize run_id for filesystem safety
        clean_run_id = re.sub(r"[^a-zA-Z0-9_-]", "_", report.run_id)
        target_dir = os.path.join(output_dir, clean_run_id)
        os.makedirs(target_dir, exist_ok=True)

        md_path = os.path.join(target_dir, "report.md")
        html_path = os.path.join(target_dir, "report.html")
        report_json_path = os.path.join(target_dir, "report.json")
        sources_path = os.path.join(target_dir, "sources.json")
        evidence_path = os.path.join(target_dir, "evidence.jsonl")
        manifest_path = os.path.join(target_dir, "run_manifest.json")

        # 1. report.md
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(self.to_markdown(report))

        # 2. report.html
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(self.to_html(report))

        # 3. report.json
        with open(report_json_path, "w", encoding="utf-8") as f:
            f.write(report.model_dump_json(indent=2))

        # 4. sources.json
        with open(sources_path, "w", encoding="utf-8") as f:
            sources_data = [s.model_dump() for s in report.sources]
            json.dump(sources_data, f, indent=2)

        # 5. evidence.jsonl
        passages = passages or []
        with open(evidence_path, "w", encoding="utf-8") as f:
            for p in passages:
                f.write(p.model_dump_json() + "\n")

        # 6. run_manifest.json
        manifest = {
            "run_id": report.run_id,
            "query": report.query,
            "created_at": report.created_at,
            "sources_count": len(report.sources),
            "citations_count": len(report.citations),
            "passages_count": len(passages),
            "unverified_claims_count": len(report.unverified_claims),
            "warnings_count": len(report.warnings),
        }
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

        return {
            "markdown": md_path,
            "html": html_path,
            "json": report_json_path,
            "sources": sources_path,
            "evidence": evidence_path,
            "manifest": manifest_path,
        }
