# Financial Intelligence Platform

An open-source API for derived financial intelligence: company relationships, factor scores, events, signals, explainable summaries, investment theses, and graph-shaped network data.

This first iteration is intentionally lightweight. It runs locally with FastAPI and SQLite, seeds a small company universe, and exposes the core API shape before external ingestion credentials are required.

## What is included

- FastAPI application with OpenAPI docs
- SQLite persistence by default
- Seeded company universe: `AAPL`, `MSFT`, `NVDA`, `AMD`, `TSM`, `GOOGL`, `AMZN`
- Company relationship graph
- Financial factor scores
- Events and deterministic signals
- Explanation, thesis, similarity, and network endpoints
- Connector skeletons for SEC and Wikidata

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

Optional environment configuration:

```bash
cp .env.example .env
```

## Run

```bash
uvicorn app.main:app --reload
```

Open:

- API: http://127.0.0.1:8000
- Docs: http://127.0.0.1:8000/docs

## Example endpoints

```text
GET /health
GET /companies
GET /companies/NVDA
GET /companies/NVDA/relationships
GET /companies/NVDA/factors
GET /companies/NVDA/events
GET /companies/NVDA/signals
GET /companies/NVDA/explain
GET /companies/NVDA/thesis
GET /companies/NVDA/similar
GET /network/NVDA
```

## Test

```bash
pytest
```

## Next iteration

- Add Alembic migrations
- Add Postgres and Redis Docker Compose
- Implement live Wikidata ingestion
- Implement SEC company facts ingestion with a configured `SEC_USER_AGENT`
- Add factor calculations from real historical prices
- Add LLM-backed explanations with citations
- Add MCP server for AI agents
