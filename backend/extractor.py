from __future__ import annotations

import json
import logging
from typing import Optional

from litellm import completion as litellm_completion

from .config import settings
from .models import DealCard, DealClaim, DealStatus, ExtractionResult

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """你是一个电商优惠信息提取助手。用户会发送微信群里的优惠攻略消息，你需要从中提取结构化信息。

请严格以 JSON 格式输出，字段如下：
{
    "product_name": "商品名称（含规格）",
    "original_price": 原价（数字或null），
    "claimed_price": 到手价（数字或null），
    "claims": [
        {
            "claim_type": "coupon|full_reduction|red_packet|member_discount|cashback|gift|other",
            "description": "优惠描述",
            "platform": "淘宝|京东|拼多多|其他"
        }
    ],
    "steps": ["操作步骤1", "操作步骤2"],
    "valid_from": "开始时间 ISO格式 或 null",
    "valid_until": "截止时间 ISO格式 或 null"
}

注意：
- 只输出 JSON，不要其他文字
- 价格只填数字，不要单位
- claim_type 必须是指定的枚举值之一
- 时间尽量推断，如"今晚8点"推断为今天20:00
- 如果信息不足无法提取，仍然输出JSON，缺失字段填null"""


class DealExtractor:
    def __init__(self, model: Optional[str] = None, api_key: Optional[str] = None):
        self.model = model or settings.llm_model
        self.api_key = api_key or settings.llm_api_key

    def extract(
        self,
        message: str,
        source: str = "",
        source_name: str = "",
    ) -> ExtractionResult:
        try:
            response = litellm_completion(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": message},
                ],
                api_key=self.api_key or None,
                temperature=0.1,
                response_format={"type": "json_object"},
            )
            raw_content = response.choices[0].message.content
            return self._parse_response(raw_content, message, source, source_name)
        except json.JSONDecodeError as e:
            return ExtractionResult(success=False, error=f"JSON 解析失败: {e}")
        except Exception as e:
            logger.exception("LLM 调用失败")
            return ExtractionResult(success=False, error=str(e))

    def _parse_response(
        self,
        raw_content: str,
        original_message: str,
        source: str,
        source_name: str,
    ) -> ExtractionResult:
        try:
            data = json.loads(raw_content)
        except json.JSONDecodeError as e:
            return ExtractionResult(
                success=False,
                error=f"JSON 解析失败: {e}",
                raw_llm_response=raw_content,
            )

        claims = []
        for c in data.get("claims", []):
            claims.append(
                DealClaim(
                    claim_type=c.get("claim_type", "other"),
                    description=c.get("description", ""),
                    platform=c.get("platform", ""),
                )
            )

        from datetime import datetime

        def parse_dt(val: Optional[str]) -> Optional[datetime]:
            if not val:
                return None
            try:
                return datetime.fromisoformat(val)
            except (ValueError, TypeError):
                return None

        card = DealCard(
            product_name=data.get("product_name", "未知商品"),
            original_price=data.get("original_price"),
            claimed_price=data.get("claimed_price"),
            claims=claims,
            steps=data.get("steps", []),
            valid_from=parse_dt(data.get("valid_from")),
            valid_until=parse_dt(data.get("valid_until")),
            status=DealStatus.UNVERIFIED,
            source=source,
            source_name=source_name,
            raw_content=original_message,
        )
        return ExtractionResult(success=True, card=card, raw_llm_response=raw_content)
