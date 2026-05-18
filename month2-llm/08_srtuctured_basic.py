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


def extract_with_prompt(text: str) -> str:
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {
                "role": "system",
                "content": """请从用户输入中提取产品信息,返回 JSON 格式,
包含字段:product(产品名)、price(价格,数字)、colors(颜色列表)。
只返回 JSON,不要其他文字。"""
            },
            {"role": "user", "content": text},
        ],
        temperature=0,
    )
    return response.choices[0].message.content

def extract_with_json_mode(text: str) -> str:
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {
                "role": "system",
                "content": """请从用户输入中提取产品信息,返回 JSON 格式,
包含字段:product(产品名)、price(价格,数字)、colors(颜色列表)。"""
            },
            {"role": "user", "content": text},
        ],
        temperature=0,
        response_format={"type": "json_object"},   # ← 关键!强制 JSON
    )
    return response.choices[0].message.content

test_text ="这件连衣裙现价 199元，目前有红色、黑色、白色三种颜色"

print("=" * 60)
print("方式1：纯 prompt 引导")
print("=" * 60)
result1 = extract_with_json_mode(test_text)
print("LLM原始输出：")
print(result1)
print()
try:
    data1 = json.loads(result1)
    print("✅ JSON 解析成功:", data1)
except json.JSONDecodeError as e:
    print(f"❌ JSON 解析失败:{e}")

print("\n" + "=" * 60)
print("方式 2:强制 JSON 模式")
print("=" * 60)
result2 = extract_with_json_mode(test_text)
print("LLM 原始输出:")
print(result2)
print()
try:
    data2 = json.loads(result2)
    print("✅ JSON 解析成功:", data2)
except json.JSONDecodeError as e:
    print(f"❌ JSON 解析失败:{e}")