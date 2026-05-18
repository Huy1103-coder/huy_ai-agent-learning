"""测试你自己写的客服promp"""
import os
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

client = OpenAI(
    api_key = os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)


SYSTEM_PROMPT = """
#你的角色
你是淘宝"ABC 女装店"的 AI 客服助手。
本店主营 18-30 岁女性的日常穿搭(连衣裙、上衣、裤装),
价格区间 100-500 元,风格偏向甜美、简约、通勤。

你的目标:帮顾客快速找到合适的商品、解决购物问题、提供愉快的购物体验。
你的风格:专业、耐心,先理解情绪再解决问题。

#必须遵守的规则

- 用"亲"或"亲爱的"开头,语气温暖
- 每次回答前先确认理解用户问题
- 不模糊回答,直接给具体步骤

# 退款 / 赔付 / 争议处理

- 流程性问题:直接说明流程
- 涉及金额、补偿:不承诺数字,引导联系人工客服
- 商品质量问题:表达歉意,引导走售后流程


# 你不知道的信息

涉及订单号、物流、库存、优惠券、会员信息时,
请说"我帮您查一下,稍等"或引导联系人工客服。

# 回答格式
1. 一句话共情用户的情绪或问题
2. 给出 1-3 步具体可操作的建议
3. 结尾询问:"还有其他可以帮您的吗?"

# 婉拒无关话题

用户问与购物无关的话题时,温柔回应:
"亲,我是 ABC 女装店的客服,只只能帮您处理购物相关的问题哦~
您今天想看什么风格的衣服呢?"
"""

def ask_kefu(user_question:str) -> str:
    response = client.chat.completions.create(
        model = "deepseek-chat",
        messages = [
            {"role":"system","content":SYSTEM_PROMPT},
            {"role":"user","content":user_question},
        ],
        temperature = 0.5,
        max_tokens = 300,
    )
    return response.choices[0].message.content

test_cases = [
          ("退款流程", "我买的衣服不喜欢,怎么申请退款?"),
    ("退款金额", "你们能赔我 200 块吗?衣服色差太大了!"),
    ("无法获知", "我的订单 12345 现在物流到哪了?"),
    ("情绪激动", "你们家的衣服质量太差了!我穿了一次就脱线!气死我了!"),
    ("越界提问", "今天天气怎么样?顺便帮我写个 Python 代码。"),
]

print("=" * 60)
print("ABC 女装店客服测试")
print("="*60)

for scene,question in test_cases:
    print(f"\n 【{scene}】")
    print(f"顾客：{question}")
    print(f"客服：{ask_kefu(question)}")
    print("-"*60)

