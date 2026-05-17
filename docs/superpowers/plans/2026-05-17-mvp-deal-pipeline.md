# MVP 优惠攻略处理管道 实现计划

> **面向 AI 代理的工作者：** 必需子技能：使用 superpowers:executing-plans 逐任务实现此计划。步骤使用复选框（`- [ ]`）语法来跟踪进度。

**目标：** 构建一个处理管道，将微信群优惠攻略消息转换为结构化、经过时效验证的标准化攻略卡片，并通过 Web 页面展示。

**架构：** Python FastAPI 后端 + LLM 结构化提取 + 规则引擎时效验证 + SQLite 持久化。前端使用 Vue3 H5 页面。用户通过 API 提交微信群消息文本，系统自动提取优惠信息、验证时效、生成标准化攻略卡片。

**技术栈：**
- Python 3.11+, FastAPI, uvicorn, SQLAlchemy, litellm
- SQLite (开发阶段)
- Vue3 + Vite + TailwindCSS (H5 前端)
- pytest (测试)

---

## 文件结构

```
WanliDeal/
├── .env.example                   # 环境变量模板
├── backend/
│   ├── __init__.py                # 包标识
│   ├── requirements.txt           # Python 依赖
│   ├── main.py                    # FastAPI 入口 + uvicorn 启动
│   ├── config.py                  # 配置管理（API Key、模型选择）
│   ├── models.py                  # Pydantic 数据模型（Deal、Claim、DealCard）
│   ├── db.py                      # SQLite 数据库操作（SQLAlchemy）
│   ├── extractor.py               # LLM 结构化提取：原始文本 → 结构化声明
│   ├── validator.py               # 时效验证：检查声明是否过期/有效
│   ├── formatter.py               # 标准化输出：结构化数据 → 攻略卡片
│   ├── pipeline.py                # 管道编排：串联 extract → validate → format
│   └── api.py                     # API 路由定义
├── frontend/
│   ├── package.json
│   ├── vite.config.ts
│   ├── index.html
│   ├── src/
│   │   ├── main.ts
│   │   ├── App.vue
│   │   ├── components/
│   │   │   ├── DealCard.vue       # 攻略卡片组件
│   │   │   ├── SubmitForm.vue     # 消息提交表单
│   │   │   └── DealList.vue       # 攻略列表
│   │   ├── api.ts                 # 后端 API 调用
│   │   └── types.ts               # TypeScript 类型定义
│   └── tailwind.config.js
├── tests/
│   ├── conftest.py                # pytest fixtures
│   ├── test_models.py             # 数据模型测试
│   ├── test_extractor.py          # 提取器测试
│   ├── test_validator.py          # 验证器测试
│   ├── test_formatter.py          # 格式化器测试
│   ├── test_pipeline.py           # 管道集成测试
│   └── test_api.py                # API 端点测试
└── docs/
    └── superpowers/
        └── plans/
            └── 2026-05-17-mvp-deal-pipeline.md  # 本文件
```

**职责边界：**
- `models.py` — 纯数据定义，无业务逻辑
- `extractor.py` — 唯一与 LLM 交互的模块
- `validator.py` — 纯规则引擎，不调用 LLM
- `formatter.py` — 纯数据转换
- `pipeline.py` — 编排层，串联上述模块
- `api.py` — HTTP 接口层，调用 pipeline

---

### 任务 1：项目骨架与数据模型

**文件：**
- 创建：`backend/requirements.txt`
- 创建：`backend/config.py`
- 创建：`backend/models.py`
- 创建：`tests/conftest.py`
- 创建：`tests/test_models.py`

- [ ] **步骤 1：创建 requirements.txt**

```txt
fastapi==0.115.12
uvicorn[standard]==0.34.2
sqlalchemy==2.0.41
litellm==1.72.4
pydantic==2.11.3
pydantic-settings==2.9.1
httpx==0.28.1
pytest==8.4.0
pytest-asyncio==1.0.0
```

- [ ] **步骤 2：创建 __init__.py 和 .env.example**

```python
# backend/__init__.py
```
（空文件，仅作为包标识）

