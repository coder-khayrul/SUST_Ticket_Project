# Ticket Investigator Service

This project implements a minimal FastAPI service with a simple web frontend for inspecting complaint tickets and transaction history. It is designed to satisfy the requirements from the problem statement and can be deployed to a provider such as Render.

## Run locally

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Open: `http://127.0.0.1:8000/`

## Endpoints

- `GET /health` — returns `{"status":"ok"}`
- `POST /analyze-ticket` — accepts a ticket JSON payload and returns the structured investigation response
- `GET /` — serves the simple frontend for testing

## Frontend usage

The frontend is available at `/` and lets you enter a ticket complaint plus transaction history JSON and inspect the analyzer response immediately.

## Deploy on Render

This repository includes `render.yaml` and `Procfile` for deployment. To deploy:

1. Push this repository to GitHub.
2. Create a new Web Service on Render.
3. Connect to this repository and select branch `main`.
4. Use the build command: `pip install -r requirements.txt`
5. Use the start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

Render will host the service and make the `/` frontend available publicly.
