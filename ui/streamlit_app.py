"""Streamlit interactive UI connected to the FastAPI Agentic Web Research Engine backend."""

import os
import sys
from typing import Any, Dict, Optional
import httpx

# Ensure repository root is in Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False


def check_api_health(base_url: str) -> Dict[str, Any]:
    """Probe the FastAPI backend for health and config."""
    try:
        with httpx.Client(timeout=2.0) as client:
            resp = client.get(f"{base_url.rstrip('/')}/health")
            if resp.status_code == 200:
                cfg_resp = client.get(f"{base_url.rstrip('/')}/api/config")
                cfg = cfg_resp.json() if cfg_resp.status_code == 200 else {}
                return {"online": True, "config": cfg}
    except Exception:
        pass
    return {"online": False, "config": {}}


def display_research_results(data: Dict[str, Any], api_url: str):
    """Render the research outputs, report, evidence, sources, and audits."""
    research_id = data.get("research_id", "unknown")
    run_status = data.get("status", "unknown")
    report = data.get("report") or {}
    sources = data.get("sources") or []
    evidence = data.get("evidence") or []
    audits = data.get("audits") or []
    warnings = data.get("warnings") or []

    st.success(f"Mission Complete! Status: `{run_status}` | Research ID: `{research_id}`")

    if warnings:
        with st.expander("⚠️ Pipeline Warnings & Observations", expanded=True):
            for w in warnings:
                st.warning(w)

    tab_report, tab_evidence, tab_sources, tab_audits, tab_downloads = st.tabs([
        "📄 Final Report",
        "🧩 Stored Evidence",
        "🌐 Sources & Provenance",
        "🛡️ Citation Audit",
        "💾 Downloads & Exports",
    ])

    # Tab 1: Report
    with tab_report:
        if report:
            title = report.get("title", "Research Report")
            summary = report.get("executive_summary", "")
            thematic = report.get("thematic_findings") or []
            disagreements = report.get("disagreements_and_uncertainty") or []
            conclusion = report.get("conclusion", "")
            limitations = report.get("limitations") or []
            citations = report.get("citations") or []

            st.header(title)
            st.markdown(f"**Executive Summary:**\n\n{summary}")

            for sec in thematic:
                st.subheader(sec.get("theme", "Theme"))
                if sec.get("content"):
                    st.write(sec.get("content"))
                for pt in sec.get("findings", []):
                    st.markdown(f"- {pt}")

            if disagreements:
                st.subheader("Disagreements & Uncertainty")
                for d in disagreements:
                    st.markdown(f"- {d}")

            if conclusion:
                st.subheader("Conclusion")
                st.write(conclusion)

            if limitations:
                st.subheader("Limitations")
                for l in limitations:
                    st.markdown(f"- {l}")

            if citations:
                st.subheader("References")
                for c in citations:
                    meta = c.get("display_metadata") or {}
                    c_title = meta.get("title") or "Source"
                    c_domain = meta.get("domain") or c.get("url")
                    st.markdown(f"- **[^{c.get('citation_id')}]:** [{c_title}]({c.get('url')}) *({c_domain})*")
        else:
            st.info("No synthesized report content is available for this run.")

    # Tab 2: Stored Evidence
    with tab_evidence:
        st.markdown(f"### Ranked Evidence Items ({len(evidence)})")
        if not evidence:
            st.info("No evidence items were extracted for this research run.")
        for ev in evidence:
            score = ev.get("relevance_score", 0.0)
            with st.expander(f"🔹 [{ev.get('evidence_id')}] Relevance: {score:.2f} — {ev.get('claim')[:80]}..."):
                st.markdown(f"**Claim / Finding:** {ev.get('claim')}")
                st.markdown(f"**Source Domain:** `{ev.get('source_domain')}`")
                st.markdown(f"**Supporting Passage IDs:** `{ev.get('passage_ids')}`")
                if ev.get("notes"):
                    st.caption(f"Scoring Notes: {ev.get('notes')}")

    # Tab 3: Sources
    with tab_sources:
        st.markdown(f"### Collected Sources ({len(sources)})")
        if not sources:
            st.info("No web sources were successfully retrieved.")
        for s in sources:
            with st.container():
                st.markdown(f"#### [{s.get('title')}]({s.get('canonical_url')})")
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.caption(f"Domain: `{s.get('domain')}`")
                with col_b:
                    st.caption(f"Status: `{s.get('fetch_status')}`")
                with col_c:
                    st.caption(f"Language: `{s.get('language')}`")
                st.divider()

    # Tab 4: Citation Audit
    with tab_audits:
        st.markdown(f"### Citation Verification Audits ({len(audits)})")
        if not audits:
            st.info("No citations to audit.")
        for a in audits:
            is_verified = a.get("citation_verified", False)
            is_substantiated = a.get("substantiated", False)
            icon = "✅" if (is_verified and is_substantiated) else ("⚠️" if is_verified else "❌")
            st.markdown(f"{icon} **{a.get('citation_id')}**: {a.get('detail')}")

    # Tab 5: Downloads
    with tab_downloads:
        st.markdown("### Export Deliverables")
        export_md_url = f"{api_url.rstrip('/')}/api/research/{research_id}/export/md"
        export_html_url = f"{api_url.rstrip('/')}/api/research/{research_id}/export/html"
        export_json_url = f"{api_url.rstrip('/')}/api/research/{research_id}/export/json"

        col1, col2, col3 = st.columns(3)
        with col1:
            try:
                with httpx.Client(timeout=5.0) as client:
                    resp_md = client.get(export_md_url)
                    if resp_md.status_code == 200:
                        st.download_button(
                            label="📥 Download Markdown (.md)",
                            data=resp_md.content,
                            file_name=f"{research_id}-report.md",
                            mime="text/markdown",
                        )
            except Exception:
                st.markdown(f"[Download Markdown]({export_md_url})")

        with col2:
            try:
                with httpx.Client(timeout=5.0) as client:
                    resp_html = client.get(export_html_url)
                    if resp_html.status_code == 200:
                        st.download_button(
                            label="📥 Download HTML (.html)",
                            data=resp_html.content,
                            file_name=f"{research_id}-report.html",
                            mime="text/html",
                        )
            except Exception:
                st.markdown(f"[Download HTML]({export_html_url})")

        with col3:
            try:
                with httpx.Client(timeout=5.0) as client:
                    resp_json = client.get(export_json_url)
                    if resp_json.status_code == 200:
                        st.download_button(
                            label="📥 Download JSON (.json)",
                            data=resp_json.content,
                            file_name=f"{research_id}-report.json",
                            mime="application/json",
                        )
            except Exception:
                st.markdown(f"[Download JSON]({export_json_url})")


