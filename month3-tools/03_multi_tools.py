"""
单元 26: 多工具自主选择
给 LLM 3 个工具(查天气、算数、查时间),让它根据用户问题自主选择。
"""
import os
import json
from datetime import datetime
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)

def get_weather(city: str) -> dict:
    """mock 天气查询"""
    mock_data = {
        "北京": {"temp": 12, "condition": "晴", "humidity": 45},
        "上海": {"temp": 18, "condition": "多云", "humidity": 70},
        "广州": {"temp": 24, "condition": "小雨", "humidity": 85},
    }
    return mock_data.get(city, {"error": f"没有 {city} 的数据"})


def calculator(expression: str) -> dict:
    """安全的简单计算器(不用 eval,避免代码注入)"""
    try:
        # 只允许数字和基本运算符
        allowed_chars = set("0123456789+-*/.() ")
        if not all(c in allowed_chars for c in expression):
            return {"error": "表达式包含不允许的字符"}
        result = eval(expression)   # 真实生产慎用,这里 mock 学习用
        return {"expression": expression, "result": result}
    except Exception as e:
        return {"error": f"计算失败: {e}"}


def get_current_time(timezone: str = "Asia/Shanghai") -> dict:
    """返回当前时间(简化版,只支持中国时区)"""
    now = datetime.now()
    return {
        "timezone": timezone,
        "datetime": now.strftime("%Y-%m-%d %H:%M:%S"),
        "weekday": ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][now.weekday()],
    }

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "查询指定城市的当前天气信息,包括温度、天气状况、湿度",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "城市名称,如 北京、上海、广州",
                    },
                },
                "required": ["city"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "执行简单的数学运算,支持加减乘除和括号",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "数学表达式,如 '3+5*2' 或 '(10-3)/2'",
                    },
                },
                "required": ["expression"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "获取当前的日期和时间,以及今天是周几",
            "parameters": {
                "type": "object",
                "properties": {
                    "timezone": {
                        "type": "string",
                        "description": "时区,默认 Asia/Shanghai",
                    },
                },
                "required": [],   # ← 注意:这里参数是可选的,required 为空
            },
        },
    },
]


TOOL_MAP = {
    "get_weather": get_weather,
    "calculator": calculator,
    "get_current_time": get_current_time,
}

def run_agent(user_question: str) -> str:
    """跑一次完整 Agent 循环,返回最终答案"""
    print(f"\n{'=' * 60}")
    print(f"用户提问: {user_question}")
    print(f"{'=' * 60}")
    
    messages = [{"role": "user", "content": user_question}]
    
    # 第 1 轮
    response_1 = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        tools=tools,
        tool_choice="auto",
    )
    message_1 = response_1.choices[0].message
    messages.append(message_1)
    
    # 看模型选了什么
    if message_1.tool_calls:
        print(f"\n>>> 模型选择调用 {len(message_1.tool_calls)} 个工具:")
        for tc in message_1.tool_calls:
            print(f"    - {tc.function.name}({tc.function.arguments})")
        
        # 执行所有 tool_calls
        for tool_call in message_1.tool_calls:
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)
            
            real_function = TOOL_MAP[tool_name]
            result = real_function(**tool_args)
            print(f"\n>>> {tool_name} 执行结果: {result}")
            
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result, ensure_ascii=False),
            })
        
        # 第 2 轮
        response_2 = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
        )
        final = response_2.choices[0].message.content
    else:
        # 模型没调工具,直接拿 content
        print(f"\n>>> 模型未调用工具,直接回答")
        final = message_1.content
    
    print(f"\n>>> 最终回答:\n{final}")
    return final


if __name__ == "__main__":
    test_cases = [
        "今天北京天气怎么样?",                # 场景 A: 单一工具(天气)
        "100 乘以 23 等于多少?",              # 场景 B: 单一工具(计算)
        "现在几点了?",                        # 场景 C: 单一工具(时间)
        "你是谁?能做什么?",                   # 场景 D: 不用工具(直接答)
        "今天上海天气怎么样,顺便算一下 27 度的华氏度",   # 场景 E: 多工具组合
    ]
    
    for question in test_cases:
        run_agent(question)
        print("\n" + "─" * 60)