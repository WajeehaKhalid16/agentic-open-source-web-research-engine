# Agentic Open-Source Web Research Engine

A locally deployable, agentic research assistant that converts a natural language query into a structured, evidence-backed report with traceable, verifiable citations.

Built entirely with open-source and self-hostable components—no paid APIs, API keys, or proprietary cloud services required.

---

## Key Capabilities

- **Discovery**: Free web search via **DuckDuckGo** (no API key, no Docker required) with optional self-hosted **SearXNG** metasearch and public RSS/Atom news feeds.
- **Safe Crawling**: Multi-hop SSRF protection, strict private IP/cloud metadata blocking, content-type filtering, and response size limits.
- **Extraction**: Clean main-text and article metadata extraction using **Trafilatura**.
- **Deduplication & Chunking**: Canonical URL filtering, exact hash checks, and near-duplicate shingling; deterministic passage chunking with character offsets.
- **Explainable Ranking**: Built-in pure-Python **Okapi BM25** lexical ranking with primary-source domain boosts.
- **Report Synthesis**: Local LLM support via **Ollama** (e.g., `qwen2.5:7b`) with automatic fallback to deterministic evidence-grounded synthesis.
- **Citation Auditing**: Independent verifier that audits citations against stored passages to prevent citation hallucination, distinguishing citation existence from claim support.
- **Multi-Format Export**: Generates `report.md`, `report.html`, `report.json`, `sources.json`, `evidence.jsonl`, and `run_manifest.json`.
- **Zero-Admin Storage**: Fully persistent SQLite storage for runs, documents, passages, evidence, and citations.
- **Streamlit Prototype UI**: Web dashboard connected directly to the FastAPI REST backend.

---

## Project Structure

```text
agentic-web-research-engine/
├── app/
│   ├── __init__.py
│   ├── main.py                # FastAPI web service (POST /api/research, GET /api/research/{id}, export)
│   └── config.py              # Pydantic-settings configuration from .env
├── agent/
│   ├── __init__.py
│   ├── graph.py               # ResearchWorkflow state graph coordinator
│   ├── state.py               # Typed ResearchState contract
│   └── nodes.py               # Discrete research stages (plan, discover, crawl, rank, synthesize, verify, export)
├── search/
│   ├── __init__.py
│   ├── duckduckgo_client.py   # Free DuckDuckGo scraper — primary search engine (no key/Docker)
│   ├── searxng_client.py      # HTTPX client for SearXNG JSON endpoint (optional, requires Docker)
│   └── news_client.py         # Open RSS/Atom news discovery client
├── crawl/
│   ├── __init__.py
│   ├── fetcher.py             # Safe streaming HTTP fetcher with redirect guards
│   ├── policy.py              # SSRF defense, IP validation, URL canonicalization
│   └── extractor.py           # Trafilatura clean text and metadata extraction
├── retrieval/
│   ├── __init__.py
│   ├── chunking.py            # Passage chunking with character offsets and hashes
│   ├── deduplication.py       # Canonical URL and near-duplicate detection
│   └── ranking.py             # Pure-Python Okapi BM25 lexical ranking
├── evidence/
│   ├── __init__.py
│   ├── schemas.py             # Pydantic models (ResearchRun, Document, Passage, Citation, Request/Response)
│   └── verifier.py            # Citation verification against stored passages
├── report/
│   ├── __init__.py
│   ├── writer.py              # Grounded report synthesis (Ollama / deterministic)
│   └── exporter.py            # Exporter for Markdown, HTML, JSON, and JSONL
├── storage/
│   ├── __init__.py
│   ├── database.py            # SQLite schema initialization and connection management
│   └── repository.py          # Typed repository for all entities
├── tests/
│   ├── test_api.py            # API endpoint unit & integration tests
│   ├── test_extractor.py      # Extraction tests against local HTML fixture
│   ├── test_evidence.py       # Passage chunking, deduplication, and citation verification tests
│   ├── test_repository.py     # SQLite persistence and report serialization tests
│   └── fixtures/
│       └── sample_article.html# Local test HTML article
├── ui/
│   └── streamlit_app.py       # Interactive Streamlit UI dashboard connected to FastAPI backend
├── docs/
│   ├── architecture.md        # Architecture overview and Mermaid workflow
│   └── design-decisions.md    # Design rationale, trade-offs, and future roadmap
├── docker/
│   └── searxng/
│       └── settings.yml       # SearXNG configuration enabling JSON format
├── docker-compose.yml         # Local SearXNG container definition
├── requirements.txt           # Core project dependencies (Python 3.13)
├── .env.example               # Example configuration variables
├── .gitignore                 # Standard Python, SQLite, and export ignores
├── LICENSE                    # MIT License
└── README.md
```

