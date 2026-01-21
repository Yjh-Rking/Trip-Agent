#!/bin/bash

# Travel-Agent 一键启动脚本

set -e

# 颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "🚀 Travel-Agent 启动脚本"
echo ""

# 解析参数
AMAP_API_KEY="${1:-}"
LLM_MODEL_ID="${2:-}"
LLM_API_KEY="${3:-}"
LLM_BASE_URL="${4:-}"

# 交互式输入
if [ -z "$AMAP_API_KEY" ] || [ -z "$LLM_MODEL_ID" ] || [ -z "$LLM_API_KEY" ] || [ -z "$LLM_BASE_URL" ]; then
  echo -e "${YELLOW}请输入配置信息:${NC}"
  echo ""
  [ -z "$AMAP_API_KEY" ] && read -p "高德地图 API Key: " AMAP_API_KEY
  [ -z "$LLM_MODEL_ID" ] && read -p "LLM Model ID: " LLM_MODEL_ID
  [ -z "$LLM_API_KEY" ] && read -p "LLM API Key: " LLM_API_KEY
  [ -z "$LLM_BASE_URL" ] && read -p "LLM Base URL: " LLM_BASE_URL
fi

# 验证
if [ -z "$AMAP_API_KEY" ] || [ -z "$LLM_MODEL_ID" ] || [ -z "$LLM_API_KEY" ] || [ -z "$LLM_BASE_URL" ]; then
  echo -e "${RED}错误: 4个参数都是必填的${NC}"
  exit 1
fi

echo ""

# 脚本目录
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# 创建 .env
echo "📝 创建配置文件..."
cp backend/.env.example backend/.env

# 修改配置值
sed -i "s/AMAP_API_KEY=\"YOU-AMAP-API-KEY-HERE\"/AMAP_API_KEY=\"$AMAP_API_KEY\"/" backend/.env
sed -i "s/LLM_MODEL_ID=\"YOU_OPENAI_MODEL_ID\"/LLM_MODEL_ID=\"$LLM_MODEL_ID\"/" backend/.env
sed -i "s/LLM_API_KEY=\"YOU_OPENAI_API_KEY\"/LLM_API_KEY=\"$LLM_API_KEY\"/" backend/.env
sed -i "s|L_LM_BASE_URL=\"YOU_OPENAI_BASE_URL\"|LLM_BASE_URL=\"$LLM_BASE_URL\"|" backend/.env
echo -e "${GREEN}✓ 配置文件已生成${NC}"

# 日志文件
BACKEND_LOG="$SCRIPT_DIR/logs/backend.log"
FRONTEND_LOG="$SCRIPT_DIR/logs/frontend.log"
mkdir -p "$SCRIPT_DIR/logs"

# 安装后端依赖
echo ""
echo "📦 安装后端依赖..."
cd "$SCRIPT_DIR/backend"
pip install -r requirements.txt -q 2>/dev/null || pip install -r requirements.txt
echo -e "${GREEN}✓ 后端依赖安装完成${NC}"

# 启动后端
echo ""
echo "🚀 启动后端服务..."
uvicorn app.api.main:app --host 0.0.0.0 --port 8000 > "$BACKEND_LOG" 2>&1 &
BACKEND_PID=$!
echo -e "${GREEN}✓ 后端已启动 (PID: $BACKEND_PID)${NC}"
echo "  日志: $BACKEND_LOG"

# 安装前端依赖
echo ""
echo "📦 安装前端依赖..."
cd "$SCRIPT_DIR/frontend"
npm install 2>/dev/null || npm install
echo -e "${GREEN}✓ 前端依赖安装完成${NC}"

# 启动前端
echo ""
echo "🚀 启动前端服务..."
npm run dev > "$FRONTEND_LOG" 2>&1 &
FRONTEND_PID=$!
echo -e "${GREEN}✓ 前端已启动 (PID: $FRONTEND_PID)${NC}"
echo "  日志: $FRONTEND_LOG"

echo ""
echo "========================================"
echo -e "${GREEN}🎉 启动成功！${NC}"
echo ""
echo "  后端: http://localhost:8000/docs (PID: $BACKEND_PID)"
echo "  前端: http://localhost:5173 (PID: $FRONTEND_PID)"
echo ""
echo "  后端日志: tail -f $BACKEND_LOG"
echo "  前端日志: tail -f $FRONTEND_LOG"
echo ""
echo "按 Ctrl+C 停止所有服务"
echo "========================================"

# 等待
wait $BACKEND_PID $FRONTEND_PID
