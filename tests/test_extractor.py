import json
import pytest
from unittest.mock import patch, MagicMock
from backend.extractor import DealExtractor
from backend.models import ClaimType


SAMPLE_MESSAGE = "今晚8点，兰蔻小黑瓶精华50ml，先领200-30券，叠加跨店满300-50，到手价189元"

MOCK_LLM_RESPONSE = json.dumps({
    "product_name": "兰蔻小黑瓶精华 50ml",
    "original_price": None,
    "claimed_price": 189.0,
    "claims": [
        {"claim_type": "coupon", "description": "200-30店铺券", "platform": "淘宝"},
        {"claim_type": "full_reduction", "description": "跨店满300-50", "platform": "淘宝"},
    ],
    "steps": ["领取店铺券200-30", "加入购物车凑跨店满减300-50", "下单付款"],
    "valid_from": None,
    "valid_until": "2026-06-20T23:59:59",
}, ensure_ascii=False)


def test_extractor_parses_llm_response():
    extractor = DealExtractor()
    with patch("backend.extractor.litellm_completion") as mock_llm:
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = MOCK_LLM_RESPONSE
        mock_llm.return_value = mock_response

        result = extractor.extract(SAMPLE_MESSAGE, source="wechat_group", source_name="618攻略群")

    assert result.success is True
    assert result.card is not None
    assert result.card.product_name == "兰蔻小黑瓶精华 50ml"
    assert result.card.claimed_price == 189.0
    assert len(result.card.claims) == 2
    assert result.card.claims[0].claim_type == ClaimType.COUPON
    assert len(result.card.steps) == 3


def test_extractor_handles_invalid_json():
    extractor = DealExtractor()
    with patch("backend.extractor.litellm_completion") as mock_llm:
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "这不是JSON"
        mock_llm.return_value = mock_response

        result = extractor.extract("测试消息")

    assert result.success is False
    assert "JSON" in result.error or "json" in result.error


def test_extractor_handles_llm_error():
    extractor = DealExtractor()
    with patch("backend.extractor.litellm_completion") as mock_llm:
        mock_llm.side_effect = Exception("API 错误")

        result = extractor.extract("测试消息")

    assert result.success is False
    assert "API" in result.error or "错误" in result.error