---

## Step-by-Step Setup & Execution (PowerShell)

### 1. Virtual Environment & Dependencies

The project uses Python 3.13. The virtual environment is located at `.venv`.

In your VS Code PowerShell terminal:

```powershell
# Optional: Activate the virtual environment in your session
.\.venv\Scripts\Activate.ps1

# Or invoke python directly from .venv without activating:
.\.venv\Scripts\python.exe --version
```

If you need to install or update dependencies:
```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

> **Note:** `streamlit` is now included in `requirements.txt` and will be installed by the command above.

### 2. Configure Environment Variables

Copy the example configuration to create your local `.env`:

```powershell
Copy-Item .env.example .env
```

Settings inside `.env`:
- `APP_NAME`: Display title.
- `DATABASE_PATH`: SQLite file path (default: `research.db`).
- `SEARCH_PROVIDER`: Which engine to use — `duckduckgo` (default, no Docker) or `searxng` (requires Docker).
- `DUCKDUCKGO_URL`: DuckDuckGo HTML endpoint (default: `https://html.duckduckgo.com/html/`).
- `SEARXNG_URL`: SearXNG endpoint (default: `http://localhost:8080`), only used when `SEARCH_PROVIDER=searxng`.
- `OLLAMA_BASE_URL`: Ollama endpoint (default: `http://localhost:11434`).
- `OLLAMA_MODEL`: Target model identifier (default: `qwen2.5:7b`).
- `MAX_SOURCES`: Max candidate sources to fetch per query (default: `10`).

### 3. Run the Automated Test Suite

Execute the complete test suite offline (no external network, Docker, or Ollama required):

```powershell
.\.venv\Scripts\python.exe -m pytest -v
```

All 26 unit and integration tests validate the API, crawler safety, HTML extraction, BM25 ranking, citation verification, and database persistence.

### 4. Start Web Search (DuckDuckGo — Default, No Docker Needed)

The engine uses **DuckDuckGo** for free web search by default. No configuration, API key, or Docker is required.

To verify your search provider setting in `.env`:
```powershell
Select-String "SEARCH_PROVIDER" .env
```
Expected output: `SEARCH_PROVIDER=duckduckgo`

#### Optional: Enable SearXNG instead (requires Docker Desktop)

If Docker Desktop is available and running, you can switch to self-hosted SearXNG:

1. Set `SEARCH_PROVIDER=searxng` in your `.env` file.
2. Launch SearXNG:
   ```powershell
   docker compose up -d
   ```
3. Verify the JSON search endpoint responds:
   ```powershell
   Invoke-RestMethod -Uri "http://localhost:8080/search?q=test&format=json"
   ```

> **If Docker is not running**, leave `SEARCH_PROVIDER=duckduckgo` (the default) and skip this step entirely.

### 5. Start the FastAPI Backend

Launch the backend web service with Uvicorn:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

