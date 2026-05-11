import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENWEATHER_API_KEY")

def get_weather(city:str) -> dict | None:
    """
    查询一个城市的天气
    成功返回字典；失败返回 None 并打印错误原因
    """
    url = "https://api.openweathermap.org/data/2.5/weather"

    params = {
      "q":city,
      "appid":api_key,
      "units":"metric",
      "lang":"zh_cn"
    }


    try:
        response = requests.get(url,params=params)
    except requests.exceptions.Timeout:
        print(f"❌ 请求超时（10 秒）")
        return None
    except  requests.exceptions.ConnectionError:
        print(f"❌ 网络连接失败，请检查网络")
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求失败: {e}")
        return None
    
    if response.status_code == 401:
        print(f"❌ API Key 无效（状态码 401）")
        return None
    elif response.status_code == 404:
        print(f"❌ 找不到城市 '{city}'（状态码 404）")
        return None
    elif response.status_code != 200:
        print(f"❌ API 返回异常状态码: {response.status_code}")
        return None
    
    try:
        data = response.json()
        return {
            "city": data["name"],
            "country": data["sys"]["country"],
            "temp": data["main"]["temp"],
            "feels_like": data["main"]["feels_like"],
            "humidity": data["main"]["humidity"],
            "description": data["weather"][0]["description"],
            "wind_speed": data["wind"]["speed"],
        }
    except (KeyError,IndexError) as e:
        print(f"❌ 响应数据格式异常,缺少字段: {e}")
        return None
    

def display_weather(weather: dict) -> None:
    """漂亮地打印天气信息"""
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
    test_cities =[
       "Beijing",
       "Shenzhen",
       "FakeCityXYZ",
    ]

    for city in test_cities:
        print(f"\n>>> 查询{city}")
        weather = get_weather(city)
        if weather:
            display_weather(weather)
        else:
            print("(查询失败，跳过)")