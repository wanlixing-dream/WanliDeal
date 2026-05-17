from datetime import datetime, timedelta
from backend.formatter import DealFormatter
from backend.models import DealCard, DealClaim, ClaimType, DealStatus


def test_format_deal_card_to_text():
    card = DealCard(
        product_name="兰蔻小黑瓶精华 50ml",
        claimed_price=189.0,
        original_price=480.0,
        claims=[
            DealClaim(claim_type=ClaimType.COUPON, description="200-30店铺券", platform="淘宝"),
            DealClaim(claim_type=ClaimType.FULL_REDUCTION, description="跨店满300-50", platform="淘宝"),
        ],
        steps=["领取店铺券200-30", "凑满减300-50", "下单付款"],
        status=DealStatus.ACTIVE,
        valid_until=datetime.now() + timedelta(days=1),
        source="wechat_group",
        source_name="618攻略群",
    )
    formatter = DealFormatter()
    text = formatter.to_text(card)

    assert "兰蔻小黑瓶精华" in text
    assert "189" in text
    assert "领取店铺券" in text


def test_format_deal_card_to_dict():
    card = DealCard(
        product_name="测试商品",
        claimed_price=99.0,
        claims=[],
        steps=["步骤1"],
        status=DealStatus.ACTIVE,
    )
    formatter = DealFormatter()
    d = formatter.to_dict(card)

    assert d["product_name"] == "测试商品"
    assert d["claimed_price"] == 99.0
    assert d["status"] == "active"
    assert d["status_label"] == "有效"


def test_status_labels():
    formatter = DealFormatter()
    assert formatter.status_label(DealStatus.ACTIVE) == "有效"
    assert formatter.status_label(DealStatus.EXPIRING_SOON) == "即将过期"
    assert formatter.status_label(DealStatus.EXPIRED) == "已过期"
    assert formatter.status_label(DealStatus.UNVERIFIED) == "未验证"
