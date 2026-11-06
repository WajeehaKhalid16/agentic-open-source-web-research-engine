"""Offline tests for DuckDuckGo free search client and URL extraction."""

from unittest.mock import AsyncMock, patch
import httpx
import pytest

from search.duckduckgo_client import DuckDuckGoClient

SAMPLE_DDG_HTML = """
<!DOCTYPE html>
<html>
<body>
<div class="results">
    <div class="result results_links results_links_deep web-result">
        <h2 class="result__title">
            <a class="result__a" href="//duckduckgo.com/l/?uddg=https%3A%2F%2Fexample.org%2Fdisaster-ai-tech&rut=abc">
                AI Innovations in Disaster Response
            </a>
        </h2>
        <a class="result__snippet" href="//duckduckgo.com/l/?uddg=https%3A%2F%2Fexample.org%2Fdisaster-ai-tech&rut=abc">
            Machine learning satellite algorithms detect flood zones within minutes.
        </a>
    </div>
    <div class="result results_links results_links_deep web-result">
        <h2 class="result__title">
            <a class="result__a" href="//duckduckgo.com/l/?uddg=https%3A%2F%2Fexample.gov%2Fearly-warning-alert&rut=xyz">
                Seismic Early Warning Systems
            </a>
        </h2>
        <a class="result__snippet" href="//duckduckgo.com/l/?uddg=https%3A%2F%2Fexample.gov%2Fearly-warning-alert&rut=xyz">
            Automated sensor clusters dispatch emergency broadcast notifications.
        </a>
    </div>
</div>
</body>
</html>
"""

SAMPLE_DDG_LITE_HTML = """
<!DOCTYPE html>
<html>
<body>
<table>
    <tr>
        <td>
            <a class="result-link" href="//duckduckgo.com/l/?uddg=https%3A%2F%2Fexample.edu%2Fresearch-paper&rut=123">
                Emergency Robotics Research
            </a>
        </td>
    </tr>
    <tr>
        <td class="result-snippet">
            Autonomous drones assist emergency teams in debris mapping.
        </td>
    </tr>
</table>
</body>
</html>
"""


@pytest.mark.anyio
async def test_duckduckgo_parse_html():
    """Verify DuckDuckGo HTML parsing and uddg URL decoding."""
    client = DuckDuckGoClient()

    with patch("httpx.AsyncClient.post") as mock_post:
        mock_resp = AsyncMock()
        mock_resp.status_code = 200
        mock_resp.text = SAMPLE_DDG_HTML
        mock_post.return_value = mock_resp

        results = await client.search("disaster AI", max_results=5)

        assert len(results) == 2
        assert results[0].title == "AI Innovations in Disaster Response"
        assert results[0].url == "https://example.org/disaster-ai-tech"
        assert "satellite algorithms" in results[0].snippet
        assert results[0].engine == "duckduckgo"
        assert results[0].rank == 1

        assert results[1].title == "Seismic Early Warning Systems"
        assert results[1].url == "https://example.gov/early-warning-alert"
        assert results[1].rank == 2


@pytest.mark.anyio
async def test_duckduckgo_parse_lite_fallback():
    """Verify fallback to Lite endpoint when standard HTML returns empty or error."""
    client = DuckDuckGoClient()

    with patch.object(client, "_fetch_html_results", return_value=[]), \
         patch("httpx.AsyncClient.post") as mock_post:
        mock_resp = AsyncMock()
        mock_resp.status_code = 200
        mock_resp.text = SAMPLE_DDG_LITE_HTML
        mock_post.return_value = mock_resp

        results = await client.search("emergency robotics", max_results=5)
        assert len(results) == 1
        assert results[0].title == "Emergency Robotics Research"
        assert results[0].url == "https://example.edu/research-paper"
        assert results[0].engine == "duckduckgo_lite"


@pytest.mark.anyio
async def test_duckduckgo_empty_query():
    """Verify empty query returns empty list immediately without making network calls."""
    client = DuckDuckGoClient()
    results = await client.search("   ")
    assert results == []


@pytest.mark.anyio
async def test_duckduckgo_timeout_handling():
    """Verify timeout produces a warning and returns empty list without raising exception."""
    client = DuckDuckGoClient()

    with patch("httpx.AsyncClient.post", side_effect=httpx.TimeoutException("Timeout")):
        results = await client.search("timeout query")
        assert results == []


@pytest.mark.anyio
async def test_duckduckgo_health_check():
    """Verify health probe reports reachable status accurately."""
    client = DuckDuckGoClient()

    # Success case
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_resp = AsyncMock()
        mock_resp.status_code = 200
        mock_get.return_value = mock_resp
        health = await client.check_health()
        assert health["status"] == "ok"
        assert health["reachable"] is True
        assert health["provider"] == "duckduckgo"

    # Connection failure case
    with patch("httpx.AsyncClient.get", side_effect=httpx.ConnectError("No internet")):
        health_fail = await client.check_health()
        assert health_fail["status"] == "unreachable"
        assert health_fail["reachable"] is False
