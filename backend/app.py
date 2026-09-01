#!/usr/bin/env python3
"""
CADMIES-Matadisco Portal — API Server

This module provides a RESTful API for searching and retrieving CADMIES
concept records from the SQLite database. It serves the frontend with
data for display, search, and statistics.

Endpoints:
    /           - Returns service metadata.
    /search     - Full-text search across concept names and definitions.
    /record/<uri> - Retrieves a single record by its AT URI.
    /stats      - Returns total count of indexed concepts.

Environment variables:
    PORTAL_PORT: Port to run the server on (default: 5000).
    PORTAL_DEBUG: Enable debug mode (default: false).
"""

import os
import json
import sqlite3
from pathlib import Path

from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

DB_PATH = Path(__file__).parent.parent / "data" / "portal.db"
PORT = int(os.getenv("PORTAL_PORT", 5000))
DEBUG = os.getenv("PORTAL_DEBUG", "false").lower() == "true"


def get_db():
    """
    Establish a connection to the SQLite database.

    Returns:
        sqlite3.Connection: A connection object with row_factory set to sqlite3.Row.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def home():
    """
    GET /
    Returns basic metadata about the API service.
    """
    return jsonify({
        "name": "CADMIES-Matadisco Portal",
        "status": "running",
        "version": "0.1.0",
        "endpoints": ["/search", "/record/<uri>", "/stats"]
    })


@app.route("/search")
def search():
    """
    GET /search
    Performs a full-text search on concept names and definitions.

    Query parameters:
        q (str): Search query.
        limit (int): Max results to return (default: 20).
        offset (int): Pagination offset (default: 0).

    Returns:
        JSON list of matching concept records.
    """
    q = request.args.get("q", "")
    limit = int(request.args.get("limit", 20))
    offset = int(request.args.get("offset", 0))

    if not q:
        return jsonify({"error": "Missing search query"}), 400

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT uri, concept_name, definition, domains, source_date
        FROM concepts
        WHERE concept_name LIKE ? OR definition LIKE ?
        LIMIT ? OFFSET ?
    """, (f"%{q}%", f"%{q}%", limit, offset))

    rows = cursor.fetchall()
    conn.close()

    return jsonify([dict(row) for row in rows])


@app.route("/record/<uri>")
def get_record(uri):
    """
    GET /record/<uri>
    Retrieves a complete concept record by its AT URI.

    Path parameters:
        uri (str): The AT URI of the concept record.

    Returns:
        JSON object with all fields for the matching record.
        Returns 404 if the record is not found.
    """
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM concepts WHERE uri = ?", (uri,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return jsonify({"error": "Record not found"}), 404

    return jsonify(dict(row))


@app.route("/stats")
def stats():
    """
    GET /stats
    Returns the total number of indexed concepts.

    Returns:
        JSON object with 'total_concepts' key.
    """
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as total FROM concepts")
    total = cursor.fetchone()["total"]
    conn.close()

    return jsonify({"total_concepts": total})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, debug=DEBUG)
