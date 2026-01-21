# Travel-Agent 后端服务

基于 FastAPI + LangGraph + 高德地图MCP 的 AI 旅行规划后端服务。

## 技术栈

| 技术 | 版本 | 用途 |
|-----|------|------|
| FastAPI | 0.128.x | Web 框架 |
| LangGraph | - | AI Agent 工作流 |
| LangChain OpenAI | 1.1.x | LLM 集成 |
| Pydantic | 2.12.x | 数据验证 |
| Uvicorn | 0.40.x | ASGI 服务器 |
| Pydantic Settings | 2.12.x | 配置管理 |
| 高德地图 MCP | - | 地图/天气/POI 服务 |

## 快速启动

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env  
# !! 编辑 .env 填入配置 !!
python -m app.api.main
```

访问 http://localhost:8000/docs 查看 API 文档。

## 项目结构

```
backend/
├── app/
│   ├── __init__.py
│   ├── config.py              # 配置管理（从 .env 读取）
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── langgraph.py       # LangGraph Agent 工作流
│   │   └── prompt.py          # Agent Prompt 模板
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py            # FastAPI 应用入口
│   │   └── routes/
│   │       ├── __init__.py
│   │       └── trip.py        # /api/trip/plan 路由
│   └── models/
│       ├── __init__.py
│       └── schemas.py         # Pydantic 数据模型
├── test/
│   ├── __init__.py
│   └── test_plan_trip.py      # 测试用例
├── requirements.txt           # Python 依赖
└── .env                       # 环境变量（需创建）
```

## API 端点

### 根路径

```
GET /
GET /health
```

### 旅行规划

```
POST /api/trip/plan
```

**请求参数** ([schemas.py](app/models/schemas.py)):

```json
{
  "city": "北京",
  "start_date": "2026-01-20",
  "end_date": "2026-01-22",
  "travel_days": 3,
  "transportation": "公共交通",
  "accommodation": "经济型",
  "preferences": ["历史文化", "美食"],
  "free_text_input": "希望多安排博物馆"
}
```

**响应格式**:

```json
{
  "success": true,
  "message": "旅行计划生成成功",
  "data": {
    "city": "北京",
    "start_date": "2026-01-20",
    "end_date": "2026-01-22",
    "days": [...],
    "weather_info": [...],
    "overall_suggestions": "...",
    "budget": {...}
  }
}
```

## 配置说明

在 `backend/.env` 文件中配置：

```env
# 必填配置
AMAP_MAPS_API_KEY=your_amap_api_key
LLM_MODEL_ID=you_openai_model_id
LLM_API_KEY=you_Openai_api_key
LLM_BASE_URL=you_openai_base_url

# 可选配置
LOG_LEVEL=INFO
```

## 开发历程

### 1. 项目初始化

**技术选型**: FastAPI + LangGraph + 高德地图 MCP

**原因**:
- FastAPI: 异步支持好，自动化 API 文档
- LangGraph: 可组合的 AI Agent 工作流
- 高德 MCP: 提供地图、POI、天气等工具

### 2. Agent 设计

使用 LangGraph 构建多阶段 Agent：

```
┌─────────────┐
│  旅行规划   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ 景点 Agent  │ ← 高德 POI 搜索
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ 天气 Agent  │ ← 高德天气 API
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ 酒店 Agent  │ ← 高德 POI 搜索
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  整合规划   │
└─────────────┘
```

### 3. 数据模型

使用 Pydantic 定义请求/响应模型：

| 模型 | 用途 |
|-----|------|
| TripRequest | 请求参数 |
| TripPlanResponse | 统一响应格式 |
| TripPlan | 行程数据结构 |
| DayPlan | 单日行程 |
| Attraction/Meal/Hotel | 详情数据 |

## 测试

```bash
# 运行后端测试
pytest test/ -v

# 集成测试（需要启动服务）
cd ..
python test/test_integration.py --backend
```

## 注意事项

1. **LLM 配置**: 需要配置 OpenAI 兼容的 API（支持 OpenAI、Azure、硅基流动等）
2. **高德 API Key**: 用于 POI 搜索和天气查询
3. **MCP 服务**: 使用 `amap-mcp-server` 提供地图相关工具
4. **请求超时**: 前端已配置 5 分钟超时，生成完整行程可能需要较长时间
