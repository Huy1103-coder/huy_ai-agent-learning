import os
import logging
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENWEATHER_API_KEY")

# === 配置 logging ===
logging.basicConfig(
    level=logging.DEBUG,  # 设为 INFO 级别（看到 INFO 及以上的日志）
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler("weather.log", encoding="utf-8"),  # 写文件
        logging.StreamHandler()  # 同时输出到终端
    ]
)
logger = logging.getLogger(__name__)


def get_weather(city: str) -> dict | None:
    """查询一个城市的天气"""
    logger.info(f"开始查询天气: {city}")

    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": api_key,
        "units": "metric",
        "lang": "zh_cn"
    }

    try:
        response = requests.get(url, params=params, timeout=10)
    except requests.exceptions.Timeout:
        logger.error(f"请求超时: {city}")
        return None
    except requests.exceptions.ConnectionError:
        logger.error("网络连接失败")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"请求异常: {e}")
        return None

    logger.debug(f"HTTP 状态码: {response.status_code}")  # DEBUG 级，默认不显示

    if response.status_code == 401:
        logger.error("API Key 无效")
        return None
    elif response.status_code == 404:
        logger.warning(f"城市不存在: {city}")
        return None
    elif response.status_code != 200:
        logger.error(f"API 返回异常状态码: {response.status_code}")
        return None

    try:
        data = response.json()
        result = {
            "city": data["name"],
            "country": data["sys"]["country"],
            "temp": data["main"]["temp"],
            "feels_like": data["main"]["feels_like"],
            "humidity": data["main"]["humidity"],
            "description": data["weather"][0]["description"],
            "wind_speed": data["wind"]["speed"],
        }
        logger.info(f"查询成功: {result['city']}, {result['temp']}°C, {result['description']}")
        return result
    except (KeyError, IndexError) as e:
        logger.error(f"响应数据格式异常,缺少字段: {e}")
        return None


def display_weather(weather: dict) -> None:
    print("=" * 40)
    print(f"  {weather['city']}, {weather['country']} 当前天气")
    print("=" * 40)
    print(f"  天气状况  : {weather['description']}")
    print(f"  当前温度  : {weather['temp']}°C")
    print(f"  体感温度  : {weather['feels_like']}°C")
    print(f"  湿度      : {weather['humidity']}%")
    print(f"  风速      : {weather['wind_speed']} m/s")
    print("=" * 40)


if __name__ == "__main__":
    test_cities = ["Beijing", "Shenzhen", "FakeCityXYZ"]

    for city in test_cities:
        weather = get_weather(city)
        if weather:
            display_weather(weather)

    
    