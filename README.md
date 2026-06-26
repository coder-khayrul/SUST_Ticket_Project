# Ticket Investigator Service

This project implements a minimal FastAPI service that accepts customer complaint tickets and analyzes them against recent transaction history to determine whether the complaint matches a provided transaction and what the recommended next steps are.

Run locally:

- Install dependencies: `pip install -r requirements.txt`
- Start server: `uvicorn app.main:app --reload --port 8000`

Endpoints:

- `GET /health` — returns {"status":"ok"}
- `POST /analyze-ticket` — analyze a ticket per the problem statement
