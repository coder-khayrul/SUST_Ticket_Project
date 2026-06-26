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


import re


def _find_matching_transaction(complaint: str, transactions: Optional[List[Dict[str, Any]]]) -> Optional[str]:
    if not transactions:
        return None
    complaint_lower = complaint.lower()
    # find explicit transaction id mention
    for tx in transactions:
        if not tx:
            continue
        txid = tx.get("transaction_id")
        if txid and txid.lower() in complaint_lower:
            return txid
    # find amount mention like 5000 or 5,000
    amounts_in_complaint = re.findall(r"\b[0-9]{2,6}(?:,[0-9]{3})?\b", complaint.replace('৳',''))
    amounts_norm = {int(a.replace(',','')) for a in amounts_in_complaint}
    for tx in transactions:
        if not tx:
            continue
        amount = tx.get("amount")
        counterparty = tx.get("counterparty") or ""
        txid = tx.get("transaction_id")
        if amount is not None and int(amount) in amounts_norm:
            return txid
        # exact counterparty match
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
    # classify case type based on complaint keywords
    c_lower = complaint.lower()
    case_type = "other"
    evidence = "insufficient_data"

    if relevant_tx:
        tx = next((t for t in transactions if t.get("transaction_id") == relevant_tx), {})
        status = (tx.get("status") or "").lower()
        if any(k in c_lower for k in ("wrong", "wrong number", "wrong recipient", "sent to wrong")):
            case_type = "wrong_transfer"
            evidence = "consistent"
        elif any(k in c_lower for k in ("refund", "refund request", "please refund")):
            case_type = "refund_request"
            evidence = "insufficient_data"
        elif any(k in c_lower for k in ("failed", "payment failed", "did not go through")):
            case_type = "payment_failed"
            evidence = "consistent" if status == "failed" else "insufficient_data"
        elif any(k in c_lower for k in ("duplicate", "charged twice", "double charged")):
            case_type = "duplicate_payment"
            evidence = "consistent"
        elif any(k in c_lower for k in ("phishing", "otp", "pin", "password", "scam", "social engineering")):
            case_type = "phishing_or_social_engineering"
            evidence = "insufficient_data"
        else:
            case_type = "other"
            evidence = "insufficient_data"
    else:
        evidence = "insufficient_data"
        case_type = "other"

    severity = "high" if case_type in ("wrong_transfer", "phishing_or_social_engineering") else "low"
    department = DEPARTMENTS.get(case_type, "customer_support")

    agent_summary = f"Received complaint {ticket_id}: {complaint[:200]}"
    # Safety-conscious next action and customer reply
    if relevant_tx:
        recommended_next_action = (
            f"Verify details of {relevant_tx} with the customer and escalate to {department} if needed. Do not confirm refunds without authority."
        )
        customer_reply = (
            f"We have noted your concern about transaction {relevant_tx}. Any eligible amount will be returned through official channels after investigation."
        )
    else:
        recommended_next_action = (
            "Request additional transaction details from the customer (transaction id, timestamp, amount). Use only official support channels."
        )
        customer_reply = (
            "We have received your complaint and need more information to investigate. Please provide recent transaction details through official support channels."
        )

    human_review_required = True if case_type in ("wrong_transfer", "phishing_or_social_engineering") or (transactions and any((t.get("amount") or 0) >= 10000 for t in transactions)) else False

    # confidence heuristic
    confidence = 0.9 if evidence == "consistent" else 0.5

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
        "confidence": float(confidence),
        "reason_codes": [case_type] if case_type else [],
    }

    return result
