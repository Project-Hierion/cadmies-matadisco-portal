#!/usr/bin/env python3
"""
CADMIES-Matadisco Portal — Indexer

This module queries the PDS for CADMIES concept records and stores them
in a local SQLite database for fast, offline search and retrieval.

Functions:
    init_db(): Creates the SQLite database and concepts table if they don't exist.
    main(): Entry point for the indexer script.

Environment variables:
    MATADISCO_PDS_URL: URL of the PDS to query.
    MATADISCO_HANDLE: Handle for authentication.
    MATADISCO_APP_PASSWORD: App password for authentication.
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
    """
    Initialize the SQLite database.

    Creates the database file and the 'concepts' table if they do not exist.
    The table schema is designed to store CADMIES concept records with fields
    for URI, content identifier, concept metadata, and indexing timestamps.

    Returns:
        None
    """
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
    """
    Entry point for the indexer.

    Initializes the database and prepares the indexer for use.
    """
    print("🔍 Starting CADMIES-Matadisco indexer...")
    init_db()
    print("✅ Indexer ready.")


if __name__ == "__main__":
    main()