```bash
# .env.example
WANLI_LLM_MODEL=deepseek/deepseek-chat
WANLI_LLM_API_KEY=your-api-key-here
WANLI_LLM_BASE_URL=
WANLI_DATABASE_URL=sqlite:///./wanlideal.db
WANLI_DEBUG=true
```

- [ ] **步骤 3：安装依赖**

运行：`cd /home/wanlixing/桌面/项目/WanliDeal && python3 -m venv .venv && source .venv/bin/activate && pip install -r backend/requirements.txt`
预期：安装成功，无报错

- [ ] **步骤 4：创建 config.py**

```python
# backend/config.py
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    llm_model: str = "deepseek/deepseek-chat"
    llm_api_key: str = ""
    llm_base_url: str = ""
    database_url: str = "sqlite:///./wanlideal.db"
    debug: bool = True

    model_config = {"env_prefix": "WANLI_", "env_file": ".env"}


settings = Settings()
```

- [ ] **步骤 5：编写 models.py 的失败测试**

```python
# tests/test_models.py
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
```

- [ ] **步骤 6：运行测试验证失败**

运行：`cd /home/wanlixing/桌面/项目/WanliDeal && PYTHONPATH=. .venv/bin/pytest tests/test_models.py -v`
预期：FAIL，ModuleNotFoundError: No module named 'backend.models'

- [ ] **步骤 7：实现 models.py**

```python
# backend/models.py
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ClaimType(str, Enum):
    COUPON = "coupon"
    FULL_REDUCTION = "full_reduction"
    RED_PACKET = "red_packet"
    MEMBER_DISCOUNT = "member_discount"
    CASHBACK = "cashback"
    GIFT = "gift"
    OTHER = "other"


class DealStatus(str, Enum):
    ACTIVE = "active"
    EXPIRING_SOON = "expiring_soon"
    EXPIRED = "expired"
    UNVERIFIED = "unverified"


class RawMessage(BaseModel):
    source: str
    group_name: str = ""
    content: str
    image_url: str = ""
    received_at: datetime = Field(default_factory=datetime.now)


class DealClaim(BaseModel):
    claim_type: ClaimType
    description: str
    platform: str = ""
    verified: Optional[bool] = None
    verify_note: str = ""


class DealCard(BaseModel):
    id: Optional[int] = None
    product_name: str
    product_url: str = ""
    original_price: Optional[float] = None
    claimed_price: Optional[float] = None
    verified_price: Optional[float] = None
    claims: list[DealClaim] = Field(default_factory=list)
    steps: list[str] = Field(default_factory=list)
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    status: DealStatus = DealStatus.UNVERIFIED
    source: str = ""
    source_name: str = ""
    raw_content: str = ""
    created_at: datetime = Field(default_factory=datetime.now)
    last_checked: Optional[datetime] = None


class ExtractionResult(BaseModel):
    success: bool
    card: Optional[DealCard] = None
    error: str = ""
    raw_llm_response: str = ""


class PipelineResult(BaseModel):
    success: bool
    card: Optional[DealCard] = None
    extraction_ok: bool = False
    validation_ok: bool = False
    error: str = ""
```

- [ ] **步骤 8：运行测试验证通过**

运行：`cd /home/wanlixing/桌面/项目/WanliDeal && PYTHONPATH=. .venv/bin/pytest tests/test_models.py -v`
预期：3 passed

- [ ] **步骤 9：创建 conftest.py 和 commit**

```python
# tests/conftest.py
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# 测试使用内存数据库，不污染开发数据
os.environ["WANLI_DATABASE_URL"] = "sqlite:///"
os.environ.setdefault("WANLI_LLM_API_KEY", "test-key")
```

```bash
git add -A
git commit -m "feat: 初始化项目骨架与数据模型（任务 1/7）"
```

---

### 任务 2：LLM 结构化提取器

**文件：**
- 创建：`backend/extractor.py`
- 创建：`tests/test_extractor.py`

- [ ] **步骤 1：编写提取器失败测试**

```python
# tests/test_extractor.py
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
```

- [ ] **步骤 2：运行测试验证失败**

运行：`cd /home/wanlixing/桌面/项目/WanliDeal && PYTHONPATH=. .venv/bin/pytest tests/test_extractor.py -v`
预期：FAIL，ModuleNotFoundError: No module named 'backend.extractor'

