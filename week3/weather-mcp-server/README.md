# Weather MCP Server

基于 OpenWeather API 的 MCP (Model Context Protocol) 服务器，支持 HTTP 传输和 Bearer Token 鉴权。

## 功能特性

- ✅ 支持 HTTP/SSE 传输协议
- ✅ Bearer Token 鉴权
- ✅ 三个天气相关工具：
  - `get_current_weather`: 获取当前天气
  - `get_weather_forecast`: 获取天气预报（5天）
  - `get_air_quality`: 获取空气质量指数
- ✅ 使用 UV 管理依赖
- ✅ Docker 容器化部署
- ✅ 完整的错误处理和日志记录

## 技术栈

- **Python 3.11+**
- **FastMCP**: MCP 服务器框架
- **httpx**: 异步 HTTP 客户端
- **uvicorn**: ASGI 服务器
- **loguru**: 日志管理
- **UV**: Python 包管理器

## 快速开始

### 前置要求

- Python 3.10+
- UV (Python 包管理器)
- Docker & Docker Compose (可选，用于容器部署)

### 安装 UV

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 本地运行

1. **克隆项目并进入目录**

```bash
cd week3/weather-mcp-server
```

2. **安装依赖**

```bash
uv venv
source .venv/bin/activate  # Linux/Mac
# 或
.venv\Scripts\activate  # Windows

uv pip install -e .
```

3. **配置环境变量**

复制 `.env.example` 为 `.env` 并修改配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
OPENWEATHER_API_KEY=58368b46948dd193e1c0e377651c2b06
MCP_AUTH_TOKEN=your-secret-token-here
HOST=0.0.0.0
PORT=8000
```

4. **启动服务**

```bash
python server.py
```

服务将在 `http://localhost:8000` 启动。

### Docker 部署

1. **构建并启动容器**

```bash
docker-compose up -d
```

2. **查看日志**

```bash
docker-compose logs -f
```

3. **停止服务**

```bash
docker-compose down
```

### 直接使用 Docker

```bash
# 构建镜像
docker build -t weather-mcp-server .

# 运行容器
docker run -d \
  -p 8000:8000 \
  -e OPENWEATHER_API_KEY=58368b46948dd193e1c0e377651c2b06 \
  -e MCP_AUTH_TOKEN=your-secret-token-here \
  -v $(pwd)/logs:/app/logs \
  --name weather-mcp \
  weather-mcp-server
```

## 在 Cursor/Claude Desktop 中配置

### Cursor 配置

在 Cursor 的 MCP 配置文件中添加：

```json
{
  "mcpServers": {
    "weather": {
      "url": "https://api.wersling.cn/mcp/weather",
      "headers": {
        "Authorization": "Bearer your-secret-token-here"
      }
    }
  }
}
```

如果是本地运行：

```json
{
  "mcpServers": {
    "weather": {
      "url": "http://localhost:8000",
      "headers": {
        "Authorization": "Bearer your-secret-token-here"
      }
    }
  }
}
```

### Claude Desktop 配置

