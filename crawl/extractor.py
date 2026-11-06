"""Text and metadata extraction from HTML using Trafilatura."""

import hashlib
import re
from typing import Optional
from urllib.parse import urlparse
import trafilatura
from trafilatura.metadata import extract_metadata

from evidence.schemas import Document


def extract_article_content(
    html: str,
    url: str,
    fallback_title: Optional[str] = None,
) -> Document:
    """Extract clean readability-optimized article text and metadata from raw HTML.

    Args:
        html: Raw HTML string downloaded from web page.
        url: The canonical or source URL.
        fallback_title: Title from search snippet if metadata extraction misses it.

    Returns:
        Structured Document object containing clean text and provenance metadata.
    """
    if not html:
        parsed_url = urlparse(url)
        return Document(
            document_id=hashlib.sha256(url.encode()).hexdigest()[:16],
            canonical_url=url,
            domain=parsed_url.netloc,
            title=fallback_title or "Empty Document",
            raw_text="",
            content_hash=hashlib.sha256(b"").hexdigest(),
            fetch_status="empty",
        )

    # 1. Extract metadata (title, author, publication date, language)
    meta = extract_metadata(html, default_url=url)
    
    extracted_title = meta.title if meta and meta.title else fallback_title or "Untitled Document"
    extracted_author = meta.author if meta and meta.author else None
    extracted_date = meta.date if meta and meta.date else None
    extracted_lang = meta.language if meta and meta.language else "en"

    # 2. Extract clean main text using Trafilatura
    # config options: favor recall of factual prose, strip tables/comments if junk
    extracted_text = trafilatura.extract(
        html,
        url=url,
        include_comments=False,
        include_tables=True,
        no_fallback=False,
        output_format="txt",
    )

    if not extracted_text:
        # Fallback regex extraction of visible paragraphs if trafilatura finds no main article
        body_chunks = re.findall(r"<p[^>]*>(.*?)</p>", html, flags=re.IGNORECASE | re.DOTALL)
        clean_chunks = []
        for chunk in body_chunks:
            # Strip tags
            cleaned = re.sub(r"<[^>]+>", " ", chunk)
            cleaned = re.sub(r"\s+", " ", cleaned).strip()
            if len(cleaned) > 25:
                clean_chunks.append(cleaned)
        extracted_text = "\n\n".join(clean_chunks)

    clean_text = (extracted_text or "").strip()
    content_hash = hashlib.sha256(clean_text.encode("utf-8")).hexdigest()
    parsed_domain = urlparse(url).netloc.lower()

    # Document ID is a stable hash of the canonical URL
    doc_id = hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]

    return Document(
        document_id=doc_id,
        canonical_url=url,
        domain=parsed_domain,
        title=extracted_title,
        author=extracted_author,
        published_at=extracted_date,
        language=extracted_lang,
        content_hash=content_hash,
        fetch_status="success" if clean_text else "no_content",
        raw_text=clean_text,
    )
