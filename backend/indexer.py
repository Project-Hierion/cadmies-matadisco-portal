#!/usr/bin/env python3
"""
CADMIES-Matadisco Portal — Indexer

This module queries the PDS for CADMIES concept records and stores them
in a local SQLite database for fast, offline search and retrieval.

Functions:
    init_db(): Creates the SQLite database and concepts table if they don't exist.
    get_access_token(): Authenticates with the PDS and returns an access token.
    fetch_records(): Queries the PDS for CADMIES records.
    index_records(): Stores fetched records in the database.
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
COLLECTION = "cx.vmx.matadisco"
DID = None  # Will be set after authentication


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


def get_access_token():
    """
    Authenticate with the PDS and retrieve an access token.

    Returns:
        str: The access JWT token for API requests.

    Raises:
        Exception: If authentication fails.
    """
    print("🔐 Authenticating with PDS...")
    response = requests.post(
        f"{PDS_URL}/xrpc/com.atproto.server.createSession",
        json={"identifier": HANDLE, "password": APP_PASSWORD},
        headers={"Content-Type": "application/json"}
    )
    response.raise_for_status()

    data = response.json()
    global DID
    DID = data.get("did")
    print(f"✅ Authenticated as {HANDLE} (DID: {DID})")
    return data.get("accessJwt")


def fetch_records(access_token, limit=100):
    """
    Fetch CADMIES records from the PDS.

    Args:
        access_token (str): The access token for authentication.
        limit (int): Maximum number of records to fetch per request (default: 100).

    Returns:
        list: A list of record objects from the PDS.

    Raises:
        Exception: If the API request fails.
    """
    print(f"📡 Fetching CADMIES records from PDS...")
    records = []
    cursor = None
    fetched = 0

    while True:
        params = {
            "collection": COLLECTION,
            "repo": DID,
            "limit": limit
        }
        if cursor:
            params["cursor"] = cursor

        response = requests.get(
            f"{PDS_URL}/xrpc/com.atproto.repo.listRecords",
            params=params,
            headers={"Authorization": f"Bearer {access_token}"}
        )
        response.raise_for_status()

        data = response.json()
        records.extend(data.get("records", []))

        cursor = data.get("cursor")
        fetched += len(data.get("records", []))

        if not cursor:
            break

    print(f"📡 Fetched {fetched} records total")
    return records


def index_records(records):
    """
    Index fetched records into the SQLite database.

    Args:
        records (list): List of record objects from the PDS.

    Returns:
        int: Number of records indexed.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    indexed = 0

    for record in records:
        uri = record.get("uri")
        cid = record.get("cid")
        value = record.get("value", {})

        # Skip if not a CADMIES record
        cadmies_data = value.get("cadmies")
        if not cadmies_data:
            continue

        # Extract fields
        concept_name = cadmies_data.get("conceptName", "")
        concept_id = cadmies_data.get("conceptId", "")
        definition = cadmies_data.get("definition", "")
        core_insight = cadmies_data.get("coreInsight", "")
        domains = json.dumps(cadmies_data.get("domains", []))
        source = cadmies_data.get("source", "")
        attribution = cadmies_data.get("attribution", "")
        source_date = cadmies_data.get("sourceDate", "")
        published_at = value.get("publishedAt", "")

        # Check if record already exists
        cursor.execute("SELECT uri FROM concepts WHERE uri = ?", (uri,))
        if cursor.fetchone():
            continue

        # Insert record
        cursor.execute("""
            INSERT INTO concepts (
                uri, cid, concept_name, concept_id, definition,
                core_insight, domains, source, attribution,
                source_date, published_at, raw_record, indexed_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            uri,
            cid,
            concept_name,
            concept_id,
            definition,
            core_insight,
            domains,
            source,
            attribution,
            source_date,
            published_at,
            json.dumps(value),
            datetime.utcnow().isoformat()
        ))
        indexed += 1

    conn.commit()
    conn.close()
    print(f"✅ Indexed {indexed} new records")
    return indexed


def main():
    """
    Entry point for the indexer.

    Authenticates with the PDS, fetches CADMIES records, and indexes them
    into the local SQLite database.
    """
    print("🔍 Starting CADMIES-Matadisco indexer...")
    init_db()

    # Check for credentials
    if not HANDLE or not APP_PASSWORD:
        print("❌ ERROR: Missing credentials. Set MATADISCO_HANDLE and MATADISCO_APP_PASSWORD in .env")
        return

    try:
        # Authenticate
        access_token = get_access_token()

        # Fetch records
        records = fetch_records(access_token)

        # Index records
        indexed = index_records(records)

        print(f"✅ Indexer complete. {indexed} records indexed.")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
