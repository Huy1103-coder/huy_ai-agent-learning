"""
tools.py - Agent 可调用的工具函数

所有工具都遵循以下契约:
1. 失败时返回 {"error": "..."},不抛异常
2. 字段名带单位后缀(_celsius, _kmh, _ugm3)
3. 内部辅助函数下划线开头(_get_coordinates)
"""

import os
import requests
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent.parent / ".env"
if not env_path.exists():
    raise FileNotFoundError(
        f"❌ .env 不存在!期望位置: {env_path}\n"
        f"当前文件: {__file__}"
    )
load_dotenv(env_path)

OPENWEATHER_KEY = os.getenv("OPENWEATHER_API_KEY")


# ============================================================
# 内部辅助函数(不对外暴露为工具)
# ============================================================

def _get_coordinates(city: str) -> tuple[float, float] | None:
    """城市名 → 经纬度;失败返回 None"""
    url = "http://api.openweathermap.org/geo/1.0/direct"
    params = {"q": city, "limit": 1, "appid": OPENWEATHER_KEY}
    try:
        response = requests.get(url, params=params, timeout=5)
        if response.status_code != 200:
            return None
        data = response.json()
        if not data:
            return None
        return data[0]["lat"], data[0]["lon"]
    except Exception:
        return None


# ============================================================
# 工具 1:天气查询
# ============================================================

def get_weather(city: str) -> dict:
    """查询城市当前天气"""
    if not OPENWEATHER_KEY:
        return {"error": "OPENWEATHER_API_KEY 未配置"}
    
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": OPENWEATHER_KEY,
        "units": "metric",
        "lang": "zh_cn",
    }
    
    try:
        response = requests.get(url, params=params, timeout=5)
        
        if response.status_code == 404:
            return {"error": f"找不到城市 '{city}',请检查拼写或换个名字"}
        if response.status_code == 401:
            return {"error": "API key 无效,请检查 OPENWEATHER_API_KEY"}
        if response.status_code == 429:
            return {"error": "API 请求过于频繁,请稍后再试"}
        if response.status_code != 200:
            return {"error": f"API 返回异常状态码 {response.status_code}"}
        
        data = response.json()
        wind_ms = data["wind"]["speed"]
        return {
            "city": data["name"],
            "temp_celsius": round(data["main"]["temp"], 1),
            "feels_like_celsius": round(data["main"]["feels_like"], 1),
            "humidity_percent": data["main"]["humidity"],
            "description": data["weather"][0]["description"],
            "wind_speed_ms": round(wind_ms, 2),
            "wind_speed_kmh": round(wind_ms * 3.6, 1),
        }
    
    except requests.exceptions.Timeout:
        return {"error": "请求超时(5 秒),网络可能不稳定"}
    except requests.exceptions.ConnectionError:
        return {"error": "无法连接到天气服务,请检查网络"}
    except KeyError as e:
        return {"error": f"API 返回格式异常,缺少字段 {e}"}
    except Exception as e:
        return {"error": f"未知错误: {type(e).__name__}: {e}"}


# ============================================================
# 工具 2:空气质量查询
# ============================================================

def get_aqi(city: str) -> dict:
    """查询城市当前空气质量"""
    if not OPENWEATHER_KEY:
        return {"error": "OPENWEATHER_API_KEY 未配置"}
    
    coords = _get_coordinates(city)
    if coords is None:
        return {"error": f"找不到城市 '{city}' 的坐标"}
    lat, lon = coords
    
    url = "http://api.openweathermap.org/data/2.5/air_pollution"
    params = {"lat": lat, "lon": lon, "appid": OPENWEATHER_KEY}
    
    try:
        response = requests.get(url, params=params, timeout=5)
        if response.status_code != 200:
            return {"error": f"AQI API 返回 {response.status_code}"}
        
        data = response.json()
        item = data["list"][0]
        aqi_level = item["main"]["aqi"]
        components = item["components"]
        
        aqi_labels = {1: "优", 2: "良", 3: "中等", 4: "差", 5: "很差"}
        
        return {
            "city": city,
            "aqi_level": aqi_level,
            "aqi_label": aqi_labels.get(aqi_level, "未知"),
            "pm2_5_ugm3": round(components["pm2_5"], 1),
            "pm10_ugm3": round(components["pm10"], 1),
            "co_ugm3": round(components["co"], 1),
            "no2_ugm3": round(components["no2"], 1),
        }
    
    except requests.exceptions.Timeout:
        return {"error": "AQI 请求超时"}
    except KeyError as e:
        return {"error": f"AQI 返回格式异常,缺字段 {e}"}
    except Exception as e:
        return {"error": f"未知错误: {type(e).__name__}: {e}"}


# ============================================================
# 工具路由表(给 main.py 用)
# ============================================================

TOOL_MAP = {
    "get_weather": get_weather,
    "get_aqi": get_aqi,
}