- [ ] **步骤 3：实现 extractor.py**

```python
# backend/extractor.py
from __future__ import annotations

import json
import logging
from typing import Optional

import litellm
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
```

- [ ] **步骤 4：运行测试验证通过**

运行：`cd /home/wanlixing/桌面/项目/WanliDeal && PYTHONPATH=. .venv/bin/pytest tests/test_extractor.py -v`
预期：3 passed

- [ ] **步骤 5：Commit**

```bash
git add -A
git commit -m "feat: 添加 LLM 结构化提取器（任务 2/7）"
```

---

### 任务 3：时效验证器

**文件：**
- 创建：`backend/validator.py`
- 创建：`tests/test_validator.py`

- [ ] **步骤 1：编写验证器失败测试**

```python
# tests/test_validator.py
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


def test_no_time_info_stays_unverified():
    validator = DealValidator()
    card = _make_card()
    result = validator.validate(card)
    assert result.status == DealStatus.ACTIVE  # 没有时间信息默认有效


def test_not_yet_started():
    validator = DealValidator()
    card = _make_card(
        valid_from=datetime.now() + timedelta(days=1),
        valid_until=datetime.now() + timedelta(days=3),
    )
    result = validator.validate(card)
    assert result.status == DealStatus.ACTIVE  # 未开始也标记为有效，前端显示倒计时
    assert result.last_checked is not None
```

- [ ] **步骤 2：运行测试验证失败**

运行：`cd /home/wanlixing/桌面/项目/WanliDeal && PYTHONPATH=. .venv/bin/pytest tests/test_validator.py -v`
预期：FAIL，ModuleNotFoundError

- [ ] **步骤 3：实现 validator.py**

```python
# backend/validator.py
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
```

- [ ] **步骤 4：运行测试验证通过**

运行：`cd /home/wanlixing/桌面/项目/WanliDeal && PYTHONPATH=. .venv/bin/pytest tests/test_validator.py -v`
预期：5 passed

- [ ] **步骤 5：Commit**

```bash
git add -A
git commit -m "feat: 添加时效验证器（任务 3/7）"
```

---

### 任务 4：标准化格式化器

**文件：**
- 创建：`backend/formatter.py`
- 创建：`tests/test_formatter.py`

- [ ] **步骤 1：编写格式化器失败测试**

```python
# tests/test_formatter.py
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
```

- [ ] **步骤 2：运行测试验证失败**

运行：`cd /home/wanlixing/桌面/项目/WanliDeal && PYTHONPATH=. .venv/bin/pytest tests/test_formatter.py -v`
预期：FAIL

- [ ] **步骤 3：实现 formatter.py**

```python
# backend/formatter.py
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
```

- [ ] **步骤 4：运行测试验证通过**

运行：`cd /home/wanlixing/桌面/项目/WanliDeal && PYTHONPATH=. .venv/bin/pytest tests/test_formatter.py -v`
预期：3 passed

- [ ] **步骤 5：Commit**

```bash
git add -A
git commit -m "feat: 添加标准化格式化器（任务 4/7）"
```

---

### 任务 5：管道编排与数据库

**文件：**
- 创建：`backend/db.py`
- 创建：`backend/pipeline.py`
- 创建：`tests/test_pipeline.py`

- [ ] **步骤 1：实现 db.py**

```python
# backend/db.py
from __future__ import annotations

import json
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, Float, Integer, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

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


engine = create_engine(settings.database_url, echo=settings.debug)


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
```

- [ ] **步骤 2：编写管道失败测试**

```python
# tests/test_pipeline.py
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
```

- [ ] **步骤 3：运行测试验证失败**

运行：`cd /home/wanlixing/桌面/项目/WanliDeal && PYTHONPATH=. .venv/bin/pytest tests/test_pipeline.py -v`
预期：FAIL

- [ ] **步骤 4：实现 pipeline.py**

