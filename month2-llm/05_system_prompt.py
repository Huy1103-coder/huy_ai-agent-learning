import os
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

client = OpenAI(
    api_key = os.getenv("DEEPSEEK_API_KEY"),
    base_url = "https://api.deepseek.com",
)


def ask_with_system(system:str,user:str)  -> str:

    response = client.chat.completions.create(
        model = "deepseek-chat",
        messages = [
            {"role":"system","content":system},
            {"role":"user","content":user},
        ],
        temperature=0.7,
        max_tokens=200,
    )

    return response.choices[0].message.content

question = "我的猫这两天不爱吃东西，该怎么办？"

systems = [
    {
        "name": "1️⃣ 严谨兽医",
        "prompt": "你是一名 10 年经验的执业兽医。你回答必须严谨、基于事实,优先建议就医检查,不能给出诊断性结论。回答不超过 100 字。",
    },
    {
        "name": "2️⃣ 热情邻居大妈",
        "prompt": "你是一位热情爱聊天的邻居大妈,养过很多猫。说话亲切随意,爱用感叹号,会主动分享经验和小窍门。",
    },
    {
        "name": "3️⃣ 简洁助手",
        "prompt": "你必须只用 3 个 bullet point 回答,每条不超过 15 字。不要其他多余内容。",
    },
]


print("=" * 60)
print(f"问题：{question}")
print("="*60)

for s in systems:
    print(f"\n{s['name']}的回答：")
    print("-"*60)
    print(ask_with_system(s['prompt'],question))

