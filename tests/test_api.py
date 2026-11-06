"""Tests for FastAPI endpoints and research API workflow with mocked external services."""

import json
from unittest.mock import AsyncMock, patch
import pytest
from fastapi.testclient import TestClient

from app.main import app
from crawl.fetcher import FetchResult
from evidence.schemas import SearchResult
from ui.streamlit_app import check_api_health

client = TestClient(app)


def test_root_endpoint():
    """Verify that root endpoint returns status ready and application name."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert "name" in data
    assert "version" in data


def test_health_endpoint():
    """Verify health check probe returns ok status."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_public_config_endpoint():
    """Verify config endpoint returns public settings and does not expose secrets."""
    response = client.get("/api/config")
    assert response.status_code == 200
    data = response.json()

    assert "app_name" in data
    assert "max_sources" in data
    assert "max_search_rounds" in data
    assert "request_timeout" in data
    assert "search_provider" in data

    # Verify sensitive attributes or internal paths are never exposed
    assert "secret" not in data
    assert "password" not in data
    assert "token" not in data


def test_create_research_validation_errors():
    """Verify input validation for POST /api/research."""
    # Query too short
    resp1 = client.post("/api/research", json={"query": "ab", "max_sources": 5})
    assert resp1.status_code == 422

    # Query empty
    resp2 = client.post("/api/research", json={"query": "", "max_sources": 5})
    assert resp2.status_code == 422

    # max_sources out of bounds (< 1)
    resp3 = client.post("/api/research", json={"query": "valid query", "max_sources": 0})
    assert resp3.status_code == 422

    # max_sources out of bounds (> 20)
    resp4 = client.post("/api/research", json={"query": "valid query", "max_sources": 50})
    assert resp4.status_code == 422


