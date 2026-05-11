import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENWEATHER_API_KEY")

print(f"API Key前 8 位：{api_key[:8]}...")

url = "https://api.openweathermap.org/data/2.5/weather"
city = "Beijing"

param ={
    "q":city,
    "appid":api_key,
    "units":"metric",
    "lang":"zh_cn0"
}

response = requests.get(url,params=param)

print(f"状态码：{response.status_code}")

data = response.json()

print(f"完整响应:")
print(data)