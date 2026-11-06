"""Free web search client using DuckDuckGo HTML and Lite endpoints without API keys or Docker."""

import logging
import re
from typing import Any, Dict, List, Optional
from urllib.parse import parse_qs, unquote, urlparse
import httpx
from lxml import html

from app.config import get_settings
from evidence.schemas import SearchResult

logger = logging.getLogger(__name__)

# Standard browser User-Agent to ensure DuckDuckGo returns full result cards
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/128.0.0.0 Safari/537.36"
)


class DuckDuckGoClient:
    """Client for querying DuckDuckGo public search without API keys or Docker dependencies."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout: Optional[int] = None,
        user_agent: Optional[str] = None,
    ):
        settings = get_settings()
        self.base_url = (base_url or getattr(settings, "duckduckgo_url", "https://html.duckduckgo.com/html/")).rstrip("/")
        self.timeout = timeout or settings.request_timeout
        self.user_agent = user_agent or DEFAULT_USER_AGENT

    async def check_health(self) -> Dict[str, Any]:
        """Check whether the DuckDuckGo search endpoint is reachable."""
        try:
            async with httpx.AsyncClient(timeout=4.0, follow_redirects=True) as client:
                resp = await client.get(
                    self.base_url,
                    params={"q": "ping"},
                    headers={"User-Agent": self.user_agent},
                )
                if resp.status_code == 200:
                    return {
                        "status": "ok",
                        "reachable": True,
                        "provider": "duckduckgo",
                        "message": "DuckDuckGo free search is active and reachable (no Docker required).",
                    }
                else:
                    return {
                        "status": "degraded",
                        "reachable": True,
                        "provider": "duckduckgo",
                        "message": f"DuckDuckGo returned HTTP status {resp.status_code}.",
                    }
        except httpx.ConnectError:
            return {
                "status": "unreachable",
                "reachable": False,
                "provider": "duckduckgo",
                "message": "Could not connect to DuckDuckGo search service (check internet access).",
            }
        except Exception as exc:
            return {
                "status": "error",
                "reachable": False,
                "provider": "duckduckgo",
                "message": f"DuckDuckGo probe failed: {str(exc)}",
            }

    async def search(
        self,
        query: str,
        query_id: str = "q-default",
        max_results: int = 10,
    ) -> List[SearchResult]:
        """Execute a search query against DuckDuckGo.

        Args:
            query: Natural language search terms.
            query_id: Sub-query identifier tagging result provenance.
            max_results: Maximum candidate search results to return.

        Returns:
            List of SearchResult objects, or empty list on network/parsing error.
        """
        clean_query = query.strip()
        if not clean_query:
            return []

        headers = {
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }

        # Primary attempt: html.duckduckgo.com/html/
        results = await self._fetch_html_results(clean_query, query_id, max_results, headers)
        if results:
            return results

        # Fallback attempt: lite.duckduckgo.com/lite/
        logger.info("Retrying DuckDuckGo search using lite endpoint for query: %s", clean_query)
        lite_results = await self._fetch_lite_results(clean_query, query_id, max_results, headers)
        return lite_results

    async def _fetch_html_results(
        self,
        query: str,
        query_id: str,
        max_results: int,
        headers: Dict[str, str],
    ) -> List[SearchResult]:
        """Fetch and parse results from html.duckduckgo.com/html/."""
        url = self.base_url if "duckduckgo.com" in self.base_url else "https://html.duckduckgo.com/html/"
        try:
            async with httpx.AsyncClient(timeout=float(self.timeout), follow_redirects=True) as client:
                # DuckDuckGo HTML endpoint accepts both GET and POST with 'q'
                resp = await client.post(url, data={"q": query}, headers=headers)
                if resp.status_code != 200:
                    logger.warning("DuckDuckGo HTML search returned status %s for query '%s'", resp.status_code, query)
                    return []

                return self._parse_html_body(resp.text, query_id, max_results)

        except httpx.TimeoutException:
            logger.warning("DuckDuckGo search timed out after %s seconds.", self.timeout)
            return []
        except Exception as exc:
            logger.warning("DuckDuckGo search error: %s", exc)
            return []

    async def _fetch_lite_results(
        self,
        query: str,
        query_id: str,
        max_results: int,
        headers: Dict[str, str],
    ) -> List[SearchResult]:
        """Fetch and parse results from lite.duckduckgo.com/lite/."""
        url = "https://lite.duckduckgo.com/lite/"
        try:
            async with httpx.AsyncClient(timeout=float(self.timeout), follow_redirects=True) as client:
                resp = await client.post(url, data={"q": query}, headers=headers)
                if resp.status_code != 200:
                    return []
                return self._parse_lite_body(resp.text, query_id, max_results)
        except Exception as exc:
            logger.warning("DuckDuckGo Lite search error: %s", exc)
            return []

    def _parse_html_body(self, html_text: str, query_id: str, max_results: int) -> List[SearchResult]:
        """Parse standard DuckDuckGo HTML results page."""
        results: List[SearchResult] = []
        if not html_text:
            return results

        try:
            tree = html.fromstring(html_text)
            # Find result containers
            result_elements = tree.xpath('//div[contains(@class, "result ")]')
            rank = 1

            for el in result_elements:
                title_nodes = el.xpath('.//h2/a[contains(@class, "result__a")]')
                if not title_nodes:
                    continue

                title = title_nodes[0].text_content().strip()
                raw_href = title_nodes[0].get("href", "")

                dest_url = self._extract_destination_url(raw_href)
                if not dest_url or not dest_url.startswith(("http://", "https://")):
                    continue

                snippet_nodes = el.xpath('.//a[contains(@class, "result__snippet")]')
                snippet = snippet_nodes[0].text_content().strip() if snippet_nodes else ""

                results.append(
                    SearchResult(
                        query_id=query_id,
                        rank=rank,
                        engine="duckduckgo",
                        title=title or "Untitled",
                        snippet=snippet,
                        url=dest_url,
                    )
                )
                rank += 1
                if len(results) >= max_results:
                    break

        except Exception as exc:
            logger.warning("Failed parsing DuckDuckGo HTML response: %s", exc)

        return results

    def _parse_lite_body(self, html_text: str, query_id: str, max_results: int) -> List[SearchResult]:
        """Parse DuckDuckGo Lite table-based results page."""
        results: List[SearchResult] = []
        if not html_text:
            return results

        try:
            tree = html.fromstring(html_text)
            links = tree.xpath('//a[contains(@class, "result-link")]')
            snippets = tree.xpath('//td[contains(@class, "result-snippet")]')
            rank = 1

            for idx, link_el in enumerate(links):
                title = link_el.text_content().strip()
                raw_href = link_el.get("href", "")
                dest_url = self._extract_destination_url(raw_href)

                if not dest_url or not dest_url.startswith(("http://", "https://")):
                    continue

                snippet = snippets[idx].text_content().strip() if idx < len(snippets) else ""

                results.append(
                    SearchResult(
                        query_id=query_id,
                        rank=rank,
                        engine="duckduckgo_lite",
                        title=title or "Untitled",
                        snippet=snippet,
                        url=dest_url,
                    )
                )
                rank += 1
                if len(results) >= max_results:
                    break

        except Exception as exc:
            logger.warning("Failed parsing DuckDuckGo Lite response: %s", exc)

        return results

    @staticmethod
    def _extract_destination_url(raw_href: str) -> str:
        """Decode destination URL from DuckDuckGo redirect link: //duckduckgo.com/l/?uddg=<url>."""
        if not raw_href:
            return ""

        # Normalize protocol-relative URL
        if raw_href.startswith("//"):
            raw_href = "https:" + raw_href

        if "uddg=" in raw_href:
            try:
                parsed = urlparse(raw_href)
                qs = parse_qs(parsed.query)
                if "uddg" in qs and qs["uddg"]:
                    return unquote(qs["uddg"][0])
            except Exception:
                pass

        # If it's already a direct web URL
        if raw_href.startswith(("http://", "https://")) and "duckduckgo.com/l/" not in raw_href:
            return raw_href

        return ""
