import os 
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv("../.env")

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)

response = client.chat.completions.create(
    model="deepseek-chat",  # DeepSeek 的对话模型
    messages=[
        {"role": "user", "content": "请问中国的领土面积多大"}
    ],
)



answer = response.choices[0].message.content
print("=" * 50)
print("模型回答：")
print(answer)
print("="*50)
stop_reason = response.choices[0].finish_reason
print("停止的原因：")
print(stop_reason)
print("="*50)
usage = response.usage
print(f"输入 token: {usage.prompt_tokens}")
print(f"输出 token: {usage.completion_tokens}")
print(f"总计 token: {usage.total_tokens}")



