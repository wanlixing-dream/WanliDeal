from datetime import datetime, timedelta
from backend.validator import DealValidator
from backend.models import DealCard, DealClaim, ClaimType, DealStatus


def _make_card(valid_from=None, valid_until=None, status=DealStatus.UNVERIFIED):
    return DealCard(
        product_name="测试商品",
        claimed_price=99.0,
        claims=[DealClaim(claim_type=ClaimType.COUPON, description="测试券", platform="淘宝")],
        steps=["步骤1"],
        valid_from=valid_from,
        valid_until=valid_until,
        status=status,
        source="wechat_group",
    )


def test_active_deal():
    validator = DealValidator()
    card = _make_card(
        valid_from=datetime.now() - timedelta(hours=1),
        valid_until=datetime.now() + timedelta(days=2),
    )
    result = validator.validate(card)
    assert result.status == DealStatus.ACTIVE


def test_expired_deal():
    validator = DealValidator()
    card = _make_card(
        valid_until=datetime.now() - timedelta(hours=1),
    )
    result = validator.validate(card)
    assert result.status == DealStatus.EXPIRED


def test_expiring_soon_deal():
    validator = DealValidator()
    card = _make_card(
        valid_until=datetime.now() + timedelta(hours=2),
    )
    result = validator.validate(card)
    assert result.status == DealStatus.EXPIRING_SOON


def test_no_time_info_stays_active():
    validator = DealValidator()
    card = _make_card()
    result = validator.validate(card)
    assert result.status == DealStatus.ACTIVE


def test_not_yet_started():
    validator = DealValidator()
    card = _make_card(
        valid_from=datetime.now() + timedelta(days=1),
        valid_until=datetime.now() + timedelta(days=3),
    )
    result = validator.validate(card)
    assert result.status == DealStatus.ACTIVE
    assert result.last_checked is not None
