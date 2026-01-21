# Travel-Agent 智能旅行助手

基于 AI 的个性化旅行行程规划系统。

## 技术栈

| 端 | 技术 |
|---|------|
| 前端 | Vue3 + TypeScript + Vite + Ant Design Vue |
| 后端 | FastAPI + LangGraph + 高德地图 MCP |
| LLM | OpenAI 兼容 API |

## 快速启动

### 一键启动（推荐）

```bash
./start.sh
```

### 手动启动

**后端：**
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env 
# !! 编辑 .env 填入配置 !!
python -m app.api.main
```

**前端：**
```bash
cd frontend
npm install
npm run dev
```

访问：http://localhost:8000/docs（后端） | http://localhost:5173（前端）

## 目录结构

```
travel-agent/
├── backend/           # FastAPI 后端
│   ├── app/           # 应用代码
│   ├── requirements.txt
│   └── .env.example
├── frontend/          # Vue3 前端
│   ├── src/           # 源代码
│   ├── package.json
│   └── vite.config.ts
└── test/              # 集成测试
```

## 功能

- 输入目的地、日期、旅行偏好
- AI 自动生成每日行程规划
- 包含景点、餐饮、住宿、天气、预算信息
