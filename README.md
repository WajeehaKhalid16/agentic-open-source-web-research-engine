# Agentic Open-Source Web Research Engine

An AI-powered web research system that automates the process of searching, collecting, organizing, and analyzing information from multiple online sources. It generates structured research results supported by source references and evidence.

The project aims to make web research more organized, transparent, and efficient through an agent-based workflow and an interactive web interface.

## Overview

The Agentic Open-Source Web Research Engine takes a user's research query and processes it through a sequence of stages, including web search, content collection, extraction, retrieval, evidence organization, and research result generation.

Instead of simply returning a list of links, the system attempts to organize the collected information into a structured research response with supporting sources.

The project uses open-source technologies and search services to provide a flexible research workflow.

## Key Features

- **Agent-Based Research Workflow:** Processes research queries through multiple stages.
- **Web Search Integration:** Uses DuckDuckGo as the primary search provider, with optional SearXNG integration.
- **Web Crawling and Content Extraction:** Collects and extracts relevant information from accessible web pages.
- **Information Retrieval:** Organizes and retrieves relevant content using lexical retrieval techniques such as BM25.
- **Evidence Management:** Stores extracted evidence and associates it with its source information.
- **Source References:** Presents source URLs and references alongside research results.
- **Research History:** Allows users to access previous research runs.
- **Live Progress Updates:** Uses Server-Sent Events (SSE) to stream research progress to the frontend.
- **Audit and Verification:** Performs structural checks on source references and evidence.
- **Export Functionality:** Supports exporting research results in available formats.
- **Interactive Interface:** Provides different research modes and an organized interface for viewing results.

## Technology Stack

| Category | Technologies |
|---|---|
| Programming Language | Python |
| Backend Framework | FastAPI |
| Frontend Framework | React 19 |
| Frontend Language | TypeScript |
| Build Tool | Vite |
| Styling | Tailwind CSS |
| UI Components | Radix UI |
| Animations | Framer Motion |
| Web Search | DuckDuckGo, SearXNG (optional) |
| Information Retrieval | BM25 |
| Database | SQLite |
| API Communication | REST API |
| Live Updates | Server-Sent Events (SSE) |
| Testing | Pytest |
| Package Management | pip, npm |

## System Architecture

The system follows a modular architecture in which different components handle individual stages of the research process.

**Research Workflow:**

1. **User Query:** The user submits a research question through the web interface.
2. **Search:** The system retrieves relevant web results.
3. **Crawling:** Accessible web pages are collected for further processing.
4. **Extraction:** Relevant textual content is extracted from the collected pages.
5. **Retrieval:** Relevant information is organized and retrieved using BM25-based lexical retrieval.
6. **Evidence Organization:** Extracted information is associated with its source references.
7. **Research Output:** The system generates structured research results.
8. **Presentation:** Results, sources, evidence, and progress information are displayed through the frontend.

## Project Structure

```text
agentic-web-research-engine/
│
├── agent/              # Research agent and workflow logic
├── app/                # FastAPI application and API routes
├── crawl/              # Web crawling and content extraction
├── evidence/           # Evidence processing and management
├── retrieval/          # Information retrieval components
├── search/             # Search provider integrations
├── storage/            # Database and storage operations
├── tests/              # Backend tests
├── ui/                 # Streamlit interface
│
├── frontend/           # React and TypeScript frontend
│   ├── src/
│   ├── package.json
│   └── ...
│
├── docs/               # Local project documentation
├── requirements.txt    # Python dependencies
├── docker-compose.yml  # Optional service configuration
└── .gitignore
```

## Installation and Setup

### Prerequisites

Make sure you have the following installed:

- Python 3.13
- Node.js and npm
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/WajeehaKhalid16/agentic-open-source-web-research-engine.git
```

```bash
cd agentic-open-source-web-research-engine
```

### 2. Set Up the Python Environment

Create a virtual environment:

```bash
py -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install the Python dependencies:

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

If the project includes an environment template, copy it:

```powershell
Copy-Item .env.example .env
```

Configure the required variables according to the environment template.

Do not upload personal credentials, API keys, or secret values to GitHub.

### 4. Set Up the Frontend

Open a terminal in the project directory and run:

```powershell
cd frontend
npm install
```

## Running the Application

The backend and frontend should run in separate terminals.

### Start the Backend

From the project root:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

Backend API:

`http://localhost:8000`

Interactive API documentation:

`http://localhost:8000/docs`

Health endpoint:

`http://localhost:8000/health`

### Start the Frontend

Open another terminal:

```powershell
cd frontend
npm run dev
```

Frontend application:

`http://localhost:5173`

## API Overview

The backend exposes API endpoints for managing research runs and accessing their results.

| Endpoint | Purpose |
|---|---|
| `POST /api/runs` | Start a research run |
| `GET /api/runs` | Retrieve research history |
| `GET /api/runs/{id}` | Retrieve a specific research run |
| `GET /api/runs/{id}/events` | Receive live research updates |
| `/sources` | Access collected source information |
| `/evidence` | Access supporting evidence |
| `/audit` | Access audit information |
| `/export/{fmt}` | Export research results |

For the complete API specification, visit `http://localhost:8000/docs` after starting the backend.

## Testing

The backend test suite can be executed using:

```powershell
pytest
```

Tests are used to check individual application components and their expected behavior.

## Design Approach

The project follows a modular approach to separate search, crawling, retrieval, evidence processing, storage, and application logic.

This structure makes the system easier to maintain, test, and extend. The frontend communicates with the FastAPI backend through API endpoints, while Server-Sent Events provide live updates during research execution.

## Current Limitations

- Search results depend on the availability and quality of external search providers.
- Some websites may restrict crawling or prevent content extraction.
- BM25 is a lexical retrieval technique and does not independently provide semantic understanding.
- Evidence and citation checks do not guarantee that every generated statement is factually correct.
- Research output quality depends on the relevance, accessibility, and reliability of collected sources.

## Future Improvements

- Improve semantic retrieval and ranking.
- Strengthen evidence-to-claim verification.
- Expand search provider integrations.
- Improve research evaluation using standard information retrieval metrics.
- Enhance multilingual research capabilities.
- Improve performance and scalability.

## Project Information

**Project:** Agentic Open-Source Web Research Engine

**Developer:** Wajeeha Khalid

**GitHub:** [WajeehaKhalid16](https://github.com/WajeehaKhalid16)

**Repository:** [Agentic Open-Source Web Research Engine](https://github.com/WajeehaKhalid16/agentic-open-source-web-research-engine)

---

*An academic project exploring agent-based workflows, open-source search technologies, information retrieval, and evidence-supported web research.*
