.PHONY: help install run test docker-build docker-up docker-down docker-logs clean verify

help:  ## 显示帮助信息
	@echo "Weather MCP Server - 可用命令："
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

verify:  ## 验证环境配置
	@./verify.sh

install:  ## 安装依赖（使用 UV）
	@echo "📦 安装依赖..."
	@uv venv
	@. .venv/bin/activate && uv pip install -e .
	@echo "✅ 依赖安装完成"

run:  ## 运行服务器
	@echo "🚀 启动 Weather MCP Server..."
	@python server.py

test:  ## 运行测试
	@echo "🧪 运行测试..."
	@python test_server.py

docker-build:  ## 构建 Docker 镜像
	@echo "🐳 构建 Docker 镜像..."
	@docker build -t weather-mcp-server .

docker-up:  ## 启动 Docker 容器
	@echo "🐳 启动 Docker 容器..."
	@docker-compose up -d
	@echo "✅ 容器已启动"
	@echo "📝 查看日志: make docker-logs"

docker-down:  ## 停止 Docker 容器
	@echo "🛑 停止 Docker 容器..."
	@docker-compose down

docker-logs:  ## 查看 Docker 日志
	@docker-compose logs -f

clean:  ## 清理临时文件
	@echo "🧹 清理临时文件..."
	@rm -rf __pycache__
	@rm -rf .pytest_cache
	@rm -rf *.egg-info
	@rm -rf .venv
	@rm -rf logs/*.log
	@echo "✅ 清理完成"

dev:  ## 开发模式（自动重启）
	@echo "🔧 开发模式启动..."
	@uvicorn server:mcp --reload --host 0.0.0.0 --port 8000

