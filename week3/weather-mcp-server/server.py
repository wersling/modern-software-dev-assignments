"""
Weather MCP Server - 基于OpenWeather API的MCP服务
支持HTTP传输和Bearer Token鉴权
"""
import os
from typing import Optional
import httpx
from fastmcp import FastMCP
from loguru import logger
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 配置日志
logger.remove()  # 移除默认handler
logger.add(
    "logs/weather_mcp.log",
    rotation="10 MB",
    retention="7 days",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
)
logger.add(lambda msg: None, level="ERROR")  # 避免stdout输出

# OpenWeather API配置
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "58368b46948dd193e1c0e377651c2b06")
OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5"

# 创建MCP服务器实例
mcp = FastMCP("Weather MCP Server")


async def call_openweather_api(endpoint: str, params: dict) -> dict:
    """
    调用OpenWeather API的通用方法
    
    Args:
        endpoint: API端点路径
        params: 查询参数
    
    Returns:
        API响应的JSON数据
    """
    params["appid"] = OPENWEATHER_API_KEY
    url = f"{OPENWEATHER_BASE_URL}/{endpoint}"
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            logger.info(f"成功调用OpenWeather API: {endpoint}")
            return data
    except httpx.TimeoutException:
        logger.error(f"API请求超时: {endpoint}")
        raise Exception("Weather API request timed out")
    except httpx.HTTPStatusError as e:
        logger.error(f"API返回错误状态码: {e.response.status_code}")
        if e.response.status_code == 404:
            raise Exception("City not found")
        elif e.response.status_code == 401:
            raise Exception("Invalid API key")
        else:
            raise Exception(f"Weather API error: {e.response.status_code}")
    except Exception as e:
        logger.error(f"API调用异常: {str(e)}")
        raise Exception(f"Failed to fetch weather data: {str(e)}")


@mcp.tool()
async def get_current_weather(city: str, units: str = "metric") -> str:
    """
    获取指定城市的当前天气信息
    
    Args:
        city: 城市名称（英文），例如: London, Tokyo, Beijing
        units: 温度单位，可选值: metric(摄氏度), imperial(华氏度), standard(开尔文)，默认为metric
    
    Returns:
        包含当前天气信息的JSON字符串
    """
    logger.info(f"获取城市天气: {city}, 单位: {units}")
    
    if not city or not city.strip():
        return "错误: 城市名称不能为空"
    
    if units not in ["metric", "imperial", "standard"]:
        return "错误: units参数必须是 metric, imperial 或 standard"
    
    try:
        params = {
            "q": city.strip(),
            "units": units,
            "lang": "zh_cn"  # 返回中文描述
        }
        data = await call_openweather_api("weather", params)
        
        # 格式化返回结果
        temp_unit = "°C" if units == "metric" else ("°F" if units == "imperial" else "K")
        result = {
            "城市": data["name"],
            "国家": data["sys"]["country"],
            "天气": data["weather"][0]["description"],
            "温度": f"{data['main']['temp']}{temp_unit}",
            "体感温度": f"{data['main']['feels_like']}{temp_unit}",
            "最低温度": f"{data['main']['temp_min']}{temp_unit}",
            "最高温度": f"{data['main']['temp_max']}{temp_unit}",
            "湿度": f"{data['main']['humidity']}%",
            "气压": f"{data['main']['pressure']} hPa",
            "风速": f"{data['wind']['speed']} m/s",
            "云量": f"{data['clouds']['all']}%"
        }
        
        import json
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        error_msg = f"获取天气失败: {str(e)}"
        logger.error(error_msg)
        return error_msg


