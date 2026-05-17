from backend.models import RawMessage, DealClaim, DealCard, ClaimType, DealStatus


def test_raw_message_creation():
    msg = RawMessage(
        source="wechat_group",
        group_name="618攻略群",
        content="今晚8点，兰蔻小黑瓶精华50ml，先领200-30券，叠加跨店满300-50，到手价189元",
    )
    assert msg.source == "wechat_group"
    assert msg.group_name == "618攻略群"
    assert msg.content.startswith("今晚8点")


def test_deal_claim_creation():
    claim = DealClaim(
        claim_type=ClaimType.COUPON,
        description="领取200-30优惠券",
        platform="淘宝",
    )
    assert claim.claim_type == ClaimType.COUPON
    assert claim.verified is None


def test_deal_card_creation():
    card = DealCard(
        product_name="兰蔻小黑瓶精华 50ml",
        claimed_price=189.0,
        claims=[
            DealClaim(claim_type=ClaimType.COUPON, description="200-30店铺券", platform="淘宝"),
            DealClaim(claim_type=ClaimType.FULL_REDUCTION, description="跨店满300-50", platform="淘宝"),
        ],
        steps=["领取店铺券200-30", "加入购物车凑满减300-50", "下单付款"],
        status=DealStatus.ACTIVE,
        source="wechat_group",
        source_name="618攻略群",
    )
    assert card.product_name == "兰蔻小黑瓶精华 50ml"
    assert len(card.claims) == 2
    assert card.status == DealStatus.ACTIVE
