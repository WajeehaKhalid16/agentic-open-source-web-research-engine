"""Lexical retrieval ranking using an efficient, self-contained Okapi BM25 implementation."""

import math
import re
from typing import Dict, List, Optional, Set, Tuple
from evidence.schemas import Document, Evidence, Passage


def tokenize_text(text: str) -> List[str]:
    """Tokenize text into lowercase alphanumeric words."""
    return re.findall(r"\b[a-zA-Z0-9_-]{2,}\b", text.lower())


class BM25Ranker:
    """Okapi BM25 implementation without external heavy dependencies."""

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.corpus_size = 0
        self.avg_doc_len = 0.0
        self.doc_lens: List[int] = []
        self.doc_freqs: Dict[str, int] = {}
        self.idf: Dict[str, float] = {}
        self.term_freqs_list: List[Dict[str, int]] = []
        self.passages: List[Passage] = []

    def fit(self, passages: List[Passage]) -> "BM25Ranker":
        """Index a collection of passages for BM25 scoring."""
        self.passages = passages
        self.corpus_size = len(passages)
        self.doc_lens = []
        self.doc_freqs = {}
        self.term_freqs_list = []

        if self.corpus_size == 0:
            self.avg_doc_len = 0.0
            return self

        total_len = 0
        for passage in passages:
            tokens = tokenize_text(passage.text)
            length = len(tokens)
            self.doc_lens.append(length)
            total_len += length

            tf: Dict[str, int] = {}
            seen_in_passage: Set[str] = set()
            for token in tokens:
                tf[token] = tf.get(token, 0) + 1
                seen_in_passage.add(token)

            for token in seen_in_passage:
                self.doc_freqs[token] = self.doc_freqs.get(token, 0) + 1

            self.term_freqs_list.append(tf)

        self.avg_doc_len = total_len / self.corpus_size if self.corpus_size > 0 else 0.0

        # Calculate IDF with standard smoothing
        self.idf = {}
        for token, freq in self.doc_freqs.items():
            self.idf[token] = math.log(1.0 + (self.corpus_size - freq + 0.5) / (freq + 0.5))

        return self

    def score_query(self, query: str) -> List[Tuple[Passage, float]]:
        """Score all indexed passages against query terms."""
        if self.corpus_size == 0:
            return []

        query_tokens = tokenize_text(query)
        if not query_tokens:
            return [(p, 0.0) for p in self.passages]

        scores: List[Tuple[Passage, float]] = []

        for idx, passage in enumerate(self.passages):
            doc_len = self.doc_lens[idx]
            tf_dict = self.term_freqs_list[idx]
            score = 0.0

            for token in query_tokens:
                if token not in tf_dict:
                    continue
                tf = tf_dict[token]
                idf = self.idf.get(token, 0.0)

                # Okapi BM25 formula
                numerator = tf * (self.k1 + 1.0)
                denominator = tf + self.k1 * (1.0 - self.b + self.b * (doc_len / (self.avg_doc_len or 1.0)))
                score += idf * (numerator / denominator)

            scores.append((passage, score))

        scores.sort(key=lambda x: x[1], reverse=True)
        return scores


def calculate_source_signals(doc: Optional[Document]) -> Dict[str, any]:
    """Calculate transparent credibility and provenance signals for a source."""
    if not doc:
        return {"source_type": "unknown", "primary_boost": 1.0}

    domain = doc.domain.lower()
    is_primary = False
    source_type = "secondary_web"

    if domain.endswith(".gov") or domain.endswith(".mil"):
        is_primary = True
        source_type = "government_primary"
    elif domain.endswith(".edu") or "arxiv.org" in domain or "nih.gov" in domain:
        is_primary = True
        source_type = "academic_primary"
    elif "reuters.com" in domain or "apnews.com" in domain or "bbc.com" in domain:
        source_type = "major_news"

    return {
        "domain": domain,
        "is_primary": is_primary,
        "source_type": source_type,
        "has_author": bool(doc.author),
        "has_published_date": bool(doc.published_at),
        "primary_boost": 1.2 if is_primary else 1.0,
    }


def rank_passages_lexical(
    query: str,
    passages: List[Passage],
    documents_map: Optional[Dict[str, Document]] = None,
    top_k: int = 15,
) -> List[Evidence]:
    """Rank passages lexically and package into Evidence objects with credibility signals.

    Args:
        query: Research question.
        passages: Candidate extracted passages.
        documents_map: Lookup map of document_id -> Document.
        top_k: Maximum evidence items to return.

    Returns:
        List of Evidence objects sorted by relevance.
    """
    if not passages:
        return []

    ranker = BM25Ranker()
    ranker.fit(passages)
    scored = ranker.score_query(query)

    evidence_list: List[Evidence] = []
    for rank_idx, (passage, raw_score) in enumerate(scored[:top_k], start=1):
        doc = documents_map.get(passage.document_id) if documents_map else None
        signals = calculate_source_signals(doc)

        final_score = raw_score * signals.get("primary_boost", 1.0)

        # Create clean summary claim from first sentence of passage
        sentences = re.split(r"(?<=[.!?])\s+", passage.text.strip())
        claim_summary = sentences[0] if sentences else passage.text[:120]

        evidence = Evidence(
            evidence_id=f"ev-{rank_idx}",
            claim=claim_summary,
            passage_ids=[passage.passage_id],
            relevance_score=round(final_score, 4),
            source_signals=signals,
            source_domain=signals.get("domain", ""),
            notes=f"BM25 base: {raw_score:.2f}, boosted: {final_score:.2f}",
        )
        evidence_list.append(evidence)

    return evidence_list
