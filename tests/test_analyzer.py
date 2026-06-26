from app.analyzer import analyze_ticket


def test_wrong_transfer_matches_txn():
    payload = {
        "ticket_id": "TKT-001",
        "complaint": "I sent 5000 taka to a wrong number (+8801719876543) around 2pm today",
        "transaction_history": [
            {
                "transaction_id": "TXN-9101",
                "timestamp": "2026-04-14T14:08:22Z",
                "type": "transfer",
                "amount": 5000,
                "counterparty": "+8801719876543",
                "status": "completed",
            }
        ],
    }

    res = analyze_ticket(payload)
    assert res["ticket_id"] == "TKT-001"
    assert res["relevant_transaction_id"] == "TXN-9101"
    assert res["evidence_verdict"] == "consistent"
    assert res["case_type"] == "wrong_transfer"
    assert res["human_review_required"] is True


def test_insufficient_data_no_transactions():
    payload = {"ticket_id": "TKT-002", "complaint": "I think I lost money"}
    res = analyze_ticket(payload)
    assert res["relevant_transaction_id"] is None
    assert res["evidence_verdict"] == "insufficient_data"