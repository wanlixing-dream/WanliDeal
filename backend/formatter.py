from __future__ import annotations

from typing import Any

from .models import DealCard, DealStatus

STATUS_LABELS = {
    DealStatus.ACTIVE: "有效",
    DealStatus.EXPIRING_SOON: "即将过期",
    DealStatus.EXPIRED: "已过期",
    DealStatus.UNVERIFIED: "未验证",
}

STATUS_ICONS = {
    DealStatus.ACTIVE: "✅",
    DealStatus.EXPIRING_SOON: "⏰",
    DealStatus.EXPIRED: "❌",
    DealStatus.UNVERIFIED: "❓",
}

CLAIM_TYPE_LABELS = {
    "coupon": "优惠券",
    "full_reduction": "满减",
    "red_packet": "红包",
    "member_discount": "会员折扣",
    "cashback": "返现",
    "gift": "赠品",
    "other": "其他",
}


class DealFormatter:
    def status_label(self, status: DealStatus) -> str:
        return STATUS_LABELS.get(status, "未知")

    def to_text(self, card: DealCard) -> str:
        icon = STATUS_ICONS.get(card.status, "")
        lines = [
            f"{icon} {card.product_name}",
        ]
        if card.original_price and card.claimed_price:
            discount = round((1 - card.claimed_price / card.original_price) * 100)
            lines.append(f"💰 到手价: {card.claimed_price}元（原价{card.original_price}元，省{discount}%）")
        elif card.claimed_price:
            lines.append(f"💰 到手价: {card.claimed_price}元")

        if card.claims:
            lines.append("📋 优惠明细:")
            for c in card.claims:
                label = CLAIM_TYPE_LABELS.get(c.claim_type.value, c.claim_type.value)
                lines.append(f"  · [{label}] {c.description}")

        if card.steps:
            lines.append("📝 操作步骤:")
            for i, step in enumerate(card.steps, 1):
                lines.append(f"  {i}. {step}")

        if card.valid_until:
            lines.append(f"⏰ 截止: {card.valid_until.strftime('%m/%d %H:%M')}")

        lines.append(f"{icon} {self.status_label(card.status)} | 来源: {card.source_name or card.source}")
        return "\n".join(lines)

    def to_dict(self, card: DealCard) -> dict[str, Any]:
        return {
            "id": card.id,
            "product_name": card.product_name,
            "product_url": card.product_url,
            "original_price": card.original_price,
            "claimed_price": card.claimed_price,
            "verified_price": card.verified_price,
            "claims": [
                {
                    "type": c.claim_type.value,
                    "type_label": CLAIM_TYPE_LABELS.get(c.claim_type.value, c.claim_type.value),
                    "description": c.description,
                    "platform": c.platform,
                    "verified": c.verified,
                }
                for c in card.claims
            ],
            "steps": card.steps,
            "valid_from": card.valid_from.isoformat() if card.valid_from else None,
            "valid_until": card.valid_until.isoformat() if card.valid_until else None,
            "status": card.status.value,
            "status_label": self.status_label(card.status),
            "status_icon": STATUS_ICONS.get(card.status, ""),
            "source": card.source,
            "source_name": card.source_name,
            "created_at": card.created_at.isoformat(),
        }
