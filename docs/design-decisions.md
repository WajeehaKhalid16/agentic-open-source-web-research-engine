# Design Decisions & Trade-Offs

This document records the architectural choices, trade-offs, and design rationale for the **Agentic Open-Source Web Research Engine**.

---

## 1. Controlled State Graph vs. Autonomous Swarms

* **Decision:** Implement a bounded, inspectable state machine with typed node contracts rather than an autonomous multi-agent swarm.
* **Rationale:** Autonomous agent swarms often suffer from unpredictable loops, non-deterministic branching, uncontrolled token consumption, and debugging difficulty. A state machine provides explicit state transitions, guaranteed stopping rules, predictable resource usage, and discrete inspectability at each stage.
* **Evolution Path:** The node interfaces (`agent/nodes.py`) and typed state (`agent/state.py`) follow LangGraph conventions, allowing straightforward wrapping into a LangGraph `StateGraph` as orchestration complexity grows.

---

## 2. Pure-Python Okapi BM25 Baseline vs. Immediate Heavy Vectors

* **Decision:** Use a self-contained, pure-Python Okapi BM25 ranking algorithm as the primary baseline before adding vector embeddings.
* **Rationale:**
  1. Zero external binary dependencies: BM25 executes natively on Python 3.13 without compilation issues or GPU requirements.
  2. Explainability: Term-frequency and inverse-document-frequency scores can be inspected directly, ensuring transparent ranking signals.
  3. Speed and efficiency: Lexical ranking runs in milliseconds, making test suites fast and deterministic.
* **Trade-off:** Pure lexical matching does not capture semantic paraphrases or cross-lingual queries. Future phases will layer local sentence-transformers (e.g. `all-MiniLM-L6-v2`) and cross-encoders on top of the BM25 candidate pool.

---

## 3. SQLite Storage vs. Distributed Database Services

* **Decision:** Use Python's built-in SQLite engine with JSON fields for metadata and audit storage.
* **Rationale:** SQLite requires zero infrastructure setup, runs across all platforms (Windows, Linux, macOS), supports ACID transactions, and simplifies local inspection and automated testing.
* **Trade-off:** SQLite does not scale horizontally for multi-node web-scale crawling, which is explicitly out of scope for a locally deployed research assistant.

---

## 4. Trafilatura Static-First Extraction vs. Headless Browser Default

* **Decision:** Prioritize static HTTP fetching and Trafilatura article extraction, reserving headless browser automation (e.g., Playwright) for explicit fallback.
* **Rationale:** Static fetching is 50–100x faster and requires orders of magnitude less memory than running Chromium instances. Trafilatura excels at extracting main text, titles, authors, and dates from standard web articles while stripping junk, navigation, and advertisement boilerplate.
* **Trade-off:** Pages that rely entirely on client-side single-page JavaScript rendering will yield minimal text with static fetching. Playwright can be added conditionally when static fetch yields empty content.

---

## 5. Local Ollama LLM with Deterministic Extractive Fallback

* **Decision:** Support local Ollama inference (`qwen2.5:7b` or `qwen3:8b`) with an automated fallback to high-quality deterministic extractive synthesis.
* **Rationale:** If Ollama is not installed, not running, or running on constrained hardware (CPU without GPU acceleration), the engine still delivers a complete, well-structured, citation-backed report without failing or fabricating information.
* **Anti-Hallucination Guard:** In both LLM and extractive modes, every claim is linked to stored passage IDs and audited by the `CitationVerifier`.

---

## 6. Strict Multi-Hop SSRF Defense

* **Decision:** Re-verify URL safety and resolved IP addresses before every HTTP request and on every redirect hop.
* **Rationale:** Attackers frequently bypass naive URL filters by pointing a public domain to a redirect that targets internal services (`http://169.254.169.254` or `http://127.0.0.1:8000`). Re-evaluating `validate_url_safety` on each hop neutralizes this threat vector.

---

## 7. Current Limitations & Next Steps

| Limitation | Current State | Planned Mitigation |
| :--- | :--- | :--- |
| **JavaScript Heavy Sites** | Skipped or extracted from fallback tags | Add optional Playwright rendering for zero-text pages |
| **Semantic Matching** | Lexical BM25 ranking | Add local sentence-transformers embeddings |
| **Search Engine Dependency** | Requires local SearXNG Docker container | RSS News fallback is active; SearXNG recommended for general web |
