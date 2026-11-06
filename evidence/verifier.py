"""Citation and claim verification against actual stored passages and documents."""

import re
from typing import Dict, List, Optional
from evidence.schemas import Citation, CitationAudit, Document, Passage


class CitationVerifier:
    """Verifies that all citations in a report point to real, stored passages and authentic URLs."""

    def __init__(
        self,
        documents: List[Document],
        passages: List[Passage],
    ):
        self.doc_map: Dict[str, Document] = {d.document_id: d for d in documents}
        self.passage_map: Dict[str, Passage] = {p.passage_id: p for p in passages}

    def verify_citation(self, citation: Citation, claim_text: Optional[str] = None) -> CitationAudit:
        """Audit a single citation for document presence, passage existence, URL consistency, and text grounding."""
        # 1. Document existence check
        doc = self.doc_map.get(citation.document_id)
        if not doc:
            return CitationAudit(
                citation_id=citation.citation_id,
                exists_in_store=False,
                url_matches=False,
                passage_found=False,
                substantiated=False,
                citation_verified=False,
                detail=f"Fabrication check failed: document_id '{citation.document_id}' not found in store.",
            )

        # 2. Canonical URL consistency check
        url_matches = bool(doc.canonical_url and citation.url and doc.canonical_url == citation.url)
        if not url_matches:
            return CitationAudit(
                citation_id=citation.citation_id,
                exists_in_store=True,
                url_matches=False,
                passage_found=False,
                substantiated=False,
                citation_verified=False,
                detail=f"URL mismatch: citation URL '{citation.url}' does not match stored document canonical URL '{doc.canonical_url}'.",
            )

        # 3. Passage existence check
        passages_found: List[Passage] = []
        missing_passage_ids: List[str] = []
        for pid in citation.passage_ids:
            if pid in self.passage_map:
                passages_found.append(self.passage_map[pid])
            else:
                missing_passage_ids.append(pid)

        if missing_passage_ids or not passages_found:
            return CitationAudit(
                citation_id=citation.citation_id,
                exists_in_store=True,
                url_matches=True,
                passage_found=False,
                substantiated=False,
                citation_verified=False,
                detail=f"Passage lookup failed: IDs {missing_passage_ids} do not exist in stored passages.",
            )

        # 4. Textual substantiation check
        combined_passage_text = " ".join([p.text.lower() for p in passages_found])
        substantiated = True
        detail = "Citation verified: authentic document, valid passage IDs, and URL match."

        if claim_text:
            # Check for token overlap between claim and passages
            claim_tokens = set(re.findall(r"\b[a-zA-Z0-9_-]{3,}\b", claim_text.lower()))
            if claim_tokens:
                overlap = [t for t in claim_tokens if t in combined_passage_text]
                overlap_ratio = len(overlap) / len(claim_tokens)
                if overlap_ratio < 0.2:
                    substantiated = False
                    detail = (
                        f"Citation verified structurally, but weak claim support: "
                        f"only {overlap_ratio:.0%} of claim terms appear in cited passage."
                    )
                else:
                    detail = f"Citation verified and claim substantiated ({overlap_ratio:.0%} token match)."

        return CitationAudit(
            citation_id=citation.citation_id,
            exists_in_store=True,
            url_matches=True,
            passage_found=True,
            substantiated=substantiated,
            citation_verified=True,
            detail=detail,
        )

    def verify_all(
        self,
        citations: List[Citation],
        claims: Optional[Dict[str, str]] = None,
    ) -> List[CitationAudit]:
        """Audit a batch of citations.

        Args:
            citations: List of Citation objects to audit.
            claims: Optional mapping of citation_id -> claim statement.

        Returns:
            List of CitationAudit results.
        """
        claims = claims or {}
        audits: List[CitationAudit] = []
        for cit in citations:
            claim_text = claims.get(cit.citation_id)
            audits.append(self.verify_citation(cit, claim_text=claim_text))
        return audits
