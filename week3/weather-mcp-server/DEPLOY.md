# 部署指南

## 快速部署到服务器

### 方式一：Docker Compose（推荐）

1. **上传项目到服务器**

```bash
# 在本地打包
cd week3/weather-mcp-server
tar -czf weather-mcp-server.tar.gz .

# 上传到服务器
scp weather-mcp-server.tar.gz user@your-server:/opt/

# 在服务器上解压
ssh user@your-server
cd /opt
tar -xzf weather-mcp-server.tar.gz -C weather-mcp-server
cd weather-mcp-server
```

2. **配置环境变量**

```bash
# 编辑 .env 文件
nano .env

# 修改以下配置
OPENWEATHER_API_KEY=58368b46948dd193e1c0e377651c2b06
MCP_AUTH_TOKEN=your-production-secret-token
HOST=0.0.0.0
PORT=8000
```

3. **启动服务**

```bash
# 构建并启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 检查状态
docker-compose ps
```

4. **配置 Nginx 反向代理**

```bash
# 创建 Nginx 配置
sudo nano /etc/nginx/sites-available/weather-mcp
```

添加以下内容：

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
        
        # SSE 支持
        proxy_buffering off;
        proxy_cache off;
        proxy_read_timeout 86400;
    }
}
```

启用配置：

```bash
sudo ln -s /etc/nginx/sites-available/weather-mcp /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

5. **配置 SSL（可选但推荐）**

```bash
# 安装 Certbot
sudo apt install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d api.wersling.cn

# 自动续期
sudo certbot renew --dry-run
```

### 方式二：直接使用 Python

1. **安装依赖**

```bash
# 安装 UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# 创建虚拟环境
cd /opt/weather-mcp-server
uv venv
source .venv/bin/activate

# 安装依赖
uv pip install -e .
```

2. **配置 systemd 服务**

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
EnvironmentFile=/opt/weather-mcp-server/.env
ExecStart=/opt/weather-mcp-server/.venv/bin/python server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

3. **启动服务**

```bash
sudo systemctl daemon-reload
sudo systemctl enable weather-mcp
sudo systemctl start weather-mcp
sudo systemctl status weather-mcp
```

4. **查看日志**

```bash
# 查看 systemd 日志
sudo journalctl -u weather-mcp -f

# 查看应用日志
tail -f /opt/weather-mcp-server/logs/weather_mcp.log
```

## 测试部署

### 本地测试

```bash
# 测试服务是否正常
curl http://localhost:8000/health

# 测试天气API
curl -X POST http://localhost:8000/tools/get_current_weather \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-secret-token" \
  -d '{"city": "Beijing", "units": "metric"}'
```

### 远程测试

```bash
# 测试远程服务
curl https://api.wersling.cn/mcp/weather/health

# 测试天气API
curl -X POST https://api.wersling.cn/mcp/weather/tools/get_current_weather \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-secret-token" \
  -d '{"city": "Beijing", "units": "metric"}'
```

## 监控和维护

### 查看日志

```bash
# Docker 日志
docker-compose logs -f

# 应用日志
tail -f logs/weather_mcp.log

# Nginx 日志
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### 重启服务

```bash
# Docker
docker-compose restart

# Systemd
sudo systemctl restart weather-mcp
```

### 更新服务

```bash
# 拉取最新代码
git pull

# Docker 方式
docker-compose down
docker-compose build
docker-compose up -d

# Systemd 方式
sudo systemctl restart weather-mcp
```

### 备份

```bash
# 备份配置和日志
tar -czf weather-mcp-backup-$(date +%Y%m%d).tar.gz \
  .env \
  logs/ \
  docker-compose.yml
```

## 安全建议

1. **使用强密码**：确保 `MCP_AUTH_TOKEN` 是一个强随机字符串
2. **HTTPS**：生产环境必须使用 HTTPS
3. **防火墙**：只开放必要的端口（80, 443）
4. **定期更新**：定期更新系统和依赖包
5. **日志监控**：定期检查日志，发现异常及时处理

## 性能优化

1. **启用 Nginx 缓存**：对于不经常变化的数据可以启用缓存
2. **限流**：使用 Nginx 限制请求频率
3. **负载均衡**：高流量场景可以部署多个实例

## 故障排查

### 服务无法启动

```bash
# 检查端口占用
sudo netstat -tlnp | grep 8000

# 检查日志
docker-compose logs
sudo journalctl -u weather-mcp -n 50
```

### API 调用失败

```bash
# 检查 OpenWeather API Key
curl "https://api.openweathermap.org/data/2.5/weather?q=London&appid=YOUR_API_KEY"

# 检查网络连接
ping api.openweathermap.org
```

### 性能问题

```bash
# 查看资源使用
docker stats
top

# 查看日志大小
du -sh logs/
```

## 联系支持

如有问题，请查看：
- 项目 README.md
- GitHub Issues
- 日志文件

