"""天气查询库 - 把功能拆成可独立测试的小函数"""
import os
import logging
import requests
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


def parse_weather_data(data: dict) -> dict:
    """
    从 API 返回的原始 JSON 中提取关键字段
    这是个纯函数：相同输入永远得到相同输出，不依赖网络
    """
    return {
        "city": data["name"],
        "country": data["sys"]["country"],
        "temp": data["main"]["temp"],
        "feels_like": data["main"]["feels_like"],
        "humidity": data["main"]["humidity"],
        "description": data["weather"][0]["description"],
        "wind_speed": data["wind"]["speed"],
    }


def is_comfortable(weather: dict) -> bool:
    """
    判断天气是否舒适
    舒适条件: 温度 18-26°C 且 湿度 30%-70%
    """
    temp_ok = 18 <= weather["temp"] <= 26
    humidity_ok = 30 <= weather["humidity"] <= 70
    return temp_ok and humidity_ok


def temp_category(temp: float) -> str:
    """根据温度返回分类标签"""
    if temp < 0:
        return "严寒"
    elif temp < 10:
        return "寒冷"
    elif temp < 20:
        return "凉爽"
    elif temp < 28:
        return "舒适"
    else:
        return "炎热"


def fetch_weather(city: str, api_key: str) -> dict | None:
    """
    调用 OpenWeatherMap API 获取天气
    """
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": api_key, "units": "metric", "lang": "zh_cn"}

    try:
        response = requests.get(url, params=params, timeout=10)
    except requests.exceptions.RequestException as e:
        logger.error(f"请求失败: {e}")
        return None

    if response.status_code != 200:
        logger.warning(f"API 返回 {response.status_code}: {city}")
        return None

    try:
        return parse_weather_data(response.json())
    except (KeyError, IndexError) as e:
        logger.error(f"解析数据失败: {e}")
        return None


