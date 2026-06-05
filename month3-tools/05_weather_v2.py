import os
import json
import requests
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)

OPENWEATHER_KEY = os.getenv("OPENWEATHER_API_KEY")

def _get_coortdinates(city:str) -> tuple[float,float] | None:
    url = "http://api.openweathermap.org/geo/1.0/direct"
    params = {"q":city,"limit":1,"appid":OPENWEATHER_KEY}
    try:
        response = requests.get(url,params=params,timeout=5)
        if response.status_code != 200:
            return None
        data = response.json()
        if not data:
            return
        return data[0]['lat'],data[0]["lon"]
    except Exception:
        return None

def get_aqi(city: str) -> dict:
    if not OPENWEATHER_KEY:
        return {"error":"OPENWEATHER_API_KEY 未配置"}
    coords = _get_coortdinates(city)
    if coords is None:
        return {"error":f"找不到城市’{city}'的坐标"}
    lat, lon = coords

    url = "http://api.openweathermap.org/data/2.5/air_pollution"
    params = {"lat":lat,"lon":lon,"appid": OPENWEATHER_KEY}

    try:
        response = requests.get(url, params=params, timeout=5)
        if response.status_code != 200:
            return {"error": f"AQI API 返回 {response.status_code}"}
        
        data = response.json()
        item = data["list"][0]
        aqi_level = item["main"]["aqi"]
        components = item["components"]
        
        # AQI 等级翻译表(查官方文档抄过来的)
        aqi_labels = {
            1: "优",
            2: "良",
            3: "中等",
            4: "差",
            5: "很差",
        }
        
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

def get_weather(city:str)  ->dict:

    if not OPENWEATHER_KEY:
        return {"error":"OPENWEATHER_API_KEY 未配置,请检查 .env"}
    
    url = "https://api.openweathermap.org/data/2.5/weather"
    params ={
        "q":city,
        "appid":OPENWEATHER_KEY,
        "units":"metric",
        "lang":"zh_cn",
    }

    try:
        response = requests.get(url,params=params,timeout= 5)

        if response.status_code == 404:
            return {"error": f"找不到城市 '{city}',请检查拼写或换个名字"}
        
        if response.status_code == 401:
            return {"error":f"API Key 无效，请检查OPENWEATHER_API_KEY"}

        if response.status_code == 429:
            return {"error":f"API请求过于频繁，请稍后再试"}
        
        if response.status_code != 200:
            return {"error":f"API 返回异常状态码 {response.status_code}"}
         
        data = response.json()
        wind_ms =data['wind']["speed"]
        return {
            "city": data["name"],
            "temp_celsius": round(data["main"]["temp"], 1),
            "feels_like_celsius": round(data["main"]["feels_like"], 1),
            "humidity_percent": data["main"]["humidity"],
            "description": data["weather"][0]["description"],
            "wind_speed_ms":round(wind_ms,2),
            "wind_speed_kmh":round(wind_ms * 3.6,1),
        }
    
    except requests.exceptions.Timeout:
        return {"error":"请求超时（5秒），网络可能不稳定"}
    
    except requests.exceptions.ConnectionError:
        return {"error":"无法链接到天气服务，请检查网络"}
    
    except KeyError as e:
        return {"error":f"API 返回格式异常，缺少字段{e}"}
    
    except Exception as e:
        return {"error":f"未知错误：{type(e).__name__}:{e}"}
    
tools =[{
        "type":"function",
        "function":{
       "name":"get_weather",
       "description": "查询全球任意城市的实时天气,包括温度、体感温度、湿度、天气描述和风速。仅返回当前天气,不支持预报。",
       "parameters":{
           "type":"object",
           "properties":{
               "city":{
                 "type":"string",
                 "description":(
    "查询全球任意城市的实时天气。返回字段:"
    "temp_celsius(摄氏度),feels_like_celsius(体感摄氏度),"
    "humidity_percent(湿度百分比),description(天气描述),"
    "wind_speed_ms(风速 m/s),wind_speed_kmh(风速 km/h)。"
    "仅返回当前天气,不支持预报。"
),  
               },
           },
           "required":["city"]
       },
        },
    },
    {
        "type":"function",
        "function":{
            "name":"get_aqi",
            "description":(
                "查询城市当前空气质量。返回字段："
                "aqi_level(1-5,数字越大越差)，aqi_label(中文等级：优/良/中等/差/很差),"
                "pm2_5_ugm3(PM2.5 浓度 μg/m³,大于 75 视为不健康)，"
                "pm10_ugm3(PM10 浓度 μg/m³),"
                "co_ugm3(一氧化碳),no2_ugm3(二氧化氮)。"
                  "用于判断是否适合户外活动。"
            ),
            "parameters":{
                "type":"object",
                "properties":{
                    "city":{
                       "type":"string",
                       "description":"城市的英文名,如 Beijing、Tokyo",
                    },
                },
                "required":["city"],
            },
        },
    },
    ]

TOOL_MAP = {
            "get_weather":get_weather,
            "get_aqi":get_aqi,
        }

def run_agent(user_question:str) -> str:
    print(f"\n{'='*60}")
    print(f"用户提问: {user_question}")
    print(f"{'=' * 60}")

    messages = [{"role": "user", "content": user_question}]

    response_1 = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        tools = tools,
        tool_choice = "auto",
    )

    message_1 = response_1.choices[0].message
    messages.append(message_1)

    if message_1.tool_calls:
        for tool_call in message_1.tool_calls:
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)
            
            print(f"\n>>> 调用工具: {tool_name}({tool_args})")

            result  = TOOL_MAP[tool_name](**tool_args)

            if "error" in result:
                print(f">>> ❌ 工具失败: {result['error']}")
            else:
                print(f">>> ✅ 工具成功: {result}")
            
            messages.append({
                "role":"tool",
                "tool_call_id":tool_call.id,
                "content":json.dumps(result,ensure_ascii=False),  
            })
        
        response_2 = client.chat.completions.create(
            model = "deepseek-chat",
            messages= messages,
        )
        final = response_2.choices[0].message.content
    else:
        final = message_1.content
    
    print(f"\n>>> 最终回答:\n{final}")
    return final

if __name__ == "__main__":
    test_cases =[
        "今天北京天气怎么样?",                  
        "今天 Tokyo 天气怎么样?",               
        "今天奥德赛星球天气怎么样?",            
        "广州现在的 PM2.5 是多少?",
    ]
        
    

    for question in test_cases:
        run_agent(question)
        print("\n" + "-"* 60)