@mcp.tool()
async def get_weather_forecast(city: str, days: int = 5, units: str = "metric") -> str:
    """
    获取指定城市的天气预报（未来5天，每3小时一个数据点）
    
    Args:
        city: 城市名称（英文），例如: London, Tokyo, Beijing
        days: 预报天数，1-5天，默认5天
        units: 温度单位，可选值: metric(摄氏度), imperial(华氏度), standard(开尔文)，默认为metric
    
    Returns:
        包含天气预报信息的JSON字符串
    """
    logger.info(f"获取城市天气预报: {city}, 天数: {days}, 单位: {units}")
    
    if not city or not city.strip():
        return "错误: 城市名称不能为空"
    
    if not 1 <= days <= 5:
        return "错误: 预报天数必须在1-5之间"
    
    if units not in ["metric", "imperial", "standard"]:
        return "错误: units参数必须是 metric, imperial 或 standard"
    
    try:
        params = {
            "q": city.strip(),
            "units": units,
            "lang": "zh_cn",
            "cnt": days * 8  # 每天8个数据点（每3小时）
        }
        data = await call_openweather_api("forecast", params)
        
        # 格式化返回结果
        temp_unit = "°C" if units == "metric" else ("°F" if units == "imperial" else "K")
        result = {
            "城市": data["city"]["name"],
            "国家": data["city"]["country"],
            "预报": []
        }
        
        for item in data["list"]:
            forecast_item = {
                "时间": item["dt_txt"],
                "天气": item["weather"][0]["description"],
                "温度": f"{item['main']['temp']}{temp_unit}",
                "体感温度": f"{item['main']['feels_like']}{temp_unit}",
                "湿度": f"{item['main']['humidity']}%",
                "降水概率": f"{item.get('pop', 0) * 100:.0f}%",
                "风速": f"{item['wind']['speed']} m/s"
            }
            result["预报"].append(forecast_item)
        
        import json
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        error_msg = f"获取天气预报失败: {str(e)}"
        logger.error(error_msg)
        return error_msg


@mcp.tool()
async def get_air_quality(city: str) -> str:
    """
    获取指定城市的空气质量指数（AQI）
    
    Args:
        city: 城市名称（英文），例如: London, Tokyo, Beijing
    
    Returns:
        包含空气质量信息的JSON字符串
    """
    logger.info(f"获取城市空气质量: {city}")
    
    if not city or not city.strip():
        return "错误: 城市名称不能为空"
    
    try:
        # 首先获取城市坐标
        params = {"q": city.strip()}
        weather_data = await call_openweather_api("weather", params)
        lat = weather_data["coord"]["lat"]
        lon = weather_data["coord"]["lon"]
        
        # 获取空气质量数据
        params = {"lat": lat, "lon": lon}
        data = await call_openweather_api("air_pollution", params)
        
        # AQI等级说明
        aqi_levels = {
            1: "优秀",
            2: "良好",
            3: "中等",
            4: "较差",
            5: "差"
        }
        
        aqi = data["list"][0]["main"]["aqi"]
        components = data["list"][0]["components"]
        
        result = {
            "城市": city,
            "坐标": {"纬度": lat, "经度": lon},
            "AQI等级": aqi,
            "AQI描述": aqi_levels.get(aqi, "未知"),
            "污染物浓度 (μg/m³)": {
                "CO (一氧化碳)": components.get("co", 0),
                "NO (一氧化氮)": components.get("no", 0),
                "NO2 (二氧化氮)": components.get("no2", 0),
                "O3 (臭氧)": components.get("o3", 0),
                "SO2 (二氧化硫)": components.get("so2", 0),
                "PM2.5": components.get("pm2_5", 0),
                "PM10": components.get("pm10", 0),
                "NH3 (氨气)": components.get("nh3", 0)
            }
        }
        
        import json
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        error_msg = f"获取空气质量失败: {str(e)}"
        logger.error(error_msg)
        return error_msg


if __name__ == "__main__":
    # 创建日志目录
    os.makedirs("logs", exist_ok=True)
    
    # 启动HTTP服务器
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    
    logger.info(f"启动Weather MCP Server: {host}:{port}")
    mcp.run(transport="sse", host=host, port=port)

