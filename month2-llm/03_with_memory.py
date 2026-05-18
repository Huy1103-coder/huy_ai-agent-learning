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

conversation = [
    {"role": "system", "content": "你是一个友好的学习助手,回答要简洁,不超过 100 字。"},
]

def chat(user_input: str) -> str:
    # 把用户的新消息加进历史
    conversation.append({"role":"user","content":user_input})
    
    response = client.chat.completions.create(\
        model = "deepseek-chat",
        messages=conversation,
        )
    
    # 把模型的回答也加进历史
    answer = response.choices[0].message.content
    conversation.append({"role":"assistant","content":answer})

    print(f"[本次token：输入{response.usage.prompt_tokens}，输出{response.usage.completion_tokens}]")

    return answer

# 第一轮
print("=" * 50)
print(">>> 第 1 轮")
print("=" * 50)
print(f"用户:我叫张明,我喜欢学 Python,周末打算去爬山。")
print(f"模型:{chat('我叫张明,我喜欢学 Python,周末打算去爬山。')}\n")

# 第二轮 - 应该记得了
print("=" * 50)
print(">>> 第 2 轮(测试记忆)")
print("=" * 50)
print(f"用户:我刚才告诉你我叫什么名字?爱好是什么?")
print(f"模型:{chat('我刚才告诉你我叫什么名字?爱好是什么?')}\n")

# 第三轮 - 利用上下文做推荐
print("=" * 50)
print(">>> 第 3 轮(利用上下文给推荐)")
print("=" * 50)
print(f"用户:根据我的兴趣,给我推荐 3 本书。")
print(f"模型:{chat('根据我的兴趣,给我推荐 3 本书。')}\n")

# 第四轮 - 测试长程记忆
print("=" * 50)
print(">>> 第 4 轮(测试长程记忆)")
print("=" * 50)
print(f"用户:我周末打算去做什么来着?")
print(f"模型:{chat('我周末打算去做什么来着?')}\n")

# 看一下对话历史长成什么样
print("=" * 50)
print(f"对话历史共 {len(conversation)} 条消息:")
for i, msg in enumerate(conversation):
    role_zh = {"system": "[系统]", "user": "[用户]", "assistant": "[模型]"}[msg["role"]]
    content_preview = msg["content"][:30].replace("\n", " ")
    print(f"  {i}. {role_zh} {content_preview}...")