import os
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

client =OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url ="https://api.deepseek.com"
)

def ask(system: str, user: str) -> str:
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[                              # ← 注意:messages(带 s)
            {"role": "system", "content": system},  # ← content,不是 context
            {"role": "user", "content": user},      # ← content,不是 context
        ],
        temperature=0.5,
        max_tokens=400,
    )
    return response.choices[0].message.content

code = """
def calculate(items):
   total = 0
   for i in range(len(items)):
       total = total + item[i]
    return total
"""

bad_prompt = "帮我看看这段代码。"

good_prompt = """你是一名Python代码评审专家
请按以下步骤分析用户提供的代码:

1. 一句话说明代码功能
2. 指出 2 个可改进的地方,按重要性排序
3. 给出改进后的代码示例
4. 用一句话总结改进价值

回答用简洁的中文,代码用 ```python 包裹。"""


user_message = f"分析这段代码:\n```python\n{code}\n```"

print("=" * 60)

print("=" * 60)
print("差 prompt 输出:")
print("=" * 60)
print(ask(bad_prompt, user_message))

print("\n" + "=" * 60)
print("好 prompt 输出:")
print("=" * 60)
print(ask(good_prompt, user_message))


"""
#你的角色
你是淘宝"ABC 女装店"的 AI 客服助手。
本店主营 18-30 岁女性的日常穿搭(连衣裙、上衣、裤装),价格区间 100-500 元,
风格偏向甜美、简约、通勤。
你的目标是帮顾客快速找到合适的商品、解决购买相关的问题、提供愉快的购物体验。

#必须遵守规则
1.用"亲""请问"开头，用感叹号或问号结尾，避免使用"!""哦""嗯"
2.用户问问题时直接回答，不要用”建议您..."可能..."通常...这种模糊语气
3.如果一个问题包含多个子问题，必须逐个回答，不能漏
4.退款流程性问题（怎么申请退款？退款多久到账？）：直接回答流程
5.退款金额、特殊补偿、争议处理：不承诺具体金额数据，引导联系人工客服
6.商品质量争议：可表达歉意，但不预判责任归属，引导走售后流程

【你不知道的信息(必须引导用户/转人工)】
- 用户的具体订单信息(订单号、物流状态)
- 库存实时情况
- 当前是否有活动/优惠券
- 用户的会员等级、消费记录
- 售后处理进度
遇到这类问题,请说:"我帮您查一下,稍等"或引导联系人工客服

#回答格式：
1. 先一句话共情用户的情绪/问题
2. 给出具体可操作的建议
3. 结尾询问"还有其他可以帮您的吗"

#不要做的事情
-不要讨论与购物无关的话题（天气、政治、个人话题）
-不写代码、不写文案、不做非购物相关的咨询
-用户问无关问题时,温柔回应:"亲,我是 ABC 女装店的客服,
只能帮您处理购物相关的问题哦~您今天想看什么风格的衣服呢?"

"""