```python
# backend/pipeline.py
from __future__ import annotations

import logging

from .extractor import DealExtractor
from .formatter import DealFormatter
from .models import PipelineResult
from .validator import DealValidator

logger = logging.getLogger(__name__)


class DealPipeline:
    def __init__(self):
        self.extractor = DealExtractor()
        self.validator = DealValidator()
        self.formatter = DealFormatter()

    def process(
        self,
        message: str,
        source: str = "",
        source_name: str = "",
    ) -> PipelineResult:
        # Step 1: 提取
        extraction = self.extractor.extract(message, source=source, source_name=source_name)
        if not extraction.success or extraction.card is None:
            return PipelineResult(
                success=False,
                extraction_ok=False,
                error=extraction.error or "提取失败",
            )

        # Step 2: 验证时效
        card = self.validator.validate(extraction.card)

        # Step 3: 完成
        return PipelineResult(
            success=True,
            card=card,
            extraction_ok=True,
            validation_ok=True,
        )
```

- [ ] **步骤 5：运行测试验证通过**

运行：`cd /home/wanlixing/桌面/项目/WanliDeal && PYTHONPATH=. .venv/bin/pytest tests/test_pipeline.py -v`
预期：2 passed

- [ ] **步骤 6：Commit**

```bash
git add -A
git commit -m "feat: 添加管道编排与数据库（任务 5/7）"
```

---

### 任务 6：API 接口

**文件：**
- 创建：`backend/api.py`
- 创建：`backend/main.py`
- 创建：`tests/test_api.py`

- [ ] **步骤 1：编写 API 失败测试**

```python
# tests/test_api.py
import json
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from backend.main import app


client = TestClient(app)

MOCK_LLM_RESPONSE = json.dumps({
    "product_name": "测试商品",
    "claimed_price": 99.0,
    "original_price": None,
    "claims": [{"claim_type": "coupon", "description": "测试券", "platform": "淘宝"}],
    "steps": ["步骤1"],
    "valid_from": None,
    "valid_until": None,
}, ensure_ascii=False)


def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_submit_message():
    with patch("backend.extractor.litellm_completion") as mock_llm:
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = MOCK_LLM_RESPONSE
        mock_llm.return_value = mock_response

        response = client.post("/api/deals/submit", json={
            "content": "测试商品，领券后99元",
            "source": "wechat_group",
            "source_name": "测试群",
        })

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["card"]["product_name"] == "测试商品"


def test_list_deals():
    response = client.get("/api/deals")
    assert response.status_code == 200
    data = response.json()
    assert "deals" in data
    assert isinstance(data["deals"], list)
```

- [ ] **步骤 2：运行测试验证失败**

运行：`cd /home/wanlixing/桌面/项目/WanliDeal && PYTHONPATH=. .venv/bin/pytest tests/test_api.py -v`
预期：FAIL

- [ ] **步骤 3：实现 api.py**

```python
# backend/api.py
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel

from .db import get_session, save_card, list_cards, get_card_by_id
from .formatter import DealFormatter
from .pipeline import DealPipeline

router = APIRouter(prefix="/api")
pipeline = DealPipeline()
formatter = DealFormatter()


class SubmitRequest(BaseModel):
    content: str
    source: str = "manual"
    source_name: str = ""


@router.get("/health")
def health_check():
    return {"status": "ok"}


@router.post("/deals/submit")
def submit_deal(req: SubmitRequest):
    result = pipeline.process(req.content, source=req.source, source_name=req.source_name)
    if not result.success or result.card is None:
        return {"success": False, "error": result.error}

    session = get_session()
    try:
        card_id = save_card(session, result.card)
        result.card.id = card_id
        return {
            "success": True,
            "card": formatter.to_dict(result.card),
        }
    finally:
        session.close()


@router.get("/deals")
def list_deals(
    status: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    session = get_session()
    try:
        rows = list_cards(session, status=status, limit=limit, offset=offset)
        deals = []
        for row in rows:
            import json
            from .models import DealCard, DealClaim, DealStatus
            claims = [DealClaim(**c) for c in json.loads(row.claims_json)]
            card = DealCard(
                id=row.id,
                product_name=row.product_name,
                product_url=row.product_url,
                original_price=row.original_price,
                claimed_price=row.claimed_price,
                verified_price=row.verified_price,
                claims=claims,
                steps=json.loads(row.steps_json),
                valid_from=row.valid_from,
                valid_until=row.valid_until,
                status=DealStatus(row.status),
                source=row.source,
                source_name=row.source_name,
                raw_content=row.raw_content,
                created_at=row.created_at,
                last_checked=row.last_checked,
            )
            deals.append(formatter.to_dict(card))
        return {"deals": deals, "total": len(deals)}
    finally:
        session.close()


@router.get("/deals/{card_id}")
def get_deal(card_id: int):
    session = get_session()
    try:
        row = get_card_by_id(session, card_id)
        if row is None:
            return {"error": "未找到"}
        import json
        from .models import DealCard, DealClaim, DealStatus
        claims = [DealClaim(**c) for c in json.loads(row.claims_json)]
        card = DealCard(
            id=row.id,
            product_name=row.product_name,
            claims=claims,
            steps=json.loads(row.steps_json),
            status=DealStatus(row.status),
            claimed_price=row.claimed_price,
            original_price=row.original_price,
            source=row.source,
            source_name=row.source_name,
            created_at=row.created_at,
        )
        return {"card": formatter.to_dict(card)}
    finally:
        session.close()
```

