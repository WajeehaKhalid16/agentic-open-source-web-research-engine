"""Stateful nodes executing discrete stages of the bounded research graph."""

import logging
from typing import Any, Dict, List, Optional
from agent.state import ResearchState
from app.config import get_settings
from crawl.extractor import extract_article_content
from crawl.fetcher import SafeFetcher
from crawl.policy import is_safe_url
from evidence.schemas import SearchResult
from evidence.verifier import CitationVerifier
from report.exporter import ReportExporter
from report.writer import ReportWriter
from retrieval.chunking import chunk_document_into_passages
from retrieval.deduplication import ContentDeduplicator
from retrieval.ranking import rank_passages_lexical
from search.duckduckgo_client import DuckDuckGoClient
from search.news_client import RSSNewsClient
from search.searxng_client import SearXNGClient

logger = logging.getLogger(__name__)


def scope_and_plan_node(state: ResearchState) -> ResearchState:
    """Stage 1 & 2: Normalize query, define constraints, and plan subquestions."""
    query = state.query.strip()
    subquestions = [
        query,
        f"{query} official data reports",
        f"{query} recent developments news",
        f"{query} criticism opposing views",
    ]
    state.subquestions = subquestions
    state.step = "planned"
    return state


async def discover_node(
    state: ResearchState,
    search_client: Optional[Any] = None,
    searxng_client: Optional[SearXNGClient] = None,
    news_client: Optional[RSSNewsClient] = None,
) -> ResearchState:
    """Stage 3: Discover candidate URLs using DuckDuckGo (or SearXNG) and RSS News."""
    settings = get_settings()
    news = news_client or RSSNewsClient()

    # Determine primary search engine client
    if search_client is not None:
        client = search_client
    elif searxng_client is not None:
        client = searxng_client
    elif getattr(settings, "search_provider", "duckduckgo") == "searxng":
        client = SearXNGClient()
    else:
        client = DuckDuckGoClient()

    max_sources = state.constraints.get("max_sources") or settings.max_sources
    include_news = state.constraints.get("include_news", True)
    max_rounds = state.constraints.get("max_rounds") or settings.max_search_rounds

    all_results: List[SearchResult] = []
    seen_urls = set()

    # 1. Primary web search
    for idx, sub_q in enumerate(state.subquestions[:max_rounds]):
        try:
            results = await client.search(sub_q, query_id=f"sq-{idx+1}")
        except Exception as exc:
            state.warnings.append(f"Search provider error on '{sub_q}': {str(exc)}")
            results = []

        if not results and idx == 0 and hasattr(client, "check_health"):
            try:
                health = await client.check_health()
                if not health.get("reachable"):
                    state.warnings.append(
                        f"Search provider is unreachable: {health.get('message', 'Check network access.')}"
                    )
            except Exception:
                pass

        for r in results:
            if r.url not in seen_urls and is_safe_url(r.url):
                seen_urls.add(r.url)
                all_results.append(r)
                if len(all_results) >= max_sources:
                    break
        if len(all_results) >= max_sources:
            break

    # 2. Supplement with public RSS news if requested or if search had few results
    if include_news and len(all_results) < max_sources:
        try:
            news_res = await news.search_news(state.query, query_id="sq-news", max_results=max_sources - len(all_results))
            for r in news_res:
                if r.url not in seen_urls and is_safe_url(r.url):
                    seen_urls.add(r.url)
                    all_results.append(r)
        except Exception as exc:
            state.warnings.append(f"RSS news discovery encountered an issue: {str(exc)}")

    if not all_results:
        state.warnings.append("No candidate search results discovered across configured providers.")

    state.search_results = all_results
    state.step = "discovered"
    return state


