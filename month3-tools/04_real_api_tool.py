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
        return {
            "city": data["name"],
            "temp": round(data["main"]["temp"], 1),
            "feels_like": round(data["main"]["feels_like"], 1),
            "humidity": data["main"]["humidity"],
            "description": data["weather"][0]["description"],
            "wind_speed": data["wind"]["speed"],
        }
    
    except requests.exceptions.Timeout :
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
                 "description":"城市的英文名,如 Beijing、Shanghai、Tokyo、New York。中文城市名也支持,但英文名更准确。",  
               },
           },
           "required":["city"]
       },
        },
    }]

TOOL_MAP = {"get_weather":get_weather}

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
        "上海和广州哪个更适合周末出游?",
    ]
        
    

    for question in test_cases:
        run_agent(question)
        print("\n" + "-"* 60)