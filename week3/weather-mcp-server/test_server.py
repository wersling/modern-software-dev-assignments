"""
Weather MCP Server 测试脚本
"""
import asyncio
import httpx
import json


async def test_weather_api():
    """测试天气API功能"""
    base_url = "http://localhost:8000"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer your-secret-token-here"
    }
    
    print("🧪 开始测试 Weather MCP Server...\n")
    
    # 测试1: 获取当前天气
    print("1️⃣ 测试获取当前天气 (北京)")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/tools/get_current_weather",
                headers=headers,
                json={"city": "Beijing", "units": "metric"},
                timeout=30.0
            )
            print(f"状态码: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
                print("✅ 测试通过\n")
            else:
                print(f"❌ 测试失败: {response.text}\n")
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}\n")
    
    # 测试2: 获取天气预报
    print("2️⃣ 测试获取天气预报 (东京, 3天)")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/tools/get_weather_forecast",
                headers=headers,
                json={"city": "Tokyo", "days": 3, "units": "metric"},
                timeout=30.0
            )
            print(f"状态码: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"响应: {json.dumps(data, ensure_ascii=False, indent=2)[:500]}...")
                print("✅ 测试通过\n")
            else:
                print(f"❌ 测试失败: {response.text}\n")
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}\n")
    
    # 测试3: 获取空气质量
    print("3️⃣ 测试获取空气质量 (伦敦)")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/tools/get_air_quality",
                headers=headers,
                json={"city": "London"},
                timeout=30.0
            )
            print(f"状态码: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
                print("✅ 测试通过\n")
            else:
                print(f"❌ 测试失败: {response.text}\n")
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}\n")
    
    # 测试4: 错误处理 - 城市不存在
    print("4️⃣ 测试错误处理 (不存在的城市)")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/tools/get_current_weather",
                headers=headers,
                json={"city": "NonExistentCity123", "units": "metric"},
                timeout=30.0
            )
            print(f"状态码: {response.status_code}")
            data = response.json()
            print(f"响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
            print("✅ 错误处理正常\n")
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}\n")
    
    print("🎉 所有测试完成！")


if __name__ == "__main__":
    print("=" * 60)
    print("Weather MCP Server 测试")
    print("=" * 60)
    print("请确保服务器已启动: python server.py")
    print("=" * 60 + "\n")
    
    asyncio.run(test_weather_api())

