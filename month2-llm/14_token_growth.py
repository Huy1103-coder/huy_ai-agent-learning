import os
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent /".env"
load_dotenv(env_path)

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)

SYSTEM = "你是简洁的助手，回答不超过 30 字"
USER_QUESTIONS = [
    "什么是 Python?",
    "它适合做什么?",
    "怎么学最快?",
    "有什么推荐的资源?",
    "需要数学好吗?",
    "和 Java 比哪个更好?",
    "找工作好找吗?",
    "薪资水平如何?",
    "未来发展怎么样?",
    "我应该开始学吗?",
]

conversation = [{"role":"system","content":SYSTEM}]
records = []

for i,question in enumerate(USER_QUESTIONS,1):

    conversation.append({"role":"user","content":question})
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=conversation,
        max_tokens=80,
        temperature=0,
    )

    answer = response.choices[0].message.content
    conversation.append({"role":"assistant","content":answer})

    usage = response.usage
    records.append({
        "round":1,
        "history_msgs":len(conversation),
        "input_tokens":usage.prompt_tokens,
        "output_tokens":usage.completion_tokens, 
    })

    print(print(f"轮 {i:>2}:输入 {usage.prompt_tokens:>4} token | "
          f"输出 {usage.completion_tokens:>3} | "
          f"历史 {len(conversation):>2} 条消息"))
    
print("="* 60)
print(" token 成长分析")
print("="*60)

first_input= records[0]["input_tokens"]
last_input =records[-1]["input_tokens"]

total_input = sum(r["input_tokens"] for r in records)
total_output = sum(r["output_tokens"] for r in records)

print(f"\n第 1 轮输入:{first_input} token")
print(f"第 10 轮输入:{last_input} token")
print(f"输入增长倍数：{last_input/first_input:.1f}x")
print(f"\n10 轮总输入:{total_input} token")
print(f"10 轮总输出:{total_output} token")
print(f"10轮总成本：￥{total_input*0.5/1_000_000+total_output*2/1_000_000:.6f}")


print(f"\n📈 输入 token 增长趋势(每个 █ 代表 20 token):")
for r in records:
    bar = "█" * (r["input_tokens"] // 20)
    print(f"轮 {r['round']:>2}:{bar} {r['input_tokens']}")




