"""Splits extracted clean documents into citation-stable passages with deterministic offsets and hashes."""

import hashlib
import re
from typing import List
from evidence.schemas import Document, Passage


def chunk_document_into_passages(
    document: Document,
    target_chunk_size: int = 500,
    min_chunk_size: int = 100,
) -> List[Passage]:
    """Split a Document into stable, verifiable passage chunks with character offsets.

    Args:
        document: Cleaned Document entity.
        target_chunk_size: Preferred target passage length in characters.
        min_chunk_size: Minimum length to consider a standalone passage.

    Returns:
        List of Passage objects with unique IDs, character offsets, and content hashes.
    """
    raw_text = document.raw_text or ""
    if not raw_text.strip():
        return []

    # Split on double newlines to respect natural paragraph boundaries
    paragraph_matches = list(re.finditer(r"(?:[^\n]+\n?)+", raw_text))

    passages: List[Passage] = []
    current_chunk: List[str] = []
    current_start = 0
    current_length = 0
    passage_idx = 1

    for match in paragraph_matches:
        para_text = match.group(0).strip()
        if not para_text:
            continue

        start_offset = match.start()
        end_offset = match.end()

        # If current chunk is empty, initialize starting position
        if not current_chunk:
            current_start = start_offset

        current_chunk.append(para_text)
        current_length += len(para_text)

        # When threshold is reached, yield a passage
        if current_length >= target_chunk_size:
            combined_text = "\n\n".join(current_chunk)
            p_hash = hashlib.sha256(combined_text.encode("utf-8")).hexdigest()
            pid = f"{document.document_id}-p{passage_idx}"

            passages.append(
                Passage(
                    passage_id=pid,
                    document_id=document.document_id,
                    text=combined_text,
                    heading=None,
                    character_offsets=(current_start, end_offset),
                    passage_hash=p_hash,
                )
            )
            passage_idx += 1
            current_chunk = []
            current_length = 0

    # Handle remaining trailing text
    if current_chunk:
        combined_text = "\n\n".join(current_chunk)
        # If very small and previous passage exists, append to previous or keep if above min
        if len(combined_text) < min_chunk_size and passages:
            prev = passages[-1]
            merged_text = f"{prev.text}\n\n{combined_text}"
            passages[-1] = Passage(
                passage_id=prev.passage_id,
                document_id=prev.document_id,
                text=merged_text,
                heading=prev.heading,
                character_offsets=(prev.character_offsets[0], len(raw_text)),
                passage_hash=hashlib.sha256(merged_text.encode("utf-8")).hexdigest(),
            )
        else:
            p_hash = hashlib.sha256(combined_text.encode("utf-8")).hexdigest()
            pid = f"{document.document_id}-p{passage_idx}"
            passages.append(
                Passage(
                    passage_id=pid,
                    document_id=document.document_id,
                    text=combined_text,
                    heading=None,
                    character_offsets=(current_start, len(raw_text)),
                    passage_hash=p_hash,
                )
            )

    return passages
