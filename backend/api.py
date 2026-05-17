from __future__ import annotations

import json
from typing import Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel

from .db import get_session, save_card, list_cards, get_card_by_id
from .formatter import DealFormatter
from .models import DealCard, DealClaim, DealStatus
from .pipeline import DealPipeline

router = APIRouter(prefix="/api")
pipeline = DealPipeline()
formatter = DealFormatter()


class SubmitRequest(BaseModel):
    content: str
    source: str = "manual"
    source_name: str = ""


def _row_to_card(row) -> DealCard:
    claims = [DealClaim(**c) for c in json.loads(row.claims_json)]
    return DealCard(
        id=row.id,
        product_name=row.product_name,
        product_url=row.product_url,
        original_price=row.original_price,
        claimed_price=row.claimed_price,
        verified_price=row.verified_price,
        claims=claims,
        steps=json.loads(row.steps_json),
        valid_from=row.valid_from,
        valid_until=row.valid_until,
        status=DealStatus(row.status),
        source=row.source,
        source_name=row.source_name,
        raw_content=row.raw_content,
        created_at=row.created_at,
        last_checked=row.last_checked,
    )


@router.get("/health")
def health_check():
    return {"status": "ok"}


@router.post("/deals/submit")
def submit_deal(req: SubmitRequest):
    result = pipeline.process(req.content, source=req.source, source_name=req.source_name)
    if not result.success or result.card is None:
        return {"success": False, "error": result.error}

    session = get_session()
    try:
        card_id = save_card(session, result.card)
        result.card.id = card_id
        return {
            "success": True,
            "card": formatter.to_dict(result.card),
        }
    finally:
        session.close()


@router.get("/deals")
def list_deals(
    status: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    session = get_session()
    try:
        rows = list_cards(session, status=status, limit=limit, offset=offset)
        deals = [formatter.to_dict(_row_to_card(row)) for row in rows]
        return {"deals": deals, "total": len(deals)}
    finally:
        session.close()


@router.get("/deals/{card_id}")
def get_deal(card_id: int):
    session = get_session()
    try:
        row = get_card_by_id(session, card_id)
        if row is None:
            return {"error": "未找到"}
        return {"card": formatter.to_dict(_row_to_card(row))}
    finally:
        session.close()
