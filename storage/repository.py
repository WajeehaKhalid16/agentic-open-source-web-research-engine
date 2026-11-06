"""Data access repository for research runs, documents, passages, and citations."""

import json
from typing import Any, Dict, List, Optional
from evidence.schemas import (
    Citation,
    Document,
    Evidence,
    Passage,
    ResearchReport,
    ResearchRun,
    SearchResult,
)
from storage.database import Database


class ResearchRepository:
    """Provides typed CRUD operations against SQLite storage."""

    def __init__(self, db: Optional[Database] = None):
        self.db = db or Database()

    def save_run(self, run: ResearchRun) -> None:
        """Insert or replace a ResearchRun record."""
        with self.db.get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO research_runs
                (run_id, query, constraints_json, start_time, end_time, budgets_json, model_version, status, summary, report_json, warnings_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run.run_id,
                    run.query,
                    json.dumps(run.constraints),
                    run.start_time,
                    run.end_time,
                    json.dumps(run.budgets),
                    run.model_version,
                    run.status,
                    run.summary,
                    run.report_json,
                    run.warnings_json,
                ),
            )

    def get_run(self, run_id: str) -> Optional[ResearchRun]:
        """Fetch a ResearchRun by ID."""
        with self.db.get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM research_runs WHERE run_id = ?", (run_id,)
            ).fetchone()
            if not row:
                return None
            return ResearchRun(
                run_id=row["run_id"],
                query=row["query"],
                constraints=json.loads(row["constraints_json"] or "{}"),
                start_time=row["start_time"],
                end_time=row["end_time"],
                budgets=json.loads(row["budgets_json"] or "{}"),
                model_version=row["model_version"] or "local",
                status=row["status"],
                summary=row["summary"],
                report_json=row["report_json"] if "report_json" in row.keys() else None,
                warnings_json=row["warnings_json"] if "warnings_json" in row.keys() else None,
            )

    def list_runs(self, limit: int = 50) -> List[ResearchRun]:
        """Fetch recent research runs ordered by start_time descending."""
        with self.db.get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM research_runs ORDER BY start_time DESC LIMIT ?", (limit,)
            ).fetchall()
            return [
                ResearchRun(
                    run_id=row["run_id"],
                    query=row["query"],
                    constraints=json.loads(row["constraints_json"] or "{}"),
                    start_time=row["start_time"],
                    end_time=row["end_time"],
                    budgets=json.loads(row["budgets_json"] or "{}"),
                    model_version=row["model_version"] or "local",
                    status=row["status"],
                    summary=row["summary"],
                    report_json=row["report_json"] if "report_json" in row.keys() else None,
                    warnings_json=row["warnings_json"] if "warnings_json" in row.keys() else None,
                )
                for row in rows
            ]

    def update_run_status(
        self,
        run_id: str,
        status: str,
        summary: Optional[str] = None,
        end_time: Optional[str] = None,
        report_json: Optional[str] = None,
        warnings_json: Optional[str] = None,
    ) -> None:
        """Update status, summary, report_json, and warnings_json for a research run."""
        with self.db.get_connection() as conn:
            conn.execute(
                """
                UPDATE research_runs
                SET status = ?,
                    summary = COALESCE(?, summary),
                    end_time = COALESCE(?, end_time),
                    report_json = COALESCE(?, report_json),
                    warnings_json = COALESCE(?, warnings_json)
                WHERE run_id = ?
                """,
                (status, summary, end_time, report_json, warnings_json, run_id),
            )

    def save_search_results(self, run_id: str, results: List[SearchResult]) -> None:
        """Persist batch of SearchResult records."""
        with self.db.get_connection() as conn:
            conn.executemany(
                """
                INSERT INTO search_results
                (run_id, query_id, rank, engine, title, snippet, url, discovered_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        run_id,
                        res.query_id,
                        res.rank,
                        res.engine,
                        res.title,
                        res.snippet,
                        res.url,
                        res.discovered_at,
                    )
                    for res in results
                ],
            )

    def get_search_results(self, run_id: str) -> List[SearchResult]:
        """Retrieve all search results discovered for a run."""
        with self.db.get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM search_results WHERE run_id = ? ORDER BY rank ASC", (run_id,)
            ).fetchall()
            return [
                SearchResult(
                    query_id=row["query_id"] or "",
                    rank=row["rank"] or 1,
                    engine=row["engine"] or "unknown",
                    title=row["title"] or "Untitled",
                    snippet=row["snippet"] or "",
                    url=row["url"],
                    discovered_at=row["discovered_at"],
                )
                for row in rows
            ]

    def save_documents(self, run_id: str, docs: List[Document]) -> None:
        """Insert or replace fetched documents."""
        with self.db.get_connection() as conn:
            conn.executemany(
                """
                INSERT OR REPLACE INTO documents
                (document_id, run_id, canonical_url, domain, title, author, published_at, retrieved_at, language, content_hash, fetch_status, raw_text)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        doc.document_id,
                        run_id,
                        doc.canonical_url,
                        doc.domain,
                        doc.title,
                        doc.author,
                        doc.published_at,
                        doc.retrieved_at,
                        doc.language,
                        doc.content_hash,
                        doc.fetch_status,
                        doc.raw_text,
                    )
                    for doc in docs
                ],
            )

    def get_documents(self, run_id: str) -> List[Document]:
        """Retrieve all documents associated with a run."""
        with self.db.get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM documents WHERE run_id = ?", (run_id,)
            ).fetchall()
            return [
                Document(
                    document_id=row["document_id"],
                    canonical_url=row["canonical_url"],
                    domain=row["domain"],
                    title=row["title"] or "Untitled",
                    author=row["author"],
                    published_at=row["published_at"],
                    retrieved_at=row["retrieved_at"],
                    language=row["language"],
                    content_hash=row["content_hash"],
                    fetch_status=row["fetch_status"],
                    raw_text=row["raw_text"] or "",
                )
                for row in rows
            ]

    def save_passages(self, run_id: str, passages: List[Passage]) -> None:
        """Insert or replace passage chunks."""
        with self.db.get_connection() as conn:
            conn.executemany(
                """
                INSERT OR REPLACE INTO passages
                (passage_id, document_id, run_id, text, heading, start_char, end_char, passage_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        p.passage_id,
                        p.document_id,
                        run_id,
                        p.text,
                        p.heading,
                        p.character_offsets[0],
                        p.character_offsets[1],
                        p.passage_hash,
                    )
                    for p in passages
                ],
            )

    def get_passages(self, run_id: str) -> List[Passage]:
        """Fetch all passages for a given run."""
        with self.db.get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM passages WHERE run_id = ?", (run_id,)
            ).fetchall()
            return [
                Passage(
                    passage_id=row["passage_id"],
                    document_id=row["document_id"],
                    text=row["text"],
                    heading=row["heading"],
                    character_offsets=(row["start_char"], row["end_char"]),
                    passage_hash=row["passage_hash"],
                )
                for row in rows
            ]

    def save_evidence(self, run_id: str, evidence: List[Evidence]) -> None:
        """Insert or replace ranked evidence items."""
        with self.db.get_connection() as conn:
            conn.executemany(
                """
                INSERT OR REPLACE INTO evidence
                (evidence_id, run_id, claim, passage_ids_json, relevance_score, source_domain, source_signals_json, corroboration_group, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        ev.evidence_id,
                        run_id,
                        ev.claim,
                        json.dumps(ev.passage_ids),
                        ev.relevance_score,
                        ev.source_domain or (ev.source_signals.get("domain", "") if ev.source_signals else ""),
                        json.dumps(ev.source_signals),
                        ev.corroboration_group,
                        ev.notes,
                    )
                    for ev in evidence
                ],
            )

    def get_evidence(self, run_id: str) -> List[Evidence]:
        """Fetch all evidence items for a given run."""
        with self.db.get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM evidence WHERE run_id = ? ORDER BY relevance_score DESC", (run_id,)
            ).fetchall()
            return [
                Evidence(
                    evidence_id=row["evidence_id"],
                    claim=row["claim"],
                    passage_ids=json.loads(row["passage_ids_json"]),
                    relevance_score=row["relevance_score"] or 0.0,
                    source_domain=row["source_domain"],
                    source_signals=json.loads(row["source_signals_json"] or "{}"),
                    corroboration_group=row["corroboration_group"],
                    notes=row["notes"],
                )
                for row in rows
            ]

    def save_citations(self, run_id: str, citations: List[Citation]) -> None:
        """Insert or replace citations."""
        with self.db.get_connection() as conn:
            conn.executemany(
                """
                INSERT OR REPLACE INTO citations
                (citation_id, run_id, document_id, passage_ids_json, url, access_date, display_metadata_json)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        c.citation_id,
                        run_id,
                        c.document_id,
                        json.dumps(c.passage_ids),
                        c.url,
                        c.access_date,
                        json.dumps(c.display_metadata),
                    )
                    for c in citations
                ],
            )

    def get_citations(self, run_id: str) -> List[Citation]:
        """Retrieve citations for a run."""
        with self.db.get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM citations WHERE run_id = ?", (run_id,)
            ).fetchall()
            return [
                Citation(
                    citation_id=row["citation_id"],
                    document_id=row["document_id"],
                    passage_ids=json.loads(row["passage_ids_json"]),
                    url=row["url"],
                    access_date=row["access_date"],
                    display_metadata=json.loads(row["display_metadata_json"] or "{}"),
                )
                for row in rows
            ]

    def save_report(self, run_id: str, report: ResearchReport) -> None:
        """Persist synthesized report JSON directly into the research_runs record."""
        with self.db.get_connection() as conn:
            conn.execute(
                """
                UPDATE research_runs
                SET report_json = ?, summary = ?
                WHERE run_id = ?
                """,
                (report.model_dump_json(), report.executive_summary[:300], run_id),
            )

    def get_report(self, run_id: str) -> Optional[ResearchReport]:
        """Retrieve the synthesized report for a run if available."""
        with self.db.get_connection() as conn:
            row = conn.execute(
                "SELECT report_json FROM research_runs WHERE run_id = ?", (run_id,)
            ).fetchone()
            if not row or not row["report_json"]:
                return None
            try:
                data = json.loads(row["report_json"])
                return ResearchReport(**data)
            except Exception:
                return None
