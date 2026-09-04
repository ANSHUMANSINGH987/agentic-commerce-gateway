# Agentic Commerce Gateway (ACG)

A production-grade Model Context Protocol (MCP) server that enables safe, bounded, and auditable agent-to-agent commerce on top of Razorpay. Built for the Razorpay AI Buildathon 2026.

## Architecture & The Bar
This project tackles **Track 01: AI Growth & Agentic Commerce** by building an inventory and negotiation fortress. It does not trust the AI.

*   **Bounded & Gated:** AI agents can propose discounts, but all final prices are validated against a strict deterministic `pricing_rules` table via SQLAlchemy.
*   **Explainable Actions:** Every search, negotiation, and checkout generates an immutable record in the `audit_logs` table.
*   **Graceful Failure:** Uses PostgreSQL row-level locking (`SELECT FOR UPDATE`) to prevent race conditions when multiple agents attempt to buy the last item simultaneously.
*   **Semantic Search:** Built on `pgvector` to allow AI buyers to search inventory semantically rather than relying on exact keyword matches.

## Local Setup

1. Configure the environment:
   `copy .env.example .env` (Add your Razorpay Test Keys)
2. Spin up the pgvector database:
   `docker compose up -d`
3. Initialize schemas and mock data:
   `uv run python -m scripts.seed_db`
   `uv run python -m scripts.seed_mock_data`
4. Run the FastMCP server:
   `uv run python -m src.server`
5. Run the Concurrency Stress Test:
   `uv run python -m pytest tests/test_concurrency.py -v -s`