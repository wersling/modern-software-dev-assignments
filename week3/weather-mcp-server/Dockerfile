FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装uv
RUN pip install --no-cache-dir uv

# 复制项目文件
COPY pyproject.toml .
COPY server.py .

# 使用uv安装依赖
RUN uv pip install --system -r pyproject.toml

# 创建日志目录
RUN mkdir -p logs

# 暴露端口
EXPOSE 8000

# 设置环境变量
ENV HOST=0.0.0.0
ENV PORT=8000

# 启动服务
CMD ["python", "server.py"]

