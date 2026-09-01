#!/usr/bin/env python3
"""
CADMIES-Matadisco Portal — API Server
Serves search results, record details, and stats from the SQLite database.
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
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def home():
    return jsonify({"name": "CADMIES-Matadisco Portal", "status": "running"})


@app.route("/search")
def search():
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
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as total FROM concepts")
    total = cursor.fetchone()["total"]
    conn.close()

    return jsonify({"total_concepts": total})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, debug=DEBUG)
