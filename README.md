# CADMIES-Matadisco Portal

A dedicated viewer and search interface for CADMIES concept records published on the Matadisco network. Built for scientists, academics, and anyone exploring the mycelium.

---

## Purpose

The CADMIES-Matadisco Portal provides a specialized interface for discovering CADMIES knowledge graph concepts through the Matadisco decentralized data network. It complements the main CADMIES Gateway (`project-hierion.org`) by offering:

- **Search** — Full-text search across concept names and definitions
- **Discovery** — Browse indexed concepts from the Matadisco network
- **Transparency** — See the raw data as it exists on the network
- **Interoperability** — Built on the same data as the CADMIES Gateway

**One source of truth. Two interfaces.**

---

## Architecture
```
┌─────────────────────────────────────────────────────────────┐
│ CADMIES-Matadisco Portal │
├─────────────────────────────────────────────────────────────┤
│ │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────────┐ │
│ │ Indexer │───▶│ SQLite │───▶│ Flask API │ │
│ │ (Python) │ │ Database │ │ (REST) │ │
│ └─────────────┘ └─────────────┘ └─────────────────┘ │
│ │ │
│ ▼ │
│ ┌─────────────────────────────┐│
│ │ Frontend ││
│ │ (HTML/CSS/JS) ││
│ └─────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```


### Components

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Indexer** (`backend/indexer.py`) | Python | Queries the PDS for CADMIES records, stores them in SQLite |
| **Database** (`data/portal.db`) | SQLite | Local cache of indexed records |
| **API** (`backend/app.py`) | Flask | Serves search, record, and stats endpoints |
| **Frontend** (`frontend/`) | HTML/CSS/JS | User interface for searching and displaying concepts |

### Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Service metadata |
| `/search?q=...` | GET | Full-text search across concept names and definitions |
| `/record/<uri>` | GET | Retrieve a complete record by AT-URI |
| `/stats` | GET | Total number of indexed concepts |

---

## Data Flow

1. **Publish** — Concepts are published to Matadisco via the `hierion-matadisco` producer
2. **Index** — The indexer fetches records from the PDS and stores them locally
3. **Search** — The API serves search requests from the frontend
4. **Display** — The frontend renders concept cards with definitions, domains, and metadata

**Records are indexed on-demand, not streamed live.** This keeps the portal simple and reliable.

---

## Setup

### Prerequisites

- Python 3.10+
- SQLite
- Access to a PDS with CADMIES records

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Project-Hierion/cadmies-matadisco-portal.git
   cd cadmies-matadisco-portal
   ```

2. Set up the backend:
   ```bash
   cd backend
   python3 -m venv discovenv
   source discovenv/bin/activate
   pip install -r requirements.txt
   ```

Create .env file:

bash
cp .env.example .env
Fill in your PDS credentials.

Run the indexer:

bash
python indexer.py
Run the API server:

bash
python app.py
Serve the frontend:

bash
cd ../frontend
python3 -m http.server 8000
Open http://localhost:8000 in your browser.

Usage
Search
Enter a search term (e.g., anatta, interconnectedness, consciousness) and press Enter or click Search.

Results
Each result displays:

Concept name — The title of the concept

Domains — The canonical domains it belongs to

Definition — The core definition of the concept

Publication date — When the record was published to Matadisco

Stats
The footer shows the total number of indexed concepts.

Development
Indexer
The indexer is designed for on-demand indexing. To re-index all records, simply run python indexer.py again. It will skip duplicates.

API
The API runs on port 5000 by default. This can be changed in the .env file.

Frontend
The frontend is pure HTML/CSS/JS. No build step. Edit the files directly and refresh the browser.

Next Steps
Dataset viewer — Extend or create a separate viewer for LLMDataHub records

Frontend tweaks — Improve search experience, add filters, enhance UI

Live indexing — Add WebSocket or event-driven updates

Bulk publishing — Publish the remaining 636 concepts

Related Repositories
hierion-matadisco — Producer for publishing records

CADMIES — The CADMIES gateway

Matadisco — The Matadisco network

License
MIT

Acknowledgments
vmx and the IPFS Foundation for Matadisco

The CADMIES community for the concepts

The mycelium for the connections

***Let the mycelium grow! 🌱***
