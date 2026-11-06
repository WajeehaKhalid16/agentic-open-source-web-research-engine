"""Typed research state tracking inputs, intermediate artifacts, and outputs across nodes."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from evidence.schemas import (
    CitationAudit,
    Document,
    Evidence,
    Passage,
    ResearchReport,
    SearchResult,
)


class ResearchState(BaseModel):
    """Central typed state for the bounded agentic research graph."""

    run_id: str
    query: str
    constraints: Dict[str, Any] = Field(default_factory=dict)
    subquestions: List[str] = Field(default_factory=list)
    search_results: List[SearchResult] = Field(default_factory=list)
    documents: List[Document] = Field(default_factory=list)
    passages: List[Passage] = Field(default_factory=list)
    evidence_items: List[Evidence] = Field(default_factory=list)
    report: Optional[ResearchReport] = None
    audits: List[CitationAudit] = Field(default_factory=list)
    exported_files: Dict[str, str] = Field(default_factory=dict)
    step: str = "initialized"
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    is_complete: bool = False
