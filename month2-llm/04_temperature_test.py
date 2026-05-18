"""感受 temperature 对输出的影响"""
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


def ask(question: str, temperature: float) -> str:
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": question}],
        temperature=temperature,
        max_tokens=80,  # 限制长度,省 token
    )
    return response.choices[0].message.content


question = "用一句话描述秋天。"

# === 实验 1: temperature=0.0(最确定) ===
print("=" * 50)
print("temperature=0.0(最确定,三次输出应该几乎相同)")
print("=" * 50)
for i in range(3):
    print(f"\n第 {i+1} 次:")
    print(ask(question, temperature=0.0))

# === 实验 2: temperature=1.5(高随机) ===
print("\n" + "=" * 50)
print("temperature=1.5(高随机,三次输出会差异较大)")
print("=" * 50)
for i in range(3):
    print(f"\n第 {i+1} 次:")
    print(ask(question, temperature=1.5))