@patch("search.duckduckgo_client.DuckDuckGoClient.search")
@patch("search.duckduckgo_client.DuckDuckGoClient.check_health")
@patch("crawl.fetcher.SafeFetcher.fetch")
def test_create_research_success_and_retrieval(mock_fetch, mock_check_health, mock_search):
    """Verify end-to-end research flow via POST /api/research and GET inspection endpoints."""
    mock_check_health.return_value = {
        "status": "ok",
        "reachable": True,
        "provider": "duckduckgo",
        "message": "DuckDuckGo active",
    }

    # Mock search results
    mock_search.return_value = [
        SearchResult(
            query_id="sq-1",
            rank=1,
            engine="duckduckgo",
            title="AI in Disaster Response Overview",
            snippet="Drones and satellite imagery use machine learning to map flood damage.",
            url="https://example.org/disaster-ai",
        ),
        SearchResult(
            query_id="sq-1",
            rank=2,
            engine="duckduckgo",
            title="Early Warning AI Systems",
            snippet="Seismic sensor arrays deploy neural networks for rapid tsunami alert generation.",
            url="https://example.gov/early-warning",
        ),
    ]

    # Mock HTML pages fetched
    html1 = """
    <html><head><title>AI in Disaster Response</title></head>
    <body>
    <article>
        <h1>AI in Disaster Response Overview</h1>
        <p>Unmanned aerial vehicles and satellite imagery use deep learning algorithms to map flood damage across regional basins rapidly.</p>
        <p>Real-time resource allocation systems route emergency first responders to prioritized survival sectors.</p>
    </article>
    </body></html>
    """
    html2 = """
    <html><head><title>Early Warning AI Systems</title></head>
    <body>
    <article>
        <h1>Early Warning AI Systems</h1>
        <p>Seismic sensor arrays deploy recurrent neural networks for rapid tsunami alert generation within seconds of seabed movement.</p>
        <p>Automated communication beacons alert coastal populations with localized evacuation waypoints.</p>
    </article>
    </body></html>
    """

    async def side_effect_fetch(url: str):
        if "disaster-ai" in url:
            return FetchResult(
                url=url,
                canonical_url=url,
                status_code=200,
                content=html1,
                content_type="text/html",
                success=True,
            )
        elif "early-warning" in url:
            return FetchResult(
                url=url,
                canonical_url=url,
                status_code=200,
                content=html2,
                content_type="text/html",
                success=True,
            )
        return FetchResult(url=url, canonical_url=url, success=False, error="Not found")

    mock_fetch.side_effect = side_effect_fetch

    # 1. POST /api/research
    payload = {
        "query": "What are the recent applications of AI in disaster management?",
        "max_sources": 2,
        "include_news": False,
    }
    response = client.post("/api/research", json=payload)
    assert response.status_code == 200
    data = response.json()

    run_id = data["research_id"]
    assert run_id.startswith("run-")
    assert data["status"] == "completed"
    assert len(data["sources"]) == 2
    assert len(data["evidence"]) >= 1
    assert data["report"] is not None
    assert len(data["audits"]) >= 1

    # Verify citation verification integrity
    for audit in data["audits"]:
        assert audit["citation_verified"] is True
        assert audit["exists_in_store"] is True
        assert audit["url_matches"] is True
        assert audit["passage_found"] is True

    # 2. GET /api/research/{run_id}
    get_resp = client.get(f"/api/research/{run_id}")
    assert get_resp.status_code == 200
    run_data = get_resp.json()
    assert run_data["research_id"] == run_id
    assert run_data["status"] == "completed"
    assert run_data["report"] is not None
    assert len(run_data["sources"]) == 2

    # 3. GET /api/research/{run_id}/sources
    sources_resp = client.get(f"/api/research/{run_id}/sources")
    assert sources_resp.status_code == 200
    sources_data = sources_resp.json()
    assert sources_data["count"] == 2
    assert sources_data["sources"][0]["canonical_url"] == "https://example.org/disaster-ai"

    # 4. GET /api/research/{run_id}/evidence
    evidence_resp = client.get(f"/api/research/{run_id}/evidence")
    assert evidence_resp.status_code == 200
    ev_data = evidence_resp.json()
    assert ev_data["evidence_count"] >= 1
    assert ev_data["passages_count"] >= 1

    # 5. GET /api/research/{run_id}/export/md
    md_resp = client.get(f"/api/research/{run_id}/export/md")
    assert md_resp.status_code == 200
    assert "text/markdown" in md_resp.headers["content-type"]
    assert "AI in disaster management" in md_resp.text

    # 6. GET /api/research/{run_id}/export/html
    html_resp = client.get(f"/api/research/{run_id}/export/html")
    assert html_resp.status_code == 200
    assert "text/html" in html_resp.headers["content-type"]
    assert "<!DOCTYPE html>" in html_resp.text

    # 7. GET /api/research/{run_id}/export/json
    json_resp = client.get(f"/api/research/{run_id}/export/json")
    assert json_resp.status_code == 200
    assert "application/json" in json_resp.headers["content-type"]
    exported_json = json_resp.json()
    assert exported_json["run_id"] == run_id


def test_get_nonexistent_and_invalid_research_ids():
    """Verify 404 and 400 status codes for missing or malicious research IDs."""
    # Nonexistent run ID
    resp404 = client.get("/api/research/run-doesnotexist123")
    assert resp404.status_code == 404

    # Nonexistent sources
    resp_src_404 = client.get("/api/research/run-doesnotexist123/sources")
    assert resp_src_404.status_code == 404

    # Nonexistent evidence
    resp_ev_404 = client.get("/api/research/run-doesnotexist123/evidence")
    assert resp_ev_404.status_code == 404

    # Invalid ID with path traversal attempt
    resp_malformed = client.get("/api/research/../../etc/passwd")
    assert resp_malformed.status_code in (400, 404)

    # Invalid export format
    resp_bad_fmt = client.get("/api/research/run-doesnotexist123/export/exe")
    assert resp_bad_fmt.status_code == 400