编辑 `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac) 或 `%APPDATA%\Claude\claude_desktop_config.json` (Windows)：

```json
{
  "mcpServers": {
    "weather": {
      "command": "python",
      "args": ["/path/to/weather-mcp-server/server.py"],
      "env": {
        "OPENWEATHER_API_KEY": "58368b46948dd193e1c0e377651c2b06"
      }
    }
  }
}
```

## API 工具说明

### 1. get_current_weather

获取指定城市的当前天气信息。

**参数：**
- `city` (string, 必需): 城市名称（英文），如 "London", "Tokyo", "Beijing"
- `units` (string, 可选): 温度单位，默认 "metric"
  - `metric`: 摄氏度
  - `imperial`: 华氏度
  - `standard`: 开尔文

**示例：**

```python
# 在 AI 工具中使用
"查询北京的当前天气"
"What's the weather in London?"
```

**返回示例：**

```json
{
  "城市": "Beijing",
  "国家": "CN",
  "天气": "晴",
  "温度": "15.2°C",
  "体感温度": "13.8°C",
  "最低温度": "12.0°C",
  "最高温度": "18.0°C",
  "湿度": "45%",
  "气压": "1015 hPa",
  "风速": "3.5 m/s",
  "云量": "20%"
}
```

### 2. get_weather_forecast

获取指定城市的天气预报（未来5天，每3小时一个数据点）。

**参数：**
- `city` (string, 必需): 城市名称（英文）
- `days` (int, 可选): 预报天数，1-5天，默认5天
- `units` (string, 可选): 温度单位，默认 "metric"

**示例：**

```python
# 在 AI 工具中使用
"查询上海未来3天的天气预报"
"Get 5-day forecast for Tokyo"
```

**返回示例：**

```json
{
  "城市": "Shanghai",
  "国家": "CN",
  "预报": [
    {
      "时间": "2026-01-02 12:00:00",
      "天气": "多云",
      "温度": "16.5°C",
      "体感温度": "15.2°C",
      "湿度": "60%",
      "降水概率": "20%",
      "风速": "4.2 m/s"
    }
  ]
}
```

### 3. get_air_quality

获取指定城市的空气质量指数（AQI）。

**参数：**
- `city` (string, 必需): 城市名称（英文）

**示例：**

```python
# 在 AI 工具中使用
"查询深圳的空气质量"
"Check air quality in New York"
```

**返回示例：**

```json
{
  "城市": "Shenzhen",
  "坐标": {
    "纬度": 22.5455,
    "经度": 114.0683
  },
  "AQI等级": 2,
  "AQI描述": "良好",
  "污染物浓度 (μg/m³)": {
    "CO (一氧化碳)": 230.5,
    "NO (一氧化氮)": 0.2,
    "NO2 (二氧化氮)": 12.5,
    "O3 (臭氧)": 68.3,
    "SO2 (二氧化硫)": 5.2,
    "PM2.5": 15.3,
    "PM10": 25.8,
    "NH3 (氨气)": 1.2
  }
}
```

## 使用示例

### 在 Cursor 中使用

1. 配置好 MCP Server 后，重启 Cursor
2. 在对话中直接询问天气相关问题：

```
你：北京今天天气怎么样？
AI：[调用 get_current_weather 工具] 北京今天晴，温度15.2°C...

你：帮我查一下伦敦未来5天的天气预报
AI：[调用 get_weather_forecast 工具] 伦敦未来5天...

你：上海的空气质量如何？
AI：[调用 get_air_quality 工具] 上海空气质量良好，AQI等级2...
```

### 直接 HTTP 调用

```bash
# 获取当前天气
curl -X POST http://localhost:8000/tools/get_current_weather \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-secret-token-here" \
  -d '{"city": "Beijing", "units": "metric"}'

# 获取天气预报
curl -X POST http://localhost:8000/tools/get_weather_forecast \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-secret-token-here" \
  -d '{"city": "Tokyo", "days": 3, "units": "metric"}'

# 获取空气质量
curl -X POST http://localhost:8000/tools/get_air_quality \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-secret-token-here" \
  -d '{"city": "London"}'
```

## 错误处理

服务器实现了完整的错误处理：

- **超时处理**: API 请求超时自动重试
- **城市未找到**: 返回友好的错误提示
- **API 密钥错误**: 检测并提示 API 密钥问题
- **参数验证**: 验证输入参数的合法性
- **日志记录**: 所有请求和错误都记录到日志文件

## 日志

日志文件位于 `logs/weather_mcp.log`，包含：
- API 调用记录
- 错误信息
- 性能指标

日志配置：
- 自动轮转：文件大小超过 10MB
- 保留时间：7天

## 开发

### 运行测试

```bash
pytest
```

### 代码规范

- 4空格缩进
- 必要的中文注释
- 使用 loguru 进行日志记录

## 部署到生产环境

### 使用 Nginx 反向代理

```nginx
server {
    listen 80;
    server_name api.wersling.cn;

    location /mcp/weather {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### 使用 systemd 管理服务

创建 `/etc/systemd/system/weather-mcp.service`：

```ini
[Unit]
Description=Weather MCP Server
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/weather-mcp-server
Environment="PATH=/opt/weather-mcp-server/.venv/bin"
ExecStart=/opt/weather-mcp-server/.venv/bin/python server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable weather-mcp
sudo systemctl start weather-mcp
```

## 许可证

MIT License

## 作者

Sean Zou

## 贡献

欢迎提交 Issue 和 Pull Request！

