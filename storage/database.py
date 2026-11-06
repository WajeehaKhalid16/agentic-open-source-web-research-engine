"""SQLite connection manager and schema initialization."""

import os
import sqlite3
from typing import Optional
from app.config import get_settings


class Database:
    """Manages SQLite database connections and table lifecycle."""

    def __init__(self, db_path: Optional[str] = None):
        settings = get_settings()
        self.db_path = db_path or settings.database_path
        self._ensure_dir()
        self.init_schema()

    def _ensure_dir(self) -> None:
        """Create parent directory for database file if it does not exist."""
        dirname = os.path.dirname(self.db_path)
        if dirname and not os.path.exists(dirname):
            os.makedirs(dirname, exist_ok=True)

    def get_connection(self) -> sqlite3.Connection:
        """Return a configured SQLite connection with row factory enabled."""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def init_schema(self) -> None:
        """Initialize required database tables if not already present."""
        with self.get_connection() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS research_runs (
                    run_id TEXT PRIMARY KEY,
                    query TEXT NOT NULL,
                    constraints_json TEXT,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    budgets_json TEXT,
                    model_version TEXT,
                    status TEXT NOT NULL,
                    summary TEXT,
                    report_json TEXT,
                    warnings_json TEXT
                );

                CREATE TABLE IF NOT EXISTS search_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT NOT NULL,
                    query_id TEXT,
                    rank INTEGER,
                    engine TEXT,
                    title TEXT,
                    snippet TEXT,
                    url TEXT NOT NULL,
                    discovered_at TEXT NOT NULL,
                    FOREIGN KEY(run_id) REFERENCES research_runs(run_id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS documents (
                    document_id TEXT PRIMARY KEY,
                    run_id TEXT NOT NULL,
                    canonical_url TEXT NOT NULL,
                    domain TEXT NOT NULL,
                    title TEXT,
                    author TEXT,
                    published_at TEXT,
                    retrieved_at TEXT NOT NULL,
                    language TEXT,
                    content_hash TEXT NOT NULL,
                    fetch_status TEXT NOT NULL,
                    raw_text TEXT,
                    FOREIGN KEY(run_id) REFERENCES research_runs(run_id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS passages (
                    passage_id TEXT PRIMARY KEY,
                    document_id TEXT NOT NULL,
                    run_id TEXT NOT NULL,
                    text TEXT NOT NULL,
                    heading TEXT,
                    start_char INTEGER NOT NULL,
                    end_char INTEGER NOT NULL,
                    passage_hash TEXT NOT NULL,
                    FOREIGN KEY(document_id) REFERENCES documents(document_id) ON DELETE CASCADE,
                    FOREIGN KEY(run_id) REFERENCES research_runs(run_id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS evidence (
                    evidence_id TEXT PRIMARY KEY,
                    run_id TEXT NOT NULL,
                    claim TEXT NOT NULL,
                    passage_ids_json TEXT NOT NULL,
                    relevance_score REAL,
                    source_domain TEXT,
                    source_signals_json TEXT,
                    corroboration_group TEXT,
                    notes TEXT,
                    FOREIGN KEY(run_id) REFERENCES research_runs(run_id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS citations (
                    citation_id TEXT NOT NULL,
                    run_id TEXT NOT NULL,
                    document_id TEXT NOT NULL,
                    passage_ids_json TEXT NOT NULL,
                    url TEXT NOT NULL,
                    access_date TEXT NOT NULL,
                    display_metadata_json TEXT,
                    PRIMARY KEY(run_id, citation_id),
                    FOREIGN KEY(document_id) REFERENCES documents(document_id) ON DELETE CASCADE,
                    FOREIGN KEY(run_id) REFERENCES research_runs(run_id) ON DELETE CASCADE
                );

                CREATE INDEX IF NOT EXISTS idx_doc_run ON documents(run_id);
                CREATE INDEX IF NOT EXISTS idx_passage_doc ON passages(document_id);
                CREATE INDEX IF NOT EXISTS idx_passage_run ON passages(run_id);
                CREATE INDEX IF NOT EXISTS idx_search_run ON search_results(run_id);
                CREATE INDEX IF NOT EXISTS idx_evidence_run ON evidence(run_id);
                """
            )

            # Backward-compatible migrations for existing research_runs tables
            col_cursor = conn.execute("PRAGMA table_info(research_runs);")
            cols = {row["name"] for row in col_cursor.fetchall()}
            if "report_json" not in cols:
                conn.execute("ALTER TABLE research_runs ADD COLUMN report_json TEXT;")
            if "warnings_json" not in cols:
                conn.execute("ALTER TABLE research_runs ADD COLUMN warnings_json TEXT;")
