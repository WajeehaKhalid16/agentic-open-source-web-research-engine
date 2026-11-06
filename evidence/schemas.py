"""Data contracts and schemas for research entities, evidence, and citations."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


def utc_now_iso() -> str:
    """Return current UTC timestamp in ISO 8601 format."""
    return datetime.now(timezone.utc).isoformat()


class ResearchRun(BaseModel):
    """Represents a discrete research mission lifecycle."""

    run_id: str = Field(description="Unique run identifier (UUID or timestamped slug).")
    query: str = Field(description="The primary natural language research question.")
    constraints: Dict[str, Any] = Field(
        default_factory=dict,
        description="Search constraints such as date range, language, max sources.",
    )
    start_time: str = Field(default_factory=utc_now_iso)
    end_time: Optional[str] = None
    budgets: Dict[str, int] = Field(
        default_factory=lambda: {"max_sources": 10, "max_rounds": 2},
        description="Enforced resource bounds.",
    )
    model_version: str = Field(
        default="local-ollama",
        description="LLM identifier or synthesis mode used.",
    )
    status: str = Field(
        default="pending",
        description="Status: pending, running, completed, failed.",
    )
    summary: Optional[str] = Field(
        default=None,
        description="Brief status or executive overview summary.",
    )
    report_json: Optional[str] = Field(
        default=None,
        description="Serialized JSON string of synthesized ResearchReport.",
    )
    warnings_json: Optional[str] = Field(
        default=None,
        description="Serialized JSON list of run warnings.",
    )


class SearchResult(BaseModel):
    """Raw search engine discovery record."""

    query_id: str = Field(description="Sub-query identifier generating this result.")
    rank: int = Field(ge=1, description="Rank position in search engine result list.")
    engine: str = Field(description="Underlying search engine or discovery source.")
    title: str = Field(description="Page title from search snippet.")
    snippet: str = Field(default="", description="Search snippet text.")
    url: str = Field(description="Discovered candidate URL.")
    discovered_at: str = Field(default_factory=utc_now_iso)


class Document(BaseModel):
    """Cleaned web document retrieved and parsed from candidate URL."""

    document_id: str = Field(description="Unique document ID (e.g. SHA-256 of canonical URL).")
    canonical_url: str = Field(description="Canonical normalized URL.")
    domain: str = Field(description="Extracted domain/host of the document.")
    title: str = Field(default="Untitled", description="Extracted document title.")
    author: Optional[str] = Field(default=None, description="Author if discoverable.")
    published_at: Optional[str] = Field(default=None, description="Publication timestamp if detected.")
    retrieved_at: str = Field(default_factory=utc_now_iso)
    language: Optional[str] = Field(default="en", description="Detected language code.")
    content_hash: str = Field(description="SHA-256 hash of extracted clean text.")
    fetch_status: str = Field(default="success", description="Fetch status: success, failed, blocked.")
    raw_text: str = Field(default="", description="Clean main text extracted from HTML.")


class Passage(BaseModel):
    """Citation-stable passage chunk derived from a Document."""

    passage_id: str = Field(description="Unique passage ID (e.g. doc-id-p1).")
    document_id: str = Field(description="Foreign key pointing to parent Document.")
    text: str = Field(description="The extracted passage text content.")
    heading: Optional[str] = Field(default=None, description="Nearest section heading.")
    character_offsets: tuple[int, int] = Field(
        default=(0, 0),
        description="Start and end character offsets in parent document text.",
    )
    passage_hash: str = Field(description="SHA-256 hash of passage text for tampering detection.")


class Evidence(BaseModel):
    """Claim or topic linked to supporting passage identifiers."""

    evidence_id: str = Field(description="Unique evidence identifier.")
    claim: str = Field(description="Extracted factual claim or thematic point.")
    passage_ids: List[str] = Field(
        default_factory=list,
        description="List of passage IDs that substantiate this claim.",
    )
    relevance_score: float = Field(default=0.0, ge=0.0, description="Computed relevance score.")
    source_signals: Dict[str, Any] = Field(
        default_factory=dict,
        description="Source credibility signals (HTTPS, primary source, freshness).",
    )
    source_domain: Optional[str] = Field(
        default=None,
        description="Extracted publisher domain.",
    )
    corroboration_group: Optional[str] = Field(
        default=None,
        description="Identifier grouping independently corroborated sources.",
    )
    notes: Optional[str] = Field(default=None, description="Caveats or notes on credibility.")


class Citation(BaseModel):
    """Claim-level citation linking report claims to stored evidence."""

    citation_id: str = Field(description="Citation index or marker ID (e.g. cit-1).")
    document_id: str = Field(description="Parent Document ID.")
    passage_ids: List[str] = Field(description="Specific passage IDs providing direct support.")
    url: str = Field(description="Canonical source URL.")
    access_date: str = Field(default_factory=utc_now_iso)
    display_metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Display information (title, publisher/domain, author, publish date).",
    )


class CitationAudit(BaseModel):
    """Verification results for a citation claim."""

    citation_id: str
    exists_in_store: bool
    url_matches: bool
    passage_found: bool
    substantiated: bool
    citation_verified: bool = Field(
        default=False,
        description="True if document exists, URL is authentic, and passage IDs exist in store.",
    )
    detail: str


class ResearchReport(BaseModel):
    """Complete synthesized research report."""

    run_id: str
    query: str
    title: str
    executive_summary: str
    thematic_findings: List[Dict[str, Any]] = Field(default_factory=list)
    recent_news: Optional[List[Dict[str, Any]]] = Field(default=None)
    disagreements_and_uncertainty: List[str] = Field(default_factory=list)
    conclusion: str = ""
    limitations: List[str] = Field(default_factory=list)
    citations: List[Citation] = Field(default_factory=list)
    sources: List[Document] = Field(default_factory=list)
    unverified_claims: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    created_at: str = Field(default_factory=utc_now_iso)


class ResearchRequest(BaseModel):
    """Request payload for starting a research run."""

    query: str = Field(
        ...,
        min_length=3,
        max_length=1000,
        description="The research question to investigate.",
        examples=["What are the recent applications of AI in disaster management?"],
    )
    max_sources: Optional[int] = Field(
        default=None,
        ge=1,
        le=20,
        description="Maximum number of sources to fetch (defaults to configuration limit).",
    )
    include_news: Optional[bool] = Field(
        default=True,
        description="Whether to supplement search results with RSS news feeds.",
    )


class ResearchResponse(BaseModel):
    """Response payload returned upon executing a research mission."""

    research_id: str
    status: str
    query: str
    report: Optional[ResearchReport] = None
    sources: List[Document] = Field(default_factory=list)
    evidence: List[Evidence] = Field(default_factory=list)
    audits: List[CitationAudit] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    exported_files: Dict[str, str] = Field(default_factory=dict)
    download_links: Dict[str, str] = Field(default_factory=dict)
