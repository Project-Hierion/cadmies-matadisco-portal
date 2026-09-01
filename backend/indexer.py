#!/usr/bin/env python3
"""
Matadisco-CADMIES Portal — Indexer
Queries the PDS for CADMIES records and stores them in SQLite.
"""

import os
import json
import sqlite3
from datetime import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

PDS_URL = os.getenv("MATADISCO_PDS_URL", "https://pds.project-hierion.org")
HANDLE = os.getenv("MATADISCO_HANDLE")
APP_PASSWORD = os.getenv("MATADISCO_APP_PASSWORD")

DB_PATH = Path(__file__).parent.parent / "data" / "portal.db"


def init_db():
    """Initialize the SQLite database."""
    db_path = Path(DB_PATH)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS concepts (
            uri TEXT PRIMARY KEY,
            cid TEXT,
            concept_name TEXT,
            concept_id TEXT,
            definition TEXT,
            core_insight TEXT,
            domains TEXT,
            source TEXT,
            attribution TEXT,
            source_date TEXT,
            published_at TEXT,
            raw_record TEXT,
            indexed_at TEXT
        )
    """)

    conn.commit()
    conn.close()
    print(f"✅ Database initialized at {db_path}")


def main():
    print("🔍 Starting CADMIES indexer...")
    init_db()
    print("✅ Indexer ready.")


if __name__ == "__main__":
    main()
