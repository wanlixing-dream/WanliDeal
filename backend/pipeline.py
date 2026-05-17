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