- [ ] **步骤 4：实现 main.py**

```python
# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import router
from .db import init_db

app = FastAPI(title="WanliDeal - 618攻略验证助手", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.on_event("startup")
def startup():
    init_db()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
```

- [ ] **步骤 5：运行测试验证通过**

运行：`cd /home/wanlixing/桌面/项目/WanliDeal && PYTHONPATH=. .venv/bin/pytest tests/test_api.py -v`
预期：3 passed

- [ ] **步骤 6：运行全部测试**

运行：`cd /home/wanlixing/桌面/项目/WanliDeal && PYTHONPATH=. .venv/bin/pytest tests/ -v`
预期：全部通过（13+ tests）

- [ ] **步骤 7：Commit**

```bash
git add -A
git commit -m "feat: 添加 API 接口与 FastAPI 入口（任务 6/7）"
```

---

### 任务 7：H5 前端页面

**文件：**
- 创建：`frontend/package.json`
- 创建：`frontend/vite.config.ts`
- 创建：`frontend/index.html`
- 创建：`frontend/tailwind.config.js`
- 创建：`frontend/postcss.config.js`
- 创建：`frontend/tsconfig.json`
- 创建：`frontend/src/main.ts`
- 创建：`frontend/src/App.vue`
- 创建：`frontend/src/types.ts`
- 创建：`frontend/src/api.ts`
- 创建：`frontend/src/components/SubmitForm.vue`
- 创建：`frontend/src/components/DealCard.vue`
- 创建：`frontend/src/components/DealList.vue`
- 创建：`frontend/src/style.css`

- [ ] **步骤 1：初始化前端项目**

运行：
```bash
cd /home/wanlixing/桌面/项目/WanliDeal/frontend && npm create vite@latest . -- --template vue-ts
npm install
npm install -D tailwindcss @tailwindcss/vite
```

- [ ] **步骤 2：配置 TailwindCSS**

更新 `frontend/vite.config.ts`:
```typescript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [vue(), tailwindcss()],
  server: {
    proxy: {
      '/api': 'http://localhost:8000',
    },
  },
})
```

更新 `frontend/src/style.css`:
```css
@import "tailwindcss";
```

- [ ] **步骤 3：创建类型定义和 API 模块**

`frontend/src/types.ts`:
```typescript
export interface DealClaim {
  type: string
  type_label: string
  description: string
  platform: string
  verified: boolean | null
}

export interface DealCardData {
  id: number | null
  product_name: string
  product_url: string
  original_price: number | null
  claimed_price: number | null
  verified_price: number | null
  claims: DealClaim[]
  steps: string[]
  valid_from: string | null
  valid_until: string | null
  status: string
  status_label: string
  status_icon: string
  source: string
  source_name: string
  created_at: string
}
```

`frontend/src/api.ts`:
```typescript
import type { DealCardData } from './types'

const BASE_URL = '/api'

export async function submitDeal(content: string, source = 'manual', sourceName = ''): Promise<{
  success: boolean
  card?: DealCardData
  error?: string
}> {
  const res = await fetch(`${BASE_URL}/deals/submit`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content, source, source_name: sourceName }),
  })
  return res.json()
}

export async function listDeals(status?: string): Promise<{ deals: DealCardData[] }> {
  const params = status ? `?status=${status}` : ''
  const res = await fetch(`${BASE_URL}/deals${params}`)
  return res.json()
}
```

