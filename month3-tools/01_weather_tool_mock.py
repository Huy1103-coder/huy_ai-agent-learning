import os
import json
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)



def get_weather(city:str) ->dict:

    mock_data = {
        "北京": {"temp": 12, "condition": "晴", "humidity": 45},
        "上海": {"temp": 18, "condition": "多云", "humidity": 70},
        "广州": {"temp": 24, "condition": "小雨", "humidity": 85},
    }
    return mock_data.get(city,{"error":f"没有{city}的数据"})

tools =[
  {
    "type":"function",
    "function":{
        "name":"get_weather",
       "description":"查询指定城市的相关信息",
       "parameters":{
           "type":"object",
           "properties":{
               "city":{
                   "type":"string",
                   "description":"城市名称，如 北京、上海",
               },
           },
           "required":["city"],
       },
    },
  },
]


user_question = "今天北京的天气怎么样？"

print("=" * 60)
print(f"用户提问: {user_question}")
print("=" * 60)

response = client.chat.completions.create(
    model = "deepseek-chat",
    messages=[{"role":"user","content":user_question}],
    tools = tools,
    tool_choice="auto",
)

message = response.choices[0].message

print("\n>>> 模型返回的 content (自然语言回复):")
print(repr(message.content))   # ← 用 repr 看清是 None 还是 "" 还是有内容

print("\n>>> 模型返回的 tool_calls (工具调用指令):")
if message.tool_calls:
    for call in message.tool_calls:
        print(f"工具名：{call.function.name}")
        print(f"参数(raw):{call.function.arguments}")
        print(f"参数(类型):{type(call.function.arguments)}")

else:
    print(message.content)

print("\n>>> 完整message对象:")
print(message)

# 验证 arguments 是字符串,需要 json.loads 解码
print("\n" + "=" * 60)
print("演示:把字符串 arguments 解码成字典")
print("=" * 60)

if message.tool_calls:
    raw_args= message.tool_calls[0].function.arguments
    print(f"解码前类型: {type(raw_args)}")
    print(f"解码前值: {raw_args}")

    args_dict = json.loads(message.tool_calls[0].function.arguments)
    print(f"解码后类型: {type(args_dict)}")
    print(f"解码后值: {args_dict}")
    print(f"提取 city: {args_dict['city']}")  # 现在能用字典语法了