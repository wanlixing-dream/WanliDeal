import json
import pytest
from unittest.mock import patch, MagicMock
from backend.pipeline import DealPipeline
from backend.models import DealStatus


SAMPLE_MESSAGE = "兰蔻小黑瓶50ml，领200-30券，叠加跨店满300-50，到手189元，6月20号截止"

MOCK_LLM_RESPONSE = json.dumps({
    "product_name": "兰蔻小黑瓶精华 50ml",
    "original_price": 480.0,
    "claimed_price": 189.0,
    "claims": [
        {"claim_type": "coupon", "description": "200-30店铺券", "platform": "淘宝"},
        {"claim_type": "full_reduction", "description": "跨店满300-50", "platform": "淘宝"},
    ],
    "steps": ["领取店铺券200-30", "凑满减300-50", "下单付款"],
    "valid_from": None,
    "valid_until": "2026-06-20T23:59:59",
}, ensure_ascii=False)


def test_pipeline_end_to_end():
    pipeline = DealPipeline()
    with patch("backend.extractor.litellm_completion") as mock_llm:
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = MOCK_LLM_RESPONSE
        mock_llm.return_value = mock_response

        result = pipeline.process(SAMPLE_MESSAGE, source="wechat_group", source_name="618攻略群")

    assert result.success is True
    assert result.extraction_ok is True
    assert result.validation_ok is True
    assert result.card is not None
    assert result.card.product_name == "兰蔻小黑瓶精华 50ml"
    assert result.card.status == DealStatus.ACTIVE


def test_pipeline_with_extraction_failure():
    pipeline = DealPipeline()
    with patch("backend.extractor.litellm_completion") as mock_llm:
        mock_llm.side_effect = Exception("连接超时")

        result = pipeline.process("测试消息")

    assert result.success is False
    assert result.extraction_ok is False
