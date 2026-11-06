"""Deduplication for URLs, exact content hashes, and near-duplicate text."""

import hashlib
import re
from typing import Dict, List, Set, Tuple
from evidence.schemas import Document


def tokenize_for_similarity(text: str) -> Set[str]:
    """Extract lowercased 3-character shingles / word n-grams for Jaccard similarity."""
    cleaned = re.sub(r"[^\w\s]", "", text.lower())
    words = cleaned.split()
    if len(words) < 3:
        return set(words)
    # Generate 3-word shingles
    return {" ".join(words[i : i + 3]) for i in range(len(words) - 2)}


def jaccard_similarity(set_a: Set[str], set_b: Set[str]) -> float:
    """Compute Jaccard similarity between two token sets."""
    if not set_a or not set_b:
        return 0.0
    intersection = len(set_a.intersection(set_b))
    union = len(set_a.union(set_b))
    return intersection / union if union > 0 else 0.0


class ContentDeduplicator:
    """Tracks seen canonical URLs, exact content hashes, and near-duplicate clusters."""

    def __init__(self, near_duplicate_threshold: float = 0.75):
        self.seen_urls: Set[str] = set()
        self.seen_hashes: Set[str] = set()
        self.near_duplicate_threshold = near_duplicate_threshold
        # Stores (doc_id, shingle_set)
        self.seen_documents: List[Tuple[str, Set[str]]] = []

    def is_duplicate_url(self, canonical_url: str) -> bool:
        """Check if canonical URL has already been processed."""
        if canonical_url in self.seen_urls:
            return True
        self.seen_urls.add(canonical_url)
        return False

    def is_exact_duplicate_content(self, content_hash: str) -> bool:
        """Check if identical content hash has already been processed."""
        if content_hash in self.seen_hashes:
            return True
        self.seen_hashes.add(content_hash)
        return False

    def find_near_duplicate(self, text: str) -> Tuple[bool, float, str]:
        """Check if text is near-duplicate of previously seen document.

        Returns:
            Tuple of (is_near_dup, similarity_score, matched_doc_id).
        """
        shingles = tokenize_for_similarity(text)
        if not shingles:
            return False, 0.0, ""

        for existing_id, existing_shingles in self.seen_documents:
            sim = jaccard_similarity(shingles, existing_shingles)
            if sim >= self.near_duplicate_threshold:
                return True, sim, existing_id

        return False, 0.0, ""

    def register_document(self, doc_id: str, text: str) -> None:
        """Register a unique document into similarity index."""
        shingles = tokenize_for_similarity(text)
        self.seen_documents.append((doc_id, shingles))

    def filter_documents(self, docs: List[Document]) -> Tuple[List[Document], Dict[str, str]]:
        """Filter list of documents, keeping only distinct items.

        Returns:
            Tuple of (unique_documents, duplicates_map {dup_doc_id: canonical_doc_id}).
        """
        unique_docs: List[Document] = []
        duplicates_map: Dict[str, str] = {}

        for doc in docs:
            # 1. Check URL
            if doc.canonical_url in self.seen_urls:
                duplicates_map[doc.document_id] = f"duplicate_url:{doc.canonical_url}"
                continue
            self.seen_urls.add(doc.canonical_url)

            # 2. Check exact text hash
            if doc.content_hash in self.seen_hashes:
                duplicates_map[doc.document_id] = f"exact_hash:{doc.content_hash}"
                continue
            self.seen_hashes.add(doc.content_hash)

            # 3. Check near-duplicate text
            is_near_dup, sim, matched_id = self.find_near_duplicate(doc.raw_text)
            if is_near_dup:
                duplicates_map[doc.document_id] = f"near_duplicate_of:{matched_id}:{sim:.2f}"
                continue

            self.register_document(doc.document_id, doc.raw_text)
            unique_docs.append(doc)

        return unique_docs, duplicates_map
