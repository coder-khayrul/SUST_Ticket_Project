from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
from .analyzer import analyze_ticket

app = FastAPI(title="Ticket Investigator Service")


class Transaction(BaseModel):
    transaction_id: str
    timestamp: Optional[str]
    type: Optional[str]
    amount: Optional[float]
    counterparty: Optional[str]
    status: Optional[str]


class AnalyzeRequest(BaseModel):
    ticket_id: str
    complaint: str
    language: Optional[str] = None
    channel: Optional[str] = None
    user_type: Optional[str] = None
    campaign_context: Optional[str] = None
    transaction_history: Optional[List[Transaction]] = None
    metadata: Optional[dict] = None


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/analyze-ticket")
async def analyze_ticket_endpoint(body: AnalyzeRequest, request: Request):
    try:
        result = analyze_ticket(body.dict())
        return JSONResponse(status_code=200, content=result)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="internal server error")
