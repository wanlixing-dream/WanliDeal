# WanliDeal

WanliDeal 是一个面向 618 / 电商优惠活动的攻略验证助手，用于提交、解析、验证并展示优惠攻略信息。

项目由两部分组成：

- **后端**：FastAPI + SQLite，负责优惠攻略解析、验证、存储和 API 服务
- **前端**：Vue 3 + TypeScript + Vite，负责页面展示和用户交互

## 功能特性

- 提交优惠攻略文本
- 自动解析商品、价格、优惠规则、领取步骤等信息
- 保存优惠攻略卡片
- 查看攻略列表
- 提供健康检查接口
- 前端通过 `/api` 自动代理到后端服务

## 项目结构

```text
WanliDeal/
├── backend/                 # FastAPI 后端
│   ├── api.py               # API 路由
│   ├── config.py            # 配置项
│   ├── db.py                # 数据库初始化与访问
│   ├── extractor.py         # 攻略信息提取
│   ├── formatter.py         # 数据格式化
│   ├── main.py              # 后端入口
│   ├── models.py            # 数据模型
│   ├── pipeline.py          # 攻略处理流水线
│   ├── validator.py         # 数据验证
│   └── requirements.txt     # Python 依赖
├── frontend/                # Vue 前端
│   ├── src/
│   ├── package.json
│   └── vite.config.ts
├── tests/                   # 后端测试
├── docs/                    # 项目文档
├── .env.example             # 环境变量示例
└── start.ps1                # Windows 一键启动脚本
```

## 环境要求

请先安装：

- Python 3.10+
- Node.js 18+
- npm
- Git

## 快速启动

### 方式一：使用启动脚本

在项目根目录运行：

```powershell
.\start.ps1
```

脚本会自动完成：

- 检查并创建 `.env`
- 创建 Python 虚拟环境 `.venv`
- 安装后端依赖
- 安装前端依赖
- 启动后端服务
- 启动前端开发服务

启动后访问：

```text
前端页面：http://localhost:5173
后端接口：http://localhost:8000
健康检查：http://localhost:8000/api/health
```

### 方式二：手动启动

#### 1. 准备环境变量

复制环境变量示例：

```powershell
Copy-Item .env.example .env
```

根据需要编辑 `.env`：

```env
WANLI_LLM_MODEL=deepseek/deepseek-chat
WANLI_LLM_API_KEY=your-api-key-here
WANLI_LLM_BASE_URL=
WANLI_DATABASE_URL=sqlite:///./wanlideal.db
WANLI_DEBUG=true
```

如果需要调用真实大模型服务，请填写 `WANLI_LLM_API_KEY`。

#### 2. 启动后端

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 3. 启动前端

另开一个 PowerShell 窗口：

```powershell
cd frontend
npm install
npm run dev
```

访问：

```text
http://localhost:5173
```

## API 接口

### 健康检查

```http
GET /api/health
```

响应示例：

```json
{
  "status": "ok"
}
```

### 提交优惠攻略

```http
POST /api/deals/submit
```

请求示例：

```json
{
  "content": "商品原价 199，满减后 129，领取优惠券后下单。",
  "source": "manual",
  "source_name": "手动录入"
}
```

### 获取攻略列表

```http
GET /api/deals
```

可选参数：

```text
status=active
limit=50
offset=0
```

### 获取单个攻略

```http
GET /api/deals/{card_id}
```

## 测试

在项目根目录运行：

```powershell
pytest
```

如果使用虚拟环境：

```powershell
.\.venv\Scripts\Activate.ps1
pytest
```

## 前端开发命令

进入 `frontend` 目录后可使用：

```powershell
npm run dev
```

启动开发服务器。

```powershell
npm run build
```

构建生产版本。

```powershell
npm run preview
```

预览生产构建结果。

## 后端开发命令

启动后端开发服务：

```powershell
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

后端默认使用 SQLite 数据库：

```text
wanlideal.db
```

数据库会在服务启动时自动初始化。

## 注意事项

- 前端开发服务器默认运行在 `http://localhost:5173`
- 后端服务默认运行在 `http://localhost:8000`
- 前端接口请求使用 `/api`，由 Vite 代理到后端
- `.env` 文件包含本地配置和密钥，不建议提交到 Git
- 如果大模型 API Key 未配置，部分智能解析能力可能不可用

## 许可证

当前项目暂未声明许可证。
