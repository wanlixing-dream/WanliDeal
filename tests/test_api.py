import json
from unittest.mock import patch, MagicMock


MOCK_LLM_RESPONSE = json.dumps({
    "product_name": "测试商品",
    "claimed_price": 99.0,
    "original_price": None,
    "claims": [{"claim_type": "coupon", "description": "测试券", "platform": "淘宝"}],
    "steps": ["步骤1"],
    "valid_from": None,
    "valid_until": None,
}, ensure_ascii=False)


def test_health_check(api_client):
    response = api_client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_submit_message(api_client):
    with patch("backend.extractor.litellm_completion") as mock_llm:
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = MOCK_LLM_RESPONSE
        mock_llm.return_value = mock_response

        response = api_client.post("/api/deals/submit", json={
            "content": "测试商品，领券后99元",
            "source": "wechat_group",
            "source_name": "测试群",
        })

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["card"]["product_name"] == "测试商品"


def test_list_deals(api_client):
    response = api_client.get("/api/deals")
    assert response.status_code == 200
    data = response.json()
    assert "deals" in data
    assert isinstance(data["deals"], list)
