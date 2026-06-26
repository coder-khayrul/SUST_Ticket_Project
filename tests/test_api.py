from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_analyze_ticket_endpoint():
    payload = {
        "ticket_id": "TKT-003",
        "complaint": "Please check TXN-9102, I sent 1000 BDT by mistake",
        "transaction_history": [
            {
                "transaction_id": "TXN-9102",
                "timestamp": "2026-04-14T14:08:22Z",
                "type": "transfer",
                "amount": 1000,
                "counterparty": "+880171000000",
                "status": "completed",
            }
        ],
    }
    r = client.post("/analyze-ticket", json=payload)
    assert r.status_code == 200
    body = r.json()
    assert body["ticket_id"] == "TKT-003"
    assert body["relevant_transaction_id"] in ("TXN-9102", None)
    assert body["evidence_verdict"] in ("consistent", "insufficient_data")
