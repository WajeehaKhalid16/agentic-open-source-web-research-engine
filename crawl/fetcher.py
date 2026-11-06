"""Safe, bounded HTTP fetching with SSRF revalidation, timeouts, and size limits."""

import time
from typing import Optional, Set
import httpx
from pydantic import BaseModel

from app.config import get_settings
from crawl.policy import URLSecurityError, canonicalize_url, validate_url_safety

ALLOWED_CONTENT_TYPES: Set[str] = {
    "text/html",
    "application/xhtml+xml",
    "text/plain",
}


class FetchResult(BaseModel):
    """Encapsulates outcome of an HTTP fetch operation."""

    url: str
    canonical_url: str
    status_code: Optional[int] = None
    content: str = ""
    content_type: str = ""
    success: bool = False
    error: Optional[str] = None
    elapsed_seconds: float = 0.0


class SafeFetcher:
    """Retrieves web pages safely enforcing policy checks, size limits, and polite timeouts."""

    def __init__(
        self,
        user_agent: Optional[str] = None,
        timeout: Optional[int] = None,
        max_bytes: Optional[int] = None,
        allow_localhost: bool = False,
    ):
        settings = get_settings()
        self.user_agent = user_agent or settings.user_agent
        self.timeout = timeout or settings.request_timeout
        self.max_bytes = max_bytes or settings.max_content_size_bytes
        self.allow_localhost = allow_localhost

    async def fetch(self, url: str) -> FetchResult:
        """Fetch a single URL asynchronously with strict security controls."""
        start_time = time.perf_counter()
        canonical = canonicalize_url(url)

        # 1. Pre-flight SSRF and scheme validation
        try:
            validate_url_safety(canonical, allow_localhost=self.allow_localhost)
        except URLSecurityError as exc:
            return FetchResult(
                url=url,
                canonical_url=canonical,
                success=False,
                error=f"Security Policy Rejection: {exc}",
                elapsed_seconds=time.perf_counter() - start_time,
            )

        headers = {
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml,text/plain;q=0.9,*/*;q=0.1",
            "Accept-Language": "en-US,en;q=0.9",
        }

        # Follow redirects manually to re-verify destination safety on every hop
        current_url = canonical
        max_redirects = 5

        try:
            async with httpx.AsyncClient(
                headers=headers,
                timeout=float(self.timeout),
                follow_redirects=False,
                verify=True,
            ) as client:
                for _ in range(max_redirects):
                    # Validate current hop
                    validate_url_safety(current_url, allow_localhost=self.allow_localhost)

                    # Stream response to enforce size limit before loading full body
                    async with client.stream("GET", current_url) as response:
                        if response.is_redirect:
                            location = response.headers.get("location")
                            if not location:
                                return FetchResult(
                                    url=url,
                                    canonical_url=canonical,
                                    status_code=response.status_code,
                                    success=False,
                                    error="Redirect header missing location.",
                                    elapsed_seconds=time.perf_counter() - start_time,
                                )
                            # Resolve relative redirects
                            redirect_target = str(response.url.join(location))
                            current_url = canonicalize_url(redirect_target)
                            continue

                        # Check Content-Type header
                        raw_content_type = response.headers.get("content-type", "")
                        media_type = raw_content_type.split(";")[0].strip().lower()
                        if media_type and not any(allowed in media_type for allowed in ALLOWED_CONTENT_TYPES):
                            return FetchResult(
                                url=url,
                                canonical_url=canonical,
                                status_code=response.status_code,
                                content_type=media_type,
                                success=False,
                                error=f"Unsupported content type: {media_type}",
                                elapsed_seconds=time.perf_counter() - start_time,
                            )

                        # Check Content-Length header if present
                        content_length = response.headers.get("content-length")
                        if content_length and int(content_length) > self.max_bytes:
                            return FetchResult(
                                url=url,
                                canonical_url=canonical,
                                status_code=response.status_code,
                                success=False,
                                error=f"Content-Length ({content_length} bytes) exceeds limit ({self.max_bytes} bytes).",
                                elapsed_seconds=time.perf_counter() - start_time,
                            )

                        # Read stream with strict size limit
                        downloaded_bytes = bytearray()
                        async for chunk in response.aiter_bytes():
                            downloaded_bytes.extend(chunk)
                            if len(downloaded_bytes) > self.max_bytes:
                                return FetchResult(
                                    url=url,
                                    canonical_url=canonical,
                                    status_code=response.status_code,
                                    success=False,
                                    error=f"Response exceeded maximum allowed size of {self.max_bytes} bytes.",
                                    elapsed_seconds=time.perf_counter() - start_time,
                                )

                        encoding = response.encoding or "utf-8"
                        text_content = downloaded_bytes.decode(encoding, errors="replace")

                        return FetchResult(
                            url=url,
                            canonical_url=canonical,
                            status_code=response.status_code,
                            content=text_content,
                            content_type=media_type,
                            success=response.is_success,
                            error=None if response.is_success else f"HTTP Status {response.status_code}",
                            elapsed_seconds=time.perf_counter() - start_time,
                        )

                return FetchResult(
                    url=url,
                    canonical_url=canonical,
                    success=False,
                    error=f"Exceeded maximum redirects ({max_redirects}).",
                    elapsed_seconds=time.perf_counter() - start_time,
                )

        except httpx.TimeoutException:
            return FetchResult(
                url=url,
                canonical_url=canonical,
                success=False,
                error=f"Request timed out after {self.timeout} seconds.",
                elapsed_seconds=time.perf_counter() - start_time,
            )
        except Exception as exc:
            return FetchResult(
                url=url,
                canonical_url=canonical,
                success=False,
                error=f"Fetch failed: {str(exc)}",
                elapsed_seconds=time.perf_counter() - start_time,
            )