async def fetch_and_extract_node(
    state: ResearchState,
    fetcher: Optional[SafeFetcher] = None,
) -> ResearchState:
    """Stage 4 & 5: Fetch permissible pages and extract clean text and metadata."""
    safe_fetcher = fetcher or SafeFetcher()
    docs = []

    for res in state.search_results:
        fetch_res = await safe_fetcher.fetch(res.url)
        if fetch_res.success and fetch_res.content:
            doc = extract_article_content(
                html=fetch_res.content,
                url=fetch_res.canonical_url,
                fallback_title=res.title,
            )
            if doc.raw_text.strip():
                docs.append(doc)
            else:
                state.warnings.append(f"Source at {res.url} yielded no readable text content.")
        else:
            state.warnings.append(f"Failed to fetch {res.url}: {fetch_res.error or 'Empty response'}")

    if not docs and state.search_results:
        state.warnings.append("All discovered candidate pages failed retrieval or extraction.")

    state.documents = docs
    state.step = "extracted"
    return state


def deduplicate_and_rank_node(state: ResearchState) -> ResearchState:
    """Stage 6: Deduplicate documents, split passages, and score by BM25 relevance."""
    deduplicator = ContentDeduplicator()
    unique_docs, dup_map = deduplicator.filter_documents(state.documents)
    if dup_map:
        for dup_id, reason in dup_map.items():
            logger.info("Filtered duplicate document %s: %s", dup_id, reason)

    state.documents = unique_docs

    all_passages = []
    for doc in state.documents:
        passages = chunk_document_into_passages(doc)
        all_passages.extend(passages)

    state.passages = all_passages

    # Rank passages against query
    doc_map = {d.document_id: d for d in state.documents}
    ranked_evidence = rank_passages_lexical(
        query=state.query,
        passages=all_passages,
        documents_map=doc_map,
        top_k=15,
    )

    state.evidence_items = ranked_evidence
    state.step = "ranked"
    return state


async def synthesize_report_node(
    state: ResearchState,
    writer: Optional[ReportWriter] = None,
) -> ResearchState:
    """Stage 8: Synthesize an evidence-grounded report."""
    report_writer = writer or ReportWriter()
    report = await report_writer.generate_report(
        run_id=state.run_id,
        query=state.query,
        evidence_items=state.evidence_items,
        documents=state.documents,
        passages=state.passages,
    )
    # Merge run warnings into report
    if state.warnings:
        for w in state.warnings:
            if w not in report.warnings:
                report.warnings.append(w)

    state.report = report
    state.step = "synthesized"
    return state


def verify_citations_node(state: ResearchState) -> ResearchState:
    """Stage 9: Verify all report citations against actual stored evidence and check claim support."""
    if not state.report:
        return state

    verifier = CitationVerifier(
        documents=state.documents,
        passages=state.passages,
    )

    # Map citation IDs to evidence claims for substantiation verification
    claims_map: Dict[str, str] = {
        f"cit-{idx}": ev.claim for idx, ev in enumerate(state.evidence_items, start=1)
    }

    audits = verifier.verify_all(state.report.citations, claims=claims_map)
    state.audits = audits

    # Flag unverified citations and weak substantiation
    for audit in audits:
        if not audit.citation_verified:
            flag_msg = f"Citation {audit.citation_id}: Structural check failed ({audit.detail})"
            if flag_msg not in state.report.unverified_claims:
                state.report.unverified_claims.append(flag_msg)
        elif not audit.substantiated:
            state.warnings.append(f"Citation {audit.citation_id}: {audit.detail}")

    state.step = "verified"
    return state


def export_node(
    state: ResearchState,
    exporter: Optional[ReportExporter] = None,
    output_dir: str = "reports",
) -> ResearchState:
    """Stage 10: Export deliverables to disk (Markdown, HTML, JSON, JSONL)."""
    if not state.report:
        return state

    rep_exporter = exporter or ReportExporter()
    exports = rep_exporter.export_all(
        report=state.report,
        passages=state.passages,
        output_dir=output_dir,
    )
    state.exported_files = exports
    state.step = "exported"
    state.is_complete = True
    return state
