"""
单元 25: Tool Loop
完整两轮调用:模型 → 工具 → 模型 → 自然语言答案
"""
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


# ============================================================
# 1. 工具函数(和单元 24 一样)
# ============================================================

def get_weather(city: str) -> dict:
    """mock 天气查询"""
    mock_data = {
        "北京": {"temp": 12, "condition": "晴", "humidity": 45},
        "上海": {"temp": 18, "condition": "多云", "humidity": 70},
        "广州": {"temp": 24, "condition": "小雨", "humidity": 85},
    }
    return mock_data.get(city, {"error": f"没有 {city} 的数据"})


# ============================================================
# 2. 工具菜单(和单元 24 一样)
# ============================================================

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "查询指定城市的当前天气信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "城市名称,如 北京、上海",
                    },
                },
                "required": ["city"],
            },
        },
    },
]


# ============================================================
# 3. 工具名 → 真实函数的映射(路由表)
# ============================================================

# 模型告诉你"调 get_weather",你需要根据这个名字找到真正的 Python 函数
TOOL_MAP = {
    "get_weather": get_weather,
}


# ============================================================
# 4. 启动:维护 messages 列表(对话历史)
# ============================================================

user_question = "今天北京天气怎么样?"

messages = [
    {"role": "user", "content": user_question},
]

print("=" * 60)
print(f"用户提问: {user_question}")
print("=" * 60)


# ============================================================
# 5. 第 1 轮 API 调用:让模型决定调什么工具
# ============================================================

print("\n>>> 第 1 轮 API 调用(给模型问题 + 工具菜单)")

response_1 = client.chat.completions.create(
    model="deepseek-chat",
    messages=messages,
    tools=tools,
    tool_choice="auto",
)

message_1 = response_1.choices[0].message
print(f"  模型 content: {message_1.content!r}")
print(f"  模型 tool_calls: {message_1.tool_calls}")


# ============================================================
# 6. 关键:把模型的回复(指令)塞回 messages
# ============================================================

# ⚠️ 这一步极重要!模型下一轮要"看到"自己上一轮做了什么决定
messages.append(message_1)

print(f"\n>>> 当前 messages 长度: {len(messages)}")


# ============================================================
# 7. 执行模型要求的工具调用
# ============================================================

if message_1.tool_calls:
    for tool_call in message_1.tool_calls:
        # 取出工具名 + 参数(参数是 JSON 字符串,需要解码!)
        tool_name = tool_call.function.name
        tool_args = json.loads(tool_call.function.arguments)
        tool_call_id = tool_call.id   # 这是每次调用的唯一 ID,后面要用!
        
        print(f"\n>>> 执行工具: {tool_name}({tool_args})")
        print(f"    tool_call_id: {tool_call_id}")
        
        # 从映射表找到真正的 Python 函数,真的执行它
        real_function = TOOL_MAP[tool_name]
        result = real_function(**tool_args)   # 用 ** 解包传参
        
        print(f"    执行结果: {result}")
        
        # 把结果塞回 messages,用 role="tool" 这种新角色
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call_id,        # 对应到哪次调用
            "content": json.dumps(result, ensure_ascii=False),  # 结果转字符串
        })


# ============================================================
# 8. 第 2 轮 API 调用:把工具结果给模型,让它生成最终答案
# ============================================================

print(f"\n>>> 准备第 2 轮 API 调用,当前 messages:")
for i, msg in enumerate(messages):
    role = msg["role"] if isinstance(msg, dict) else msg.role
    print(f"  [{i}] role={role}")

print("\n>>> 第 2 轮 API 调用(无需再传 tools,只要把对话历史发过去)")

response_2 = client.chat.completions.create(
    model="deepseek-chat",
    messages=messages,
    # 注意:这一轮不传 tools 也可以,因为模型已经有结果了
    # 但传了也无妨,这里为了简洁不传
)

message_2 = response_2.choices[0].message
print(f"\n>>> 模型最终回答:")
print(f"  {message_2.content}")

print("\n" + "=" * 60)
print("✅ Agent 循环完成!")
print("=" * 60)