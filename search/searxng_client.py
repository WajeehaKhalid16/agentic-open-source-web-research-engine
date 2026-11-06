"""HTTPX-based client for interacting with a self-hosted SearXNG metasearch instance."""

import logging
from typing import Any, Dict, List, Optional
import httpx
from app.config import get_settings
from evidence.schemas import SearchResult

logger = logging.getLogger(__name__)


class SearXNGClient:
    """Client for querying SearXNG JSON API endpoint with error tolerance."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout: Optional[int] = None,
    ):
        settings = get_settings()
        self.base_url = (base_url or settings.searxng_url).rstrip("/")
        self.timeout = timeout or settings.request_timeout
        self.user_agent = settings.user_agent

    async def check_health(self) -> Dict[str, Any]:
        """Check whether SearXNG service is reachable and whether its JSON API is enabled.

        Returns:
            Dict containing reachable status, json_supported status, and a diagnostic message.
        """
        search_url = f"{self.base_url}/search"
        params = {"q": "ping", "format": "json"}
        headers = {"User-Agent": self.user_agent, "Accept": "application/json"}

        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                resp = await client.get(search_url, params=params, headers=headers)
                if resp.status_code == 200:
                    try:
                        data = resp.json()
                        if "results" in data:
                            return {
                                "status": "ok",
                                "reachable": True,
                                "json_supported": True,
                                "message": f"SearXNG at {self.base_url} is active with JSON format enabled.",
                            }
                    except Exception:
                        pass
                    return {
                        "status": "degraded",
                        "reachable": True,
                        "json_supported": False,
                        "message": "SearXNG responded but did not return valid JSON. Check docker/searxng/settings.yml formats.",
                    }
                elif resp.status_code == 403:
                    return {
                        "status": "misconfigured",
                        "reachable": True,
                        "json_supported": False,
                        "message": "SearXNG responded with 403 Forbidden. Enable 'json' under search.formats in settings.yml.",
                    }
                else:
                    return {
                        "status": "error",
                        "reachable": True,
                        "json_supported": False,
                        "message": f"SearXNG responded with HTTP {resp.status_code}.",
                    }
        except httpx.ConnectError:
            return {
                "status": "unreachable",
                "reachable": False,
                "json_supported": False,
                "message": (
                    f"Could not connect to SearXNG at {self.base_url}. "
                    "Start it using: docker compose up -d"
                ),
            }
        except Exception as exc:
            return {
                "status": "error",
                "reachable": False,
                "json_supported": False,
                "message": f"SearXNG probe failed: {str(exc)}",
            }

    async def search(
        self,
        query: str,
        categories: str = "general",
        pageno: int = 1,
        query_id: str = "q-default",
    ) -> List[SearchResult]:
        """Execute a search query against the SearXNG instance.

        Args:
            query: The search query string.
            categories: Comma-separated category string (e.g. 'general', 'news', 'science').
            pageno: Result page number.
            query_id: Identifier tagging the specific subquestion/query variant.

        Returns:
            List of SearchResult objects. Returns empty list gracefully on network or JSON errors.
        """
        if not query.strip():
            return []

        search_url = f"{self.base_url}/search"
        params: Dict[str, Any] = {
            "q": query,
            "format": "json",
            "categories": categories,
            "pageno": pageno,
        }
        headers = {
            "User-Agent": self.user_agent,
            "Accept": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=float(self.timeout)) as client:
                response = await client.get(search_url, params=params, headers=headers)

                if response.status_code != 200:
                    logger.warning(
                        "SearXNG query returned status %s: %s",
                        response.status_code,
                        response.text[:200],
                    )
                    return []

                data = response.json()
                raw_results = data.get("results", [])

                search_results: List[SearchResult] = []
                for idx, item in enumerate(raw_results, start=1):
                    url = item.get("url")
                    if not url or not url.startswith(("http://", "https://")):
                        continue

                    title = item.get("title", "Untitled")
                    snippet = item.get("content", "") or item.get("snippet", "")
                    engine = item.get("engine", "searxng")

                    search_results.append(
                        SearchResult(
                            query_id=query_id,
                            rank=idx,
                            engine=engine,
                            title=title,
                            snippet=snippet,
                            url=url,
                        )
                    )

                return search_results

        except httpx.ConnectError:
            logger.warning(
                "Could not connect to SearXNG at %s. Ensure SearXNG container is running.",
                self.base_url,
            )
            return []
        except httpx.TimeoutException:
            logger.warning("SearXNG search timed out after %s seconds.", self.timeout)
            return []
        except Exception as exc:
            logger.warning("SearXNG search error: %s", exc)
            return []