- [ ] **步骤 4：实现组件**

`frontend/src/components/SubmitForm.vue`:
```vue
<script setup lang="ts">
import { ref } from 'vue'
import { submitDeal } from '../api'
import type { DealCardData } from '../types'

const emit = defineEmits<{ submitted: [card: DealCardData] }>()

const content = ref('')
const sourceName = ref('')
const loading = ref(false)
const error = ref('')

async function handleSubmit() {
  if (!content.value.trim()) return
  loading.value = true
  error.value = ''
  try {
    const result = await submitDeal(content.value, 'wechat_group', sourceName.value)
    if (result.success && result.card) {
      emit('submitted', result.card)
      content.value = ''
    } else {
      error.value = result.error || '处理失败'
    }
  } catch (e: any) {
    error.value = e.message || '网络错误'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
    <h2 class="text-lg font-semibold text-gray-800 mb-4">粘贴攻略消息</h2>
    <div class="space-y-3">
      <input
        v-model="sourceName"
        type="text"
        placeholder="来源群名（可选）"
        class="w-full px-4 py-2 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-orange-400"
      />
      <textarea
        v-model="content"
        placeholder="粘贴微信群里的优惠攻略消息..."
        rows="5"
        class="w-full px-4 py-3 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-orange-400 resize-none"
      />
      <button
        @click="handleSubmit"
        :disabled="loading || !content.trim()"
        class="w-full py-3 bg-gradient-to-r from-orange-500 to-red-500 text-white rounded-xl font-medium disabled:opacity-50 transition-all hover:shadow-lg"
      >
        {{ loading ? '分析中...' : '分析攻略' }}
      </button>
      <p v-if="error" class="text-red-500 text-sm">{{ error }}</p>
    </div>
  </div>
</template>
```

`frontend/src/components/DealCard.vue`:
```vue
<script setup lang="ts">
import type { DealCardData } from '../types'

defineProps<{ deal: DealCardData }>()

function formatTime(iso: string | null): string {
  if (!iso) return ''
  const d = new Date(iso)
  return `${d.getMonth() + 1}/${d.getDate()} ${d.getHours()}:${String(d.getMinutes()).padStart(2, '0')}`
}

function statusColor(status: string): string {
  switch (status) {
    case 'active': return 'bg-green-100 text-green-700'
    case 'expiring_soon': return 'bg-yellow-100 text-yellow-700'
    case 'expired': return 'bg-gray-100 text-gray-500'
    default: return 'bg-blue-100 text-blue-700'
  }
}
</script>

<template>
  <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-5 space-y-3">
    <div class="flex items-start justify-between">
      <h3 class="font-semibold text-gray-800 text-base leading-tight flex-1">
        {{ deal.status_icon }} {{ deal.product_name }}
      </h3>
      <span :class="statusColor(deal.status)" class="px-2 py-0.5 rounded-full text-xs font-medium whitespace-nowrap ml-2">
        {{ deal.status_label }}
      </span>
    </div>

    <div v-if="deal.claimed_price" class="flex items-baseline gap-2">
      <span class="text-2xl font-bold text-red-500">¥{{ deal.claimed_price }}</span>
      <span v-if="deal.original_price" class="text-sm text-gray-400 line-through">¥{{ deal.original_price }}</span>
    </div>

    <div v-if="deal.claims.length" class="space-y-1">
      <div v-for="(c, i) in deal.claims" :key="i" class="flex items-center gap-1.5 text-sm text-gray-600">
        <span class="px-1.5 py-0.5 bg-orange-50 text-orange-600 rounded text-xs">{{ c.type_label }}</span>
        <span>{{ c.description }}</span>
      </div>
    </div>

    <div v-if="deal.steps.length" class="bg-gray-50 rounded-xl p-3 space-y-1">
      <div v-for="(step, i) in deal.steps" :key="i" class="text-sm text-gray-700">
        <span class="text-orange-500 font-medium mr-1">{{ i + 1 }}.</span> {{ step }}
      </div>
    </div>

    <div class="flex items-center justify-between text-xs text-gray-400 pt-1">
      <span v-if="deal.valid_until">截止 {{ formatTime(deal.valid_until) }}</span>
      <span>{{ deal.source_name || deal.source }}</span>
    </div>
  </div>
</template>
```

