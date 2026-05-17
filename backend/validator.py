from __future__ import annotations

from datetime import datetime, timedelta

from .models import DealCard, DealStatus

EXPIRING_SOON_THRESHOLD = timedelta(hours=6)


class DealValidator:
    def __init__(self, expiring_threshold: timedelta = EXPIRING_SOON_THRESHOLD):
        self.expiring_threshold = expiring_threshold

    def validate(self, card: DealCard) -> DealCard:
        now = datetime.now()
        card.last_checked = now

        if card.valid_until is not None:
            if card.valid_until < now:
                card.status = DealStatus.EXPIRED
                return card
            if card.valid_until - now < self.expiring_threshold:
                card.status = DealStatus.EXPIRING_SOON
                return card

        card.status = DealStatus.ACTIVE
        return card
