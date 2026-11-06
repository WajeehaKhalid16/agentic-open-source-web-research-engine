"""Tests for HTML article extraction and metadata parsing."""

import os
import pytest
from crawl.extractor import extract_article_content


@pytest.fixture
def sample_html() -> str:
    """Load the local sample HTML article fixture."""
    fixture_path = os.path.join(os.path.dirname(__file__), "fixtures", "sample_article.html")
    with open(fixture_path, "r", encoding="utf-8") as f:
        return f.read()


def test_extract_article_content(sample_html: str):
    """Verify that Trafilatura extracts main text, metadata, and computes stable hashes."""
    url = "https://example.org/studies/arid-solar-effects"
    doc = extract_article_content(sample_html, url=url)

    assert doc.document_id is not None
    assert len(doc.document_id) == 16
    assert doc.domain == "example.org"
    assert "Solar" in doc.title
    assert "photovoltaic heat island effect" in doc.raw_text
    assert "agrivoltaics" in doc.raw_text

    # HTML tags must be stripped from clean text
    assert "<article>" not in doc.raw_text
    assert "<h2>" not in doc.raw_text
    assert "<p>" not in doc.raw_text

    # Content hash must be 64-character SHA-256
    assert len(doc.content_hash) == 64
    assert doc.fetch_status == "success"


def test_extract_empty_html():
    """Verify that empty HTML is handled safely without throwing exceptions."""
    doc = extract_article_content("", url="https://example.org/empty")
    assert doc.raw_text == ""
    assert doc.fetch_status == "empty"
    assert doc.domain == "example.org"