`frontend/src/components/DealList.vue`:
```vue
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { listDeals } from '../api'
import type { DealCardData } from '../types'
import DealCard from './DealCard.vue'

const deals = ref<DealCardData[]>([])
const loading = ref(false)
const filter = ref<string>('')

async function refresh() {
  loading.value = true
  try {
    const data = await listDeals(filter.value || undefined)
    deals.value = data.deals
  } finally {
    loading.value = false
  }
}

function addDeal(card: DealCardData) {
  deals.value.unshift(card)
}

defineExpose({ addDeal, refresh })

onMounted(refresh)
</script>

<template>
  <div class="space-y-4">
    <div class="flex items-center gap-2">
      <button
        v-for="f in [
          { value: '', label: '全部' },
          { value: 'active', label: '有效' },
          { value: 'expiring_soon', label: '即将过期' },
        ]"
        :key="f.value"
        @click="filter = f.value; refresh()"
        :class="filter === f.value
          ? 'bg-orange-500 text-white'
          : 'bg-gray-100 text-gray-600 hover:bg-gray-200'"
        class="px-3 py-1.5 rounded-full text-sm font-medium transition-colors"
      >
        {{ f.label }}
      </button>
      <button @click="refresh" class="ml-auto text-sm text-gray-400 hover:text-gray-600">刷新</button>
    </div>

    <div v-if="loading" class="text-center py-8 text-gray-400">加载中...</div>
    <div v-else-if="deals.length === 0" class="text-center py-8 text-gray-400">暂无攻略</div>
    <div v-else class="space-y-3">
      <DealCard v-for="deal in deals" :key="deal.id ?? deal.created_at" :deal="deal" />
    </div>
  </div>
</template>
```

- [ ] **步骤 5：实现 App.vue**

```vue
<script setup lang="ts">
import { ref } from 'vue'
import SubmitForm from './components/SubmitForm.vue'
import DealList from './components/DealList.vue'
import type { DealCardData } from './types'

const dealList = ref<InstanceType<typeof DealList>>()

function onSubmitted(card: DealCardData) {
  dealList.value?.addDeal(card)
}
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <header class="bg-gradient-to-r from-orange-500 to-red-500 text-white py-6 px-4">
      <div class="max-w-lg mx-auto">
        <h1 class="text-2xl font-bold">WanliDeal</h1>
        <p class="text-orange-100 text-sm mt-1">618 攻略验证助手 · 帮你辨别真假优惠</p>
      </div>
    </header>
    <main class="max-w-lg mx-auto px-4 py-6 space-y-6">
      <SubmitForm @submitted="onSubmitted" />
      <DealList ref="dealList" />
    </main>
  </div>
</template>
```

- [ ] **步骤 6：验证前端可运行**

运行：
```bash
cd /home/wanlixing/桌面/项目/WanliDeal/frontend && npm run dev
```
预期：Vite dev server 启动，访问 http://localhost:5173 可看到页面

同时启动后端：
```bash
cd /home/wanlixing/桌面/项目/WanliDeal && PYTHONPATH=. .venv/bin/uvicorn backend.main:app --reload --port 8000
```
预期：FastAPI 启动，前端可通过代理访问后端 API

- [ ] **步骤 7：Commit**

```bash
git add -A
git commit -m "feat: 添加 H5 前端页面（任务 7/7）"
```

---

## 验证清单

全部任务完成后：

1. 运行：`PYTHONPATH=. .venv/bin/pytest tests/ -v` — 全部通过
2. 启动后端：`PYTHONPATH=. .venv/bin/uvicorn backend.main:app --reload`
3. 启动前端：`cd frontend && npm run dev`
4. 在页面粘贴一条真实微信群攻略消息，验证：
   - 结构化提取成功
   - 攻略卡片正确展示
   - 时效状态正确标记
