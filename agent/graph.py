"""Bounded state graph orchestrating research stages with explicit transitions and stopping rules."""

import json
import logging
import uuid
from typing import Any, Callable, Dict, List, Optional
from agent.nodes import (
    deduplicate_and_rank_node,
    discover_node,
    export_node,
    fetch_and_extract_node,
    scope_and_plan_node,
    synthesize_report_node,
    verify_citations_node,
)
from agent.state import ResearchState
from app.config import get_settings
from crawl.fetcher import SafeFetcher
from evidence.schemas import ResearchRun, utc_now_iso
from report.exporter import ReportExporter
from report.writer import ReportWriter
from search.duckduckgo_client import DuckDuckGoClient
from search.news_client import RSSNewsClient
from search.searxng_client import SearXNGClient
from storage.repository import ResearchRepository

logger = logging.getLogger(__name__)


class ResearchWorkflow:
    """Bounded, stateful workflow coordinator executing research nodes in order."""

    def __init__(
        self,
        repository: Optional[ResearchRepository] = None,
        search_client: Optional[Any] = None,
        searxng_client: Optional[SearXNGClient] = None,
        news_client: Optional[RSSNewsClient] = None,
        fetcher: Optional[SafeFetcher] = None,
        writer: Optional[ReportWriter] = None,
        exporter: Optional[ReportExporter] = None,
    ):
        settings = get_settings()
        self.repository = repository or ResearchRepository()

        # Prioritize search_client, then searxng_client (backward compat), then config
        if search_client is not None:
            self.search_client = search_client
        elif searxng_client is not None:
            self.search_client = searxng_client
        elif getattr(settings, "search_provider", "duckduckgo") == "searxng":
            self.search_client = SearXNGClient()
        else:
            self.search_client = DuckDuckGoClient()

        self.news = news_client or RSSNewsClient()
        self.fetcher = fetcher or SafeFetcher()
        self.writer = writer or ReportWriter()
        self.exporter = exporter or ReportExporter()

    async def execute(
        self,
        query: str,
        run_id: Optional[str] = None,
        constraints: Optional[Dict[str, Any]] = None,
        event_callback: Optional[Callable[[Dict[str, Any]], Any]] = None,
    ) -> ResearchState:
        """Execute the end-to-end research graph sequentially."""
        active_run_id = run_id or f"run-{uuid.uuid4().hex[:8]}"
        state = ResearchState(
            run_id=active_run_id,
            query=query,
            constraints=constraints or {},
        )

        def emit(ev: Dict[str, Any]):
            if event_callback:
                try:
                    res = event_callback(ev)
                    import asyncio
                    if asyncio.iscoroutine(res):
                        asyncio.create_task(res)
                except Exception:
                    pass

        # 0. Initialize run record in storage
        run_record = ResearchRun(
            run_id=active_run_id,
            query=query,
            constraints=state.constraints,
            status="running",
        )
        self.repository.save_run(run_record)

        try:
            # Stage 1 & 2: Scope & Plan
            emit({"event": "stage", "stage": "scope", "status": "running", "ts": utc_now_iso()})
            logger.info("[%s] Scoping and planning query...", active_run_id)
            state = scope_and_plan_node(state)
            emit({"event": "stage", "stage": "scope", "status": "complete", "ts": utc_now_iso()})
            emit({"event": "stage", "stage": "plan", "status": "complete", "ts": utc_now_iso()})
            emit({"event": "plan_ready", "plan": {"scope": query, "query_variants": state.subquestions}})

            # Stage 3: Discover candidate sources via free search + news
            emit({"event": "stage", "stage": "search", "status": "running", "ts": utc_now_iso()})
            logger.info("[%s] Discovering sources via Search / News...", active_run_id)
            state = await discover_node(
                state,
                search_client=self.search_client,
                news_client=self.news,
            )
            if state.search_results:
                self.repository.save_search_results(active_run_id, state.search_results)
                for res in state.search_results:
                    emit({
                        "event": "source",
                        "source": {
                            "source_id": res.url,
                            "url": res.url,
                            "title": res.title,
                            "type": "news" if getattr(res, "engine", "") == "rss" else "web",
                            "status": "fetching",
                            "fetch_ms": None,
                            "credibility_score": 0.8,
                            "snippet": res.snippet,
                        },
                    })
            emit({"event": "stage", "stage": "search", "status": "complete", "ts": utc_now_iso()})

            # Stage 4 & 5: Fetch & Extract
            emit({"event": "stage", "stage": "fetch", "status": "running", "ts": utc_now_iso()})
            logger.info("[%s] Fetching %d candidate sources...", active_run_id, len(state.search_results))
            state = await fetch_and_extract_node(state, fetcher=self.fetcher)
            if state.documents:
                self.repository.save_documents(active_run_id, state.documents)
                for doc in state.documents:
                    emit({
                        "event": "source_update",
                        "source_id": doc.canonical_url,
                        "status": "extracted" if doc.fetch_status == "success" else "failed",
                        "snippet": (doc.raw_text[:200] + "...") if doc.raw_text else None,
                        "credibility_score": 0.85,
                    })
            emit({"event": "stage", "stage": "fetch", "status": "complete", "ts": utc_now_iso()})
            emit({"event": "stage", "stage": "extract", "status": "complete", "ts": utc_now_iso()})

            # Stage 6: Deduplicate, Chunk, & Rank Evidence
            emit({"event": "stage", "stage": "rank", "status": "running", "ts": utc_now_iso()})
            logger.info("[%s] Deduplicating, chunking, and ranking passages...", active_run_id)
            state = deduplicate_and_rank_node(state)
            if state.passages:
                self.repository.save_passages(active_run_id, state.passages)
            if state.evidence_items:
                self.repository.save_evidence(active_run_id, state.evidence_items)
            emit({"event": "stage", "stage": "rank", "status": "complete", "ts": utc_now_iso()})

            # Stage 8: Synthesize Report
            emit({"event": "stage", "stage": "write", "status": "running", "ts": utc_now_iso()})
            logger.info("[%s] Synthesizing grounded report...", active_run_id)
            state = await synthesize_report_node(state, writer=self.writer)
            if state.report:
                self.repository.save_report(active_run_id, state.report)
            emit({"event": "stage", "stage": "write", "status": "complete", "ts": utc_now_iso()})

            # Stage 9: Verify Citations
            emit({"event": "stage", "stage": "verify", "status": "running", "ts": utc_now_iso()})
            logger.info("[%s] Verifying claim citations...", active_run_id)
            state = verify_citations_node(state)
            if state.report and state.report.citations:
                self.repository.save_citations(active_run_id, state.report.citations)
            emit({"event": "stage", "stage": "verify", "status": "complete", "ts": utc_now_iso()})

            # Stage 10: Export Deliverables
            logger.info("[%s] Exporting deliverables...", active_run_id)
            state = export_node(state, exporter=self.exporter)

            # Update final storage state
            end_time = utc_now_iso()
            self.repository.update_run_status(
                run_id=active_run_id,
                status="completed",
                summary=state.report.executive_summary[:250] if state.report else "Finished.",
                end_time=end_time,
                report_json=state.report.model_dump_json() if state.report else None,
                warnings_json=json.dumps(state.warnings) if state.warnings else None,
            )
            emit({"event": "complete", "run_id": active_run_id, "redirect": f"/runs/{active_run_id}"})

        except Exception as exc:
            logger.exception("[%s] Research pipeline encountered error: %s", active_run_id, exc)
            state.errors.append(str(exc))
            state.step = "failed"
            self.repository.update_run_status(
                run_id=active_run_id,
                status="failed",
                summary=f"Failed with error: {str(exc)}",
                end_time=utc_now_iso(),
                warnings_json=json.dumps(state.warnings) if state.warnings else None,
            )
            emit({"event": "error", "stage": "verify", "message": str(exc), "recoverable": False})

        return state
