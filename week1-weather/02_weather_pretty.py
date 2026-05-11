import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENWEATHER_API_KEY")

city="shenzhen"
url = "https://api.openweathermap.org/data/2.5/weather"
param = {
    "q":city,
    "appid":api_key,
    "units":"metric",
    "lang":"zh_cn"
}

response = requests.get(url,params=param)
data = response.json()

city_name = data["name"]
country = data["sys"]["country"]
temp = data["main"]["temp"]
feels_like = data["main"]["feels_like"]
humdity = data["main"]["humidity"]
description = data["weather"][0]["description"]
wind_speed = data["wind"]["speed"] 

print("="*40)
print(f"{city_name},{country}当前天气")
print("="*40)
print(f" 天气状况 ：{description}")
print(f" 当前温度 ：{temp} C")
print(f" 体感温度 ：{feels_like} C")
print(f" 湿度 ：{humdity}%")
print(f" 风速 ：{wind_speed} m/s")
print("="*40)