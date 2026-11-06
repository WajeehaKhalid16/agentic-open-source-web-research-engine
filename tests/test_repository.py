"""Tests for SQLite database initialization, migrations, and repository operations."""

import gc
import os
import shutil
import tempfile
import pytest

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
from storage.repository import ResearchRepository


@pytest.fixture
def temp_repo():
    """Create a temporary SQLite database for testing with Windows-safe cleanup."""
    tmp_dir = tempfile.mkdtemp()
    db_path = os.path.join(tmp_dir, "test_research.db")
    db = Database(db_path=db_path)
    repo = ResearchRepository(db=db)
    yield repo
    gc.collect()
    shutil.rmtree(tmp_dir, ignore_errors=True)


def test_repository_run_lifecycle(temp_repo: ResearchRepository):
    """Verify research run persistence, update, and retrieval."""
    run = ResearchRun(
        run_id="run-repo-test-1",
        query="Quantum computing cryptography algorithms",
        constraints={"max_sources": 5},
        status="running",
    )
    temp_repo.save_run(run)

    retrieved = temp_repo.get_run("run-repo-test-1")
    assert retrieved is not None
    assert retrieved.run_id == "run-repo-test-1"
    assert retrieved.query == "Quantum computing cryptography algorithms"
    assert retrieved.status == "running"

    temp_repo.update_run_status(
        run_id="run-repo-test-1",
        status="completed",
        summary="Quantum computing threatens RSA encryption.",
    )
    updated = temp_repo.get_run("run-repo-test-1")
    assert updated.status == "completed"
    assert updated.summary == "Quantum computing threatens RSA encryption."


def test_repository_search_and_documents(temp_repo: ResearchRepository):
    """Verify persistence of search results and cleaned documents."""
    run_id = "run-repo-test-2"
    run = ResearchRun(run_id=run_id, query="Test Query")
    temp_repo.save_run(run)

    # Search Results
    sr = SearchResult(
        query_id="q1",
        rank=1,
        engine="searxng",
        title="Test Search Result",
        snippet="Snippet text",
        url="https://example.org/doc1",
    )
    temp_repo.save_search_results(run_id, [sr])
    results = temp_repo.get_search_results(run_id)
    assert len(results) == 1
    assert results[0].url == "https://example.org/doc1"

    # Documents
    doc = Document(
        document_id="doc1",
        canonical_url="https://example.org/doc1",
        domain="example.org",
        title="Test Doc Title",
        content_hash="hash123",
        raw_text="Extracted document body text.",
    )
    temp_repo.save_documents(run_id, [doc])
    docs = temp_repo.get_documents(run_id)
    assert len(docs) == 1
    assert docs[0].title == "Test Doc Title"


def test_repository_passages_and_evidence(temp_repo: ResearchRepository):
    """Verify persistence of passages and ranked evidence."""
    run_id = "run-repo-test-3"
    run = ResearchRun(run_id=run_id, query="Test Query")
    temp_repo.save_run(run)

    # Need a parent document first due to FOREIGN KEY constraint
    doc = Document(
        document_id="doc-p1",
        canonical_url="https://example.org/doc-p1",
        domain="example.org",
        title="Doc P1",
        content_hash="hashdoc1",
        raw_text="Some text for passage testing.",
    )
    temp_repo.save_documents(run_id, [doc])

    # Passages
    p = Passage(
        passage_id="doc-p1-p1",
        document_id="doc-p1",
        text="Some text for passage testing.",
        character_offsets=(0, 31),
        passage_hash="hashpassage1",
    )
    temp_repo.save_passages(run_id, [p])
    passages = temp_repo.get_passages(run_id)
    assert len(passages) == 1
    assert passages[0].passage_id == "doc-p1-p1"

    # Evidence
    ev = Evidence(
        evidence_id="ev-1",
        claim="Passage testing demonstrates reliability.",
        passage_ids=["doc-p1-p1"],
        relevance_score=3.85,
        source_domain="example.org",
        source_signals={"is_primary": True},
    )
    temp_repo.save_evidence(run_id, [ev])
    ev_list = temp_repo.get_evidence(run_id)
    assert len(ev_list) == 1
    assert ev_list[0].evidence_id == "ev-1"
    assert ev_list[0].relevance_score == 3.85
    assert ev_list[0].source_domain == "example.org"


def test_repository_report_serialization(temp_repo: ResearchRepository):
    """Verify storing and retrieving complete synthesized report objects."""
    run_id = "run-repo-test-4"
    run = ResearchRun(run_id=run_id, query="Test Report Run")
    temp_repo.save_run(run)

    report = ResearchReport(
        run_id=run_id,
        query="Test Report Run",
        title="Synthesized Test Report",
        executive_summary="Key factual overview.",
        thematic_findings=[{"theme": "General", "findings": ["Finding A"]}],
        limitations=["Small sample size."],
    )
    temp_repo.save_report(run_id, report)

    loaded_report = temp_repo.get_report(run_id)
    assert loaded_report is not None
    assert loaded_report.title == "Synthesized Test Report"
    assert loaded_report.executive_summary == "Key factual overview."
    assert len(loaded_report.thematic_findings) == 1
