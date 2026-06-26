from typing import Dict, Any, List, Optional


CASE_TYPES = [
    "wrong_transfer",
    "payment_failed",
    "refund_request",
    "duplicate_payment",
    "merchant_settlement_delay",
    "agent_cash_in_issue",
    "phishing_or_social_engineering",
    "other",
]

DEPARTMENTS = {
    "wrong_transfer": "dispute_resolution",
    "payment_failed": "payments_ops",
    "refund_request": "customer_support",
    "duplicate_payment": "payments_ops",
    "merchant_settlement_delay": "merchant_operations",
    "agent_cash_in_issue": "agent_operations",
    "phishing_or_social_engineering": "fraud_risk",
    "other": "customer_support",
}


def _find_matching_transaction(complaint: str, transactions: Optional[List[Dict[str, Any]]]) -> Optional[str]:
    if not transactions:
        return None
    # naive approach: look for numbers that match amounts or txn ids
    complaint_lower = complaint.lower()
    for tx in transactions:
        if not tx:
            continue
        txid = tx.get("transaction_id")
        amount = tx.get("amount")
        counterparty = tx.get("counterparty") or ""
        if txid and txid.lower() in complaint_lower:
            return txid
        if amount is not None and str(int(amount)) in complaint_lower:
            return txid
        if counterparty and counterparty in complaint:
            return txid
    return None


def analyze_ticket(payload: Dict[str, Any]) -> Dict[str, Any]:
    # Basic validation
    ticket_id = payload.get("ticket_id")
    complaint = payload.get("complaint")
    if not ticket_id:
        raise ValueError("missing ticket_id")
    if not complaint or not complaint.strip():
        raise ValueError("empty complaint")

    transactions = payload.get("transaction_history") or []
    relevant_tx = _find_matching_transaction(complaint, transactions)

    # Determine evidence verdict
    if relevant_tx:
        # If the matching transaction status is completed and complaint mentions wrong recipient
        tx = next((t for t in transactions if t.get("transaction_id") == relevant_tx), {})
        status = tx.get("status")
        if "wrong" in complaint.lower() or "wrong" in (payload.get("campaign_context") or ""):
            evidence = "consistent"
            case_type = "wrong_transfer"
        else:
            evidence = "insufficient_data"
            case_type = "other"
    else:
        evidence = "insufficient_data"
        case_type = "other"

    severity = "high" if case_type == "wrong_transfer" else "low"
    department = DEPARTMENTS.get(case_type, "customer_support")

    agent_summary = f"Received complaint about {ticket_id}: {complaint[:200]}"
    recommended_next_action = (
        f"Verify {relevant_tx} details with the customer via official channels."
        if relevant_tx
        else "Ask customer for more details and recent transaction IDs."
    )
    customer_reply = (
        f"We have noted your concern about transaction {relevant_tx}. Our team will review and follow up through official channels."
        if relevant_tx
        else "We have received your complaint and need more information to investigate. Please provide recent transaction details."
    )

    human_review_required = True if case_type in ("wrong_transfer", "phishing_or_social_engineering") else False

    result = {
        "ticket_id": ticket_id,
        "relevant_transaction_id": relevant_tx,
        "evidence_verdict": evidence,
        "case_type": case_type,
        "severity": severity,
        "department": department,
        "agent_summary": agent_summary,
        "recommended_next_action": recommended_next_action,
        "customer_reply": customer_reply,
        "human_review_required": human_review_required,
        "confidence": 0.6,
        "reason_codes": [case_type] if case_type else [],
    }

    return result
