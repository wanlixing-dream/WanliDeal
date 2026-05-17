import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# 测试使用内存数据库，不污染开发数据
os.environ["WANLI_DATABASE_URL"] = "sqlite:///"
os.environ["WANLI_DEBUG"] = "false"
os.environ.setdefault("WANLI_LLM_API_KEY", "test-key")

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def api_client():
    from backend.main import app
    from backend.db import init_db
    init_db()
    with TestClient(app) as client:
        yield client
