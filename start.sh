#!/bin/bash

# CampusFlow 启动脚本
# 同时启动后端 API 和前端 Gradio

echo "🚀 CampusFlow 智慧校园系统启动脚本"
echo "================================"

# 检查 Python 环境
if ! command -v python &> /dev/null; then
    echo "❌ 错误：未找到 Python"
    exit 1
fi

# 检查虚拟环境
if [ ! -d ".venv" ]; then
    echo "⚠️  未找到虚拟环境，请先创建："
    echo "   python -m venv .venv"
    exit 1
fi

# 激活虚拟环境
echo "📦 激活虚拟环境..."
source .venv/bin/activate

# 检查依赖
echo "📋 检查依赖..."
python -c "import gradio, fastapi, langchain" 2>/dev/null || {
    echo "⚠️  依赖未安装，正在安装..."
    pip install -r requirements.txt -q
}

# 启动后端 API（后台）
echo ""
echo "🔧 启动后端 API 服务 (port: 8000)..."
python api/main.py > api.log 2>&1 &
API_PID=$!
echo "   API PID: $API_PID"

# 等待后端启动
echo "⏳ 等待后端服务启动..."
sleep 3

# 检查后端是否启动成功
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "   ✅ 后端服务启动成功"
else
    echo "   ⚠️  后端服务可能未完全启动，继续等待..."
    sleep 3
fi

# 启动前端 Gradio
echo ""
echo "🎨 启动前端 Gradio (port: 7860)..."
echo ""
echo "================================"
echo "✅ 系统启动成功！"
echo ""
echo "📱 访问地址："
echo "   前端界面: http://localhost:7860"
echo "   API 文档: http://localhost:8000/docs"
echo "   API 健康: http://localhost:8000/health"
echo ""
echo "🛑 停止服务："
echo "   Ctrl+C 或 kill $API_PID"
echo "================================"
echo ""

# 启动前端（前台）
python app_full.py

# 前端关闭后，关闭后端
echo ""
echo "🛑 正在关闭后端服务..."
kill $API_PID 2>/dev/null
echo "✅ 已清理"
