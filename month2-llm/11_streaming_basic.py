import os
import time
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)

QUESTION = "用 150 字介绍一下 Python 的优势,适合初学者听。"

def non_streaming_chat():
    """非流式:等很久,然后一次性出现"""
    print("=" * 60)
    print("【非流式】用户看到 → 空白 → 等待 → 突然全部出现")
    print("=" * 60)
    
    start = time.time()
    
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": QUESTION}],
    )
    
    elapsed = time.time() - start
    print(response.choices[0].message.content)
    print(f"\n⏱ 总耗时:{elapsed:.2f} 秒")

def streaming_chat():
    print("\n" + "=" * 60)
    print("【流式】用户看到 → 立刻开始打字 → 逐字出现")
    print("="* 60)

    start = time.time()
    first_chunk_time = None

    stream = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role":"user","content":QUESTION}],
        stream = True,
    )
    for chunk in stream:
        delta = chunk.choices[0].delta
        if delta.content:
            if first_chunk_time is None:
                first_chunk_time = time.time() - start
            

            print(delta.content,end="",flush=True)

    total_time = time.time() - start
    print(f"\n\n⏱ 首字延迟:{first_chunk_time:.2f} 秒")
    print(f"⏱ 总耗时:{total_time:.2f} 秒")

if __name__ == "__main__":
    non_streaming_chat()
    streaming_chat()



