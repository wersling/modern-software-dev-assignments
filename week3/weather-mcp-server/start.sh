#!/bin/bash

# Weather MCP Server 启动脚本

echo "🚀 启动 Weather MCP Server..."

# 检查是否在虚拟环境中
if [ -z "$VIRTUAL_ENV" ]; then
    echo "📦 激活虚拟环境..."
    if [ -d ".venv" ]; then
        source .venv/bin/activate
    else
        echo "❌ 虚拟环境不存在，请先运行: uv venv && source .venv/bin/activate && uv pip install -e ."
        exit 1
    fi
fi

# 检查 .env 文件
if [ ! -f ".env" ]; then
    echo "⚠️  .env 文件不存在，从 .env.example 复制..."
    cp .env.example .env
    echo "✅ 已创建 .env 文件，请根据需要修改配置"
fi

# 创建日志目录
mkdir -p logs

# 启动服务器
echo "✨ 服务器启动中..."
python server.py

