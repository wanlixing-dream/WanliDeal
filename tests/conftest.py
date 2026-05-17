import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# 测试使用内存数据库，不污染开发数据
os.environ["WANLI_DATABASE_URL"] = "sqlite:///"
os.environ.setdefault("WANLI_LLM_API_KEY", "test-key")