Available endpoints:
- Welcome message: `http://localhost:8000/`
- Health check: `http://localhost:8000/health`
- Configuration: `http://localhost:8000/api/config`
- OpenAPI Swagger UI: `http://localhost:8000/docs`
- Research execution: `POST http://localhost:8000/api/research`
- Retrieve run: `GET http://localhost:8000/api/research/{id}`
- Sources list: `GET http://localhost:8000/api/research/{id}/sources`
- Ranked evidence: `GET http://localhost:8000/api/research/{id}/evidence`
- Download export: `GET http://localhost:8000/api/research/{id}/export/{format}` (`md`, `html`, or `json`)

### 6. Start the Cinematic Web App (React + Vite + Tailwind)

In a separate PowerShell terminal, start the new cinematic frontend:

```powershell
cd frontend
npm run dev
```

Open `http://localhost:5173` in your browser. The full-page cinematic UI provides:
- Centered search with mode toggles (Web / News / Academic) and advanced filters.
- Real-time animated stage pipeline (Scope, Plan, Search, Fetch, Extract, Rank, Write, Verify).
- Live plan inspection and editable search query variants before crawling.
- Two-column report viewer with slide-in evidence drawer and entity/claim highlighting.
- Citation audit breakdown showing actual verification verdict distribution without hardcoding.
- Multi-format report export (`.md`, `.html`, `.json`) and BibTeX/APA citation export.

### 7. Optional: Start the Streamlit Prototype UI

If you wish to use the legacy Streamlit sidebar interface instead:

```powershell
.\.venv\Scripts\python.exe -m streamlit run ui/streamlit_app.py
```

Open `http://localhost:8501` in your browser.

---

## Sample Research Request

You can submit research queries via PowerShell using `Invoke-RestMethod`:

```powershell
$Body = @{
    query = "What are the recent applications of AI in disaster management?"
    max_sources = 5
    include_news = $true
} | ConvertTo-Json

$Response = Invoke-RestMethod -Uri "http://localhost:8000/api/research" -Method Post -Body $Body -ContentType "application/json"
$Response | Format-List
```

To retrieve a past run by its ID:
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/research/$($Response.research_id)"
```

To download the Markdown deliverable directly:
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/api/research/$($Response.research_id)/export/md" -OutFile "report.md"
```

---

## Fallback Behavior & Offline Capabilities

| Component | When Available | When Unavailable |
| :--- | :--- | :--- |
| **DuckDuckGo** | Default search — discovers web sources freely, no key or Docker needed. | Emits diagnostic warning; falls back to public RSS/Atom news feeds. |
| **SearXNG** | Optional — set `SEARCH_PROVIDER=searxng` and run via Docker for broad multi-engine metasearch. | Not used unless explicitly configured; DuckDuckGo is active instead. |
| **Ollama LLM** | Synthesizes narrative findings using local open-weight model (`qwen2.5:7b`). | Automatically falls back to deterministic evidence-grounded synthesis using ranked passages. |
| **Internet Access** | Fetches live web pages; respects robots.txt and SSRF policies. | Offline test suite executes cleanly using mock fixtures and local test servers. |

---

## Security & Reliability Safeguards

1. **Multi-Hop SSRF Guard**:
   Blocks loopback (`127.0.0.1`), private networks (`10.0.0.0/8`, `192.168.0.0/16`, `172.16.0.0/12`), link-local IPs, and cloud metadata addresses (`169.254.169.254`). Re-validates every redirect hop.
2. **Path Traversal Protection**:
   Deliverable export routes enforce regex validation on research IDs and verify resolved paths remain strictly within the `reports/` directory.
3. **Citation Audit & Grounding**:
   Every report citation is audited to ensure the document ID exists in SQLite, the canonical URL matches, and passage IDs exist. The verifier checks both structural validity and claim-text overlap.
4. **Untrusted Data Isolation**:
   HTML content is stripped of scripts, forms, and executable tags via Trafilatura. HTML reports escape dynamic content to prevent XSS.

---

## License

This project is licensed under the [MIT License](LICENSE).
