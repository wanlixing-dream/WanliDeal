from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ClaimType(str, Enum):
    COUPON = "coupon"
    FULL_REDUCTION = "full_reduction"
    RED_PACKET = "red_packet"
    MEMBER_DISCOUNT = "member_discount"
    CASHBACK = "cashback"
    GIFT = "gift"
    OTHER = "other"


class DealStatus(str, Enum):
    ACTIVE = "active"
    EXPIRING_SOON = "expiring_soon"
    EXPIRED = "expired"
    UNVERIFIED = "unverified"


class RawMessage(BaseModel):
    source: str
    group_name: str = ""
    content: str
    image_url: str = ""
    received_at: datetime = Field(default_factory=datetime.now)


class DealClaim(BaseModel):
    claim_type: ClaimType
    description: str
    platform: str = ""
    verified: Optional[bool] = None
    verify_note: str = ""


class DealCard(BaseModel):
    id: Optional[int] = None
    product_name: str
    product_url: str = ""
    original_price: Optional[float] = None
    claimed_price: Optional[float] = None
    verified_price: Optional[float] = None
    claims: list[DealClaim] = Field(default_factory=list)
    steps: list[str] = Field(default_factory=list)
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    status: DealStatus = DealStatus.UNVERIFIED
    source: str = ""
    source_name: str = ""
    raw_content: str = ""
    created_at: datetime = Field(default_factory=datetime.now)
    last_checked: Optional[datetime] = None


class ExtractionResult(BaseModel):
    success: bool
    card: Optional[DealCard] = None
    error: str = ""
    raw_llm_response: str = ""


class PipelineResult(BaseModel):
    success: bool
    card: Optional[DealCard] = None
    extraction_ok: bool = False
    validation_ok: bool = False
    error: str = ""