@patch("search.duckduckgo_client.DuckDuckGoClient.search")
@patch("search.duckduckgo_client.DuckDuckGoClient.check_health")
@patch("search.news_client.RSSNewsClient.search_news")
def test_create_research_no_search_results(mock_news, mock_health, mock_search):
    """Verify graceful handling when both search and RSS return zero results."""
    mock_health.return_value = {"status": "unreachable", "reachable": False, "provider": "duckduckgo"}
    mock_search.return_value = []
    mock_news.return_value = []

    payload = {
        "query": "Extremely obscure query returning zero web hits",
        "max_sources": 5,
        "include_news": True,
    }
    response = client.post("/api/research", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "completed"
    assert len(data["sources"]) == 0
    assert len(data["evidence"]) == 0
    assert "No relevant evidence" in data["report"]["executive_summary"]
    assert any("Search provider is unreachable" in w or "No candidate search results" in w for w in data["warnings"])


@patch("search.duckduckgo_client.DuckDuckGoClient.search")
@patch("search.duckduckgo_client.DuckDuckGoClient.check_health")
@patch("crawl.fetcher.SafeFetcher.fetch")
def test_create_research_individual_fetch_failure(mock_fetch, mock_health, mock_search):
    """Verify that a single source failure does not abort the entire research mission."""
    mock_health.return_value = {"status": "ok", "reachable": True, "provider": "duckduckgo"}
    mock_search.return_value = [
        SearchResult(
            query_id="sq-1",
            rank=1,
            engine="duckduckgo",
            title="Broken Website",
            snippet="This page will fail to fetch.",
            url="https://example.org/broken",
        ),
        SearchResult(
            query_id="sq-1",
            rank=2,
            engine="duckduckgo",
            title="Working Website",
            snippet="This page will fetch successfully.",
            url="https://example.org/working",
        ),
    ]

    async def side_effect_fetch(url: str):
        if "broken" in url:
            return FetchResult(
                url=url,
                canonical_url=url,
                status_code=500,
                success=False,
                error="HTTP Status 500",
            )
        return FetchResult(
            url=url,
            canonical_url=url,
            status_code=200,
            content="<html><body><p>Working reliable evidence on climate adaptation strategies.</p></body></html>",
            content_type="text/html",
            success=True,
        )

    mock_fetch.side_effect = side_effect_fetch

    payload = {
        "query": "Climate adaptation strategies",
        "max_sources": 2,
        "include_news": False,
    }
    response = client.post("/api/research", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "completed"
    assert len(data["sources"]) == 1
    assert data["sources"][0]["canonical_url"] == "https://example.org/working"
    assert any("Failed to fetch" in w for w in data["warnings"])


@patch("search.duckduckgo_client.DuckDuckGoClient.search")
@patch("search.duckduckgo_client.DuckDuckGoClient.check_health")
@patch("crawl.fetcher.SafeFetcher.fetch")
def test_create_research_empty_or_unusable_extracted_content(mock_fetch, mock_health, mock_search):
    """Verify that web pages returning empty or whitespace-only content do not cause pipeline errors."""
    mock_health.return_value = {"status": "ok", "reachable": True, "provider": "duckduckgo"}
    mock_search.return_value = [
        SearchResult(
            query_id="sq-1",
            rank=1,
            engine="duckduckgo",
            title="Empty Content Page",
            snippet="No readable paragraphs.",
            url="https://example.org/empty-page",
        )
    ]
    mock_fetch.return_value = FetchResult(
        url="https://example.org/empty-page",
        canonical_url="https://example.org/empty-page",
        status_code=200,
        content="<html><body><div><!-- comment only --></div></body></html>",
        content_type="text/html",
        success=True,
    )

    payload = {
        "query": "Zero extraction page",
        "max_sources": 1,
        "include_news": False,
    }
    response = client.post("/api/research", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert len(data["sources"]) == 0
    assert any("no readable text" in w.lower() or "failed retrieval" in w.lower() for w in data["warnings"])


def test_streamlit_api_health_check_offline():
    """Verify Streamlit UI helper handles unreachable API gracefully."""
    result = check_api_health("http://127.0.0.1:99999")
    assert result["online"] is False
    assert result["config"] == {}


def test_runs_api_contract():
    """Verify the /api/runs REST contract returns 202 Accepted and lists runs."""
    payload = {
        "query": "Test cinematic UI research query",
        "mode": "web",
        "max_sources": 3,
    }
    response = client.post("/api/runs", json=payload)
    assert response.status_code == 202
    data = response.json()
    assert "run_id" in data
    assert data["status"] == "pending"
    assert "stream_url" in data
    assert f"/api/runs/{data['run_id']}/events" == data["stream_url"]

    # Verify list runs
    list_res = client.get("/api/runs")
    assert list_res.status_code == 200
    assert isinstance(list_res.json(), list)
