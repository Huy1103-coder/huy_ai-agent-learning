"""验证 LLM 的无状态:连续两次问会发现它'不记得'"""
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


def ask_once(question: str) -> str:
    """每次都独立调用,不传任何历史"""
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "user", "content": question}
        ],
        max_tokens=150,
    )
    return response.choices[0].message.content


# 第一轮:给模型一个"它本应记住"的信息
print("=" * 50)
print(">>> 第 1 轮提问")
print("=" * 50)
question1 = "我叫张明,我喜欢学 Python,这周末打算去爬山。请用一句话简单回应即可。"
print(f"用户:{question1}\n")
answer1 = ask_once(question1)
print(f"模型:{answer1}\n")

# 第二轮:测试它是否"记得"
print("=" * 50)
print(">>> 第 2 轮提问(独立调用,不传历史)")
print("=" * 50)
question2 = "我刚才告诉你我叫什么名字?爱好是什么?周末计划去哪?"
print(f"用户:{question2}\n")
answer2 = ask_once(question2)
print(f"模型:{answer2}\n")

print("=" * 50)
print("观察:第 2 轮模型应该说'不知道'或乱猜——")
print("       这就是 LLM 的'无状态'本质。")
print("=" * 50)