#!/bin/bash

# Weather MCP Server 环境验证脚本

echo "🔍 Weather MCP Server 环境验证"
echo "================================"
echo ""

# 检查 Python 版本
echo "1️⃣ 检查 Python 版本..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "✅ $PYTHON_VERSION"
else
    echo "❌ Python 3 未安装"
    exit 1
fi

# 检查 UV
echo ""
echo "2️⃣ 检查 UV 包管理器..."
if command -v uv &> /dev/null; then
    UV_VERSION=$(uv --version)
    echo "✅ $UV_VERSION"
else
    echo "⚠️  UV 未安装，可以通过以下命令安装："
    echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
fi

# 检查 Docker
echo ""
echo "3️⃣ 检查 Docker..."
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version)
    echo "✅ $DOCKER_VERSION"
else
    echo "⚠️  Docker 未安装（可选，用于容器部署）"
fi

# 检查 Docker Compose
echo ""
echo "4️⃣ 检查 Docker Compose..."
if command -v docker-compose &> /dev/null; then
    COMPOSE_VERSION=$(docker-compose --version)
    echo "✅ $COMPOSE_VERSION"
else
    echo "⚠️  Docker Compose 未安装（可选，用于容器部署）"
fi

# 检查项目文件
echo ""
echo "5️⃣ 检查项目文件..."
FILES=("server.py" "pyproject.toml" "Dockerfile" "docker-compose.yml" "README.md")
for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file 缺失"
    fi
done

# 检查 .env 文件
echo ""
echo "6️⃣ 检查环境配置..."
if [ -f ".env" ]; then
    echo "✅ .env 文件存在"
    
    # 检查关键配置
    if grep -q "OPENWEATHER_API_KEY" .env; then
        echo "✅ OPENWEATHER_API_KEY 已配置"
    else
        echo "⚠️  OPENWEATHER_API_KEY 未配置"
    fi
    
    if grep -q "MCP_AUTH_TOKEN" .env; then
        echo "✅ MCP_AUTH_TOKEN 已配置"
    else
        echo "⚠️  MCP_AUTH_TOKEN 未配置"
    fi
else
    echo "⚠️  .env 文件不存在，将从 .env.example 复制"
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✅ 已创建 .env 文件"
    fi
fi

# 测试 OpenWeather API
echo ""
echo "7️⃣ 测试 OpenWeather API 连接..."
if [ -f ".env" ]; then
    source .env
    if [ -n "$OPENWEATHER_API_KEY" ]; then
        RESPONSE=$(curl -s "https://api.openweathermap.org/data/2.5/weather?q=London&appid=$OPENWEATHER_API_KEY")
        if echo "$RESPONSE" | grep -q "London"; then
            echo "✅ OpenWeather API 连接正常"
        else
            echo "❌ OpenWeather API 连接失败"
            echo "   响应: $RESPONSE"
        fi
    else
        echo "⚠️  OPENWEATHER_API_KEY 未设置"
    fi
else
    echo "⚠️  无法测试，.env 文件不存在"
fi

echo ""
echo "================================"
echo "✨ 验证完成！"
echo ""
echo "下一步："
echo "1. 如果使用本地运行："
echo "   ./start.sh"
echo ""
echo "2. 如果使用 Docker："
echo "   docker-compose up -d"
echo ""
echo "3. 测试服务："
echo "   python test_server.py"

