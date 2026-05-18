"""演示:无状态模型也能"假装"有记忆——只要你伪造历史"""
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


# 关键:伪造一段"从未发生过"的对话历史
fake_history = [
    {"role": "user", "content": "我叫李雷,是个程序员,我有只猫叫小白。"},
    {"role": "assistant", "content": "好的李雷,我记住了你和小白。"},
    {"role": "user", "content": "我今年 28 岁,住在杭州。"},
    {"role": "assistant", "content": "好的,28 岁,杭州。"},
]

# 现在问模型"它知道什么"
fake_history.append({"role": "user", "content": "你了解我什么?请详细列举。"})

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=fake_history,
)

print("模型回答:")
print(response.choices[0].message.content)