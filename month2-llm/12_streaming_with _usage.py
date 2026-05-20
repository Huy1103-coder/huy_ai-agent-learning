"""流式 + Token 用量统计"""
import os
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)


# 关键:加 stream_options 参数
stream = client.chat.completions.create(
    model="deepseek-chat",
    messages=[{"role": "user", "content": "用 100 字介绍 Python"}],
    stream=True,
    stream_options={"include_usage": True},   # ← 让最后一个 chunk 包含 usage 信息
)

full_text = ""
usage_info = None

for chunk in stream:
    # 中间 chunk:正常拿 content
    if chunk.choices and chunk.choices[0].delta.content:
        text = chunk.choices[0].delta.content
        full_text += text
        print(text, end="", flush=True)
    
    # 最后一个 chunk:包含 usage 信息
    if chunk.usage:
        usage_info = chunk.usage

print("\n\n" + "=" * 50)
print("📊 Token 用量:")
print(f"  输入 token: {usage_info.prompt_tokens}")
print(f"  输出 token: {usage_info.completion_tokens}")
print(f"  总计 token: {usage_info.total_tokens}")
print(f"📝 完整回答长度:{len(full_text)} 字")