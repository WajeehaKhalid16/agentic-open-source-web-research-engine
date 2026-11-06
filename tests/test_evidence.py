"""Tests for passage chunking, deduplication, and citation verification."""

import pytest
from evidence.schemas import Citation, Document, Passage
from evidence.verifier import CitationVerifier
from retrieval.chunking import chunk_document_into_passages
from retrieval.deduplication import ContentDeduplicator


def test_chunking_and_offsets():
    """Verify that chunking creates stable passages with character offsets and hashes."""
    sample_text = (
        "First major finding regarding arid solar development and ecosystem balance. "
        "Photovoltaic panels alter surface albedo.\n\n"
        "Second major finding regarding water reduction and economic yield in agrivoltaics. "
        "Water demand was reduced significantly across arid testing basins."
    )
    doc = Document(
        document_id="testdoc123",
        canonical_url="https://example.org/test",
        domain="example.org",
        title="Test Document",
        content_hash="abc123hash",
        raw_text=sample_text,
    )

    passages = chunk_document_into_passages(doc, target_chunk_size=100)
    assert len(passages) >= 1

    for p in passages:
        assert p.passage_id.startswith("testdoc123-p")
        assert len(p.passage_hash) == 64
        # Verify offsets
        start, end = p.character_offsets
        assert end > start
        # Check that sliced text matches or contains passage text
        assert doc.raw_text[start:end].strip() in p.text or p.text in doc.raw_text[start:end]


def test_deduplication():
    """Verify that duplicate URLs and near-duplicate contents are filtered out."""
    deduplicator = ContentDeduplicator(near_duplicate_threshold=0.7)

    doc1 = Document(
        document_id="doc1",
        canonical_url="https://example.org/article-1",
        domain="example.org",
        title="Solar Farming",
        content_hash="hash1",
        raw_text="Solar farming in desert ecosystems provides clean renewable electricity to remote regional grids.",
    )

    # Identical URL
    doc2_dup_url = Document(
        document_id="doc2",
        canonical_url="https://example.org/article-1",
        domain="example.org",
        title="Duplicate URL",
        content_hash="hash2",
        raw_text="Different text but exact same URL should be filtered out by canonical URL check.",
    )

    # Near duplicate text (syndicated article)
    doc3_near_dup = Document(
        document_id="doc3",
        canonical_url="https://syndicate.org/news-copy",
        domain="syndicate.org",
        title="Syndicated Copy",
        content_hash="hash3",
        raw_text="Solar farming in desert ecosystems provides clean renewable electricity to remote regional grids daily.",
    )

    unique, dup_map = deduplicator.filter_documents([doc1, doc2_dup_url, doc3_near_dup])

    assert len(unique) == 1
    assert unique[0].document_id == "doc1"
    assert "doc2" in dup_map
    assert "doc3" in dup_map


def test_citation_verification_valid():
    """Verify that legitimate citations with existing documents and passages pass verification."""
    doc = Document(
        document_id="doc-valid",
        canonical_url="https://example.org/valid",
        domain="example.org",
        title="Valid Source",
        content_hash="hashval",
        raw_text="Agrivoltaics reduced irrigation water demand by 28 percent.",
    )
    passage = Passage(
        passage_id="doc-valid-p1",
        document_id="doc-valid",
        text="Agrivoltaics reduced irrigation water demand by 28 percent in arid testing basins.",
        character_offsets=(0, 75),
        passage_hash="pashhash1",
    )

    verifier = CitationVerifier(documents=[doc], passages=[passage])

    valid_cit = Citation(
        citation_id="cit-1",
        document_id="doc-valid",
        passage_ids=["doc-valid-p1"],
        url="https://example.org/valid",
        display_metadata={"title": "Valid Source"},
    )

    audit = verifier.verify_citation(valid_cit, claim_text="Agrivoltaics reduced water demand by 28 percent.")
    assert audit.exists_in_store is True
    assert audit.url_matches is True
    assert audit.passage_found is True
    assert audit.substantiated is True
    assert audit.citation_verified is True


def test_citation_verification_invalid():
    """Verify that fabricated citations or non-existent passage IDs are rejected."""
    doc = Document(
        document_id="doc-real",
        canonical_url="https://example.org/real",
        domain="example.org",
        title="Real Source",
        content_hash="hashreal",
        raw_text="Desert ecosystems are fragile and require careful environmental review.",
    )
    passage = Passage(
        passage_id="doc-real-p1",
        document_id="doc-real",
        text="Desert ecosystems are fragile and require careful environmental review.",
        character_offsets=(0, 68),
        passage_hash="pashhash2",
    )

    verifier = CitationVerifier(documents=[doc], passages=[passage])

    # 1. Non-existent document ID (Fabricated document)
    fake_doc_cit = Citation(
        citation_id="cit-fake-doc",
        document_id="doc-nonexistent",
        passage_ids=["doc-real-p1"],
        url="https://example.org/fake",
    )
    audit1 = verifier.verify_citation(fake_doc_cit)
    assert audit1.exists_in_store is False
    assert audit1.substantiated is False
    assert audit1.citation_verified is False

    # 2. Non-existent passage ID
    fake_passage_cit = Citation(
        citation_id="cit-fake-p",
        document_id="doc-real",
        passage_ids=["doc-real-p999"],
        url="https://example.org/real",
    )
    audit2 = verifier.verify_citation(fake_passage_cit)
    assert audit2.passage_found is False
    assert audit2.substantiated is False
    assert audit2.citation_verified is False

    # 3. Mismatched URL
    mismatched_url_cit = Citation(
        citation_id="cit-wrong-url",
        document_id="doc-real",
        passage_ids=["doc-real-p1"],
        url="https://malicious.org/hijack",
    )
    audit3 = verifier.verify_citation(mismatched_url_cit)
    assert audit3.url_matches is False
    assert audit3.citation_verified is False


def test_citation_verification_weak_claim_support():
    """Distinguish structural citation existence from actual claim-support verification."""
    doc = Document(
        document_id="doc-real",
        canonical_url="https://example.org/real",
        domain="example.org",
        title="Real Source",
        content_hash="hashreal",
        raw_text="Deserts receive very low annual rainfall.",
    )
    passage = Passage(
        passage_id="doc-real-p1",
        document_id="doc-real",
        text="Deserts receive very low annual rainfall.",
        character_offsets=(0, 42),
        passage_hash="pashhash3",
    )
    verifier = CitationVerifier(documents=[doc], passages=[passage])

    cit = Citation(
        citation_id="cit-1",
        document_id="doc-real",
        passage_ids=["doc-real-p1"],
        url="https://example.org/real",
    )

    # Completely unrelated claim that has zero token overlap with the passage text
    audit = verifier.verify_citation(cit, claim_text="Quantum superconducting qubits require cryogenic helium refrigeration.")
    assert audit.citation_verified is True   # Structurally authentic (exists in store, URL matches, passage exists)
    assert audit.substantiated is False     # But claim is unsupported by this passage
    assert "weak claim support" in audit.detail.lower()
