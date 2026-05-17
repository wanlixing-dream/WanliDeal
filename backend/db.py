from __future__ import annotations

import json
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, Float, Integer, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import StaticPool

from .config import settings


class Base(DeclarativeBase):
    pass


class DealCardRow(Base):
    __tablename__ = "deal_cards"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_name = Column(String(256), nullable=False, index=True)
    product_url = Column(String(1024), default="")
    original_price = Column(Float, nullable=True)
    claimed_price = Column(Float, nullable=True)
    verified_price = Column(Float, nullable=True)
    claims_json = Column(Text, default="[]")
    steps_json = Column(Text, default="[]")
    valid_from = Column(DateTime, nullable=True)
    valid_until = Column(DateTime, nullable=True)
    status = Column(String(32), default="unverified")
    source = Column(String(64), default="")
    source_name = Column(String(128), default="")
    raw_content = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.now)
    last_checked = Column(DateTime, nullable=True)


_engine_kwargs = {"echo": settings.debug}
if settings.database_url == "sqlite:///" or ":memory:" in settings.database_url:
    _engine_kwargs["connect_args"] = {"check_same_thread": False}
    _engine_kwargs["poolclass"] = StaticPool

engine = create_engine(settings.database_url, **_engine_kwargs)


def init_db():
    Base.metadata.create_all(engine)


def get_session() -> Session:
    return sessionmaker(bind=engine)()


def save_card(session: Session, card) -> int:
    row = DealCardRow(
        product_name=card.product_name,
        product_url=card.product_url,
        original_price=card.original_price,
        claimed_price=card.claimed_price,
        verified_price=card.verified_price,
        claims_json=json.dumps([c.model_dump() for c in card.claims], ensure_ascii=False),
        steps_json=json.dumps(card.steps, ensure_ascii=False),
        valid_from=card.valid_from,
        valid_until=card.valid_until,
        status=card.status.value,
        source=card.source,
        source_name=card.source_name,
        raw_content=card.raw_content,
        created_at=card.created_at,
        last_checked=card.last_checked,
    )
    session.add(row)
    session.commit()
    return row.id


def list_cards(
    session: Session,
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> list[DealCardRow]:
    query = session.query(DealCardRow).order_by(DealCardRow.created_at.desc())
    if status:
        query = query.filter(DealCardRow.status == status)
    return query.offset(offset).limit(limit).all()


def get_card_by_id(session: Session, card_id: int) -> Optional[DealCardRow]:
    return session.query(DealCardRow).filter(DealCardRow.id == card_id).first()