def main():
    if not STREAMLIT_AVAILABLE:
        print("Streamlit is not installed in the environment. Install with: pip install streamlit")
        return

    st.set_page_config(
        page_title="Agentic Web Research Engine",
        page_icon="🔎",
        layout="wide",
    )

    st.title("🔎 Agentic Open-Source Web Research Engine")
    st.caption("Locally deployable, evidence-grounded research assistant with verifiable citations.")

    # Sidebar: Backend Connection & Configuration
    with st.sidebar:
        st.header("⚙️ Backend Connection")
        api_url = st.text_input("FastAPI Base URL", value="http://127.0.0.1:8000")

        health_data = check_api_health(api_url)
        if health_data["online"]:
            st.success("🟢 Backend Connected")
            cfg = health_data["config"]
            st.caption(f"App: **{cfg.get('app_name', 'Research Engine')}**")
            st.caption(f"Search: **{cfg.get('search_provider', 'duckduckgo').upper()}** (Free, No Docker)")
            st.caption(f"LLM Target: `{cfg.get('ollama_model', 'qwen2.5:7b')}`")
        else:
            st.error("🔴 Backend Unreachable")
            st.caption(r"Start the backend in PowerShell:\n`.\.venv\Scripts\python.exe -m uvicorn app.main:app --port 8000`")

        st.divider()
        st.header("🔬 Search Settings")
        max_sources = st.slider("Max Sources to Fetch", min_value=1, max_value=20, value=5)
        include_news = st.checkbox("Include RSS/Atom News Discovery", value=True)

        st.divider()
        st.header("📂 Retrieve Saved Run")
        lookup_run_id = st.text_input("Existing Research ID", placeholder="e.g. run-1234abcd")
        load_run_btn = st.button("Load Past Run")

    # Handle loading existing run
    if load_run_btn and lookup_run_id.strip():
        if not health_data["online"]:
            st.error("Cannot retrieve past run: FastAPI backend is offline.")
        else:
            with st.spinner(f"Fetching run {lookup_run_id}..."):
                try:
                    with httpx.Client(timeout=10.0) as client:
                        resp = client.get(f"{api_url.rstrip('/')}/api/research/{lookup_run_id.strip()}")
                        if resp.status_code == 200:
                            data = resp.json()
                            display_research_results(data, api_url)
                            return
                        else:
                            st.error(f"Run '{lookup_run_id}' not found (HTTP {resp.status_code}).")
                except Exception as exc:
                    st.error(f"Failed to fetch run: {str(exc)}")

    # Main query interface
    st.subheader("Ask a Research Question")
    query = st.text_area(
        "Enter your research question:",
        value="What are the recent applications of AI in disaster management?",
        height=90,
    )

    col_btn, _ = st.columns([1, 5])
    with col_btn:
        start_btn = st.button("🚀 Start Research", type="primary")

    if start_btn:
        if not query.strip() or len(query.strip()) < 3:
            st.warning("Please enter a research question with at least 3 characters.")
            return

        if not health_data["online"]:
            st.error(
                "FastAPI backend is offline. Please launch the backend before initiating research:\n\n"
                "```powershell\n"
                ".\\.venv\\Scripts\\python.exe -m uvicorn app.main:app --port 8000\n"
                "```"
            )
            return

        with st.spinner("Executing agentic research pipeline (scope ➔ plan ➔ discover ➔ crawl ➔ rank ➔ synthesize ➔ verify ➔ export)..."):
            payload = {
                "query": query.strip(),
                "max_sources": max_sources,
                "include_news": include_news,
            }
            try:
                # Generous timeout for crawling, extraction, ranking, and synthesis
                with httpx.Client(timeout=90.0) as client:
                    resp = client.post(f"{api_url.rstrip('/')}/api/research", json=payload)
                    if resp.status_code == 200:
                        data = resp.json()
                        display_research_results(data, api_url)
                    else:
                        st.error(f"Research request failed: HTTP {resp.status_code} - {resp.text}")
            except httpx.TimeoutException:
                st.error("Request timed out waiting for backend research pipeline. Try reducing the number of sources.")
            except Exception as exc:
                st.error(f"Failed to communicate with research API: {str(exc)}")


if __name__ == "__main__":
    main()
