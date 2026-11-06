"""Open-source RSS/Atom news discovery client without paid APIs."""

import logging
from typing import List, Optional
import xml.etree.ElementTree as ET
import httpx
from app.config import get_settings
from evidence.schemas import SearchResult

logger = logging.getLogger(__name__)

# Representative public RSS news feeds
DEFAULT_RSS_FEEDS = [
    "https://feeds.bbci.co.uk/news/world/rss.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    "https://feeds.npr.org/1001/rss.xml",
]


class RSSNewsClient:
    """Discovers current news articles from public RSS/Atom feeds using keyword filtering."""

    def __init__(
        self,
        feed_urls: Optional[List[str]] = None,
        timeout: Optional[int] = None,
    ):
        settings = get_settings()
        self.feed_urls = feed_urls or DEFAULT_RSS_FEEDS
        self.timeout = timeout or settings.request_timeout
        self.user_agent = settings.user_agent

    async def search_news(
        self,
        query: str,
        query_id: str = "q-news",
        max_results: int = 10,
    ) -> List[SearchResult]:
        """Fetch RSS feeds and filter stories containing query keywords."""
        keywords = [k.lower() for k in query.split() if len(k) > 2]
        results: List[SearchResult] = []
        rank = 1

        headers = {"User-Agent": self.user_agent}

        async with httpx.AsyncClient(timeout=float(self.timeout), follow_redirects=True) as client:
            for feed_url in self.feed_urls:
                try:
                    resp = await client.get(feed_url, headers=headers)
                    if resp.status_code != 200:
                        continue

                    # Parse XML safely
                    root = ET.fromstring(resp.content)

                    # Support standard RSS <item> tags
                    items = root.findall(".//item")
                    # If not RSS, check Atom <entry> tags
                    if not items:
                        items = root.findall(".//{http://www.w3.org/2005/Atom}entry")

                    for item in items:
                        # Extract title
                        title_el = item.find("title") or item.find("{http://www.w3.org/2005/Atom}title")
                        title = title_el.text.strip() if title_el is not None and title_el.text else ""

                        # Extract link
                        link_el = item.find("link") or item.find("{http://www.w3.org/2005/Atom}link")
                        link = ""
                        if link_el is not None:
                            link = link_el.attrib.get("href", "") or (link_el.text or "").strip()

                        # Extract description / summary
                        desc_el = (
                            item.find("description")
                            or item.find("summary")
                            or item.find("{http://www.w3.org/2005/Atom}summary")
                        )
                        desc = desc_el.text.strip() if desc_el is not None and desc_el.text else ""

                        if not link or not title:
                            continue

                        # Check if any keyword matches title or description
                        target_text = f"{title} {desc}".lower()
                        if not keywords or any(kw in target_text for kw in keywords):
                            results.append(
                                SearchResult(
                                    query_id=query_id,
                                    rank=rank,
                                    engine="rss_news",
                                    title=title,
                                    snippet=desc[:300],
                                    url=link,
                                )
                            )
                            rank += 1
                            if len(results) >= max_results:
                                return results

                except Exception as exc:
                    logger.debug("Failed to read RSS feed %s: %s", feed_url, exc)
                    continue

        return results
