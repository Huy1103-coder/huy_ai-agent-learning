"""
main.py - CSV 数据分析 Agent

运行方式:
    python main.py                              # 交互模式
    python main.py "分析 data/sales.csv"        # 单次模式
"""

import os
import sys
import json
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path


from tools import TOOL_MAP
from prompts import SYSTEM_PROMPT
from schemas import tools

env_path = Path(__file__).parent.parent.parent / ".env"

if not env_path.exists():
    raise FileExistsError(
        f"❌ .env 不存在!\n"
        f"   期望: {env_path}\n"
        f"   当前: {__file__}"
    )

load_dotenv(env_path)


client = OpenAI(
    api_key= os.getenv("DEEPSEEK_API_KEY"),
    base_url= "https://api.deepseek.com",
)

def run_agent(user_question:str,max_iterations:int = 10,verbose: bool = True) -> str:
    if verbose:
        print(f"\n{'=' * 60}")
        print(f"用户提问：{user_question}")
        print(f"{'='*60}")
    
    messages = [
              {"role":"system","content":SYSTEM_PROMPT},
              {"role":"user","content":user_question},
            ]
    for iteration in range(max_iterations):
        if verbose:
            print(f"\n--- 第 {iteration + 1} 轮 API 调用 ---")

        
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            tools=tools,
            tool_choice="auto",
        )

        message = response.choices[0].message
        messages.append(message)

        if not message.tool_calls:
            if verbose:
                print(f">>> 第 {iteration + 1} 轮:模型完成回答")
                print(f"\n>>> 最终回答:\n{message.content}")
            return message.content
        
        if verbose:
            print(f">>>模型选择调用 {len(message.tool_calls)} 个工具")

        
        for tc in message.tool_calls:
            tool_name = tc.function.name
            tool_agrs = json.loads(tc.function.arguments)

            if verbose:
                print(f"  - {tool_name}({tool_agrs})")
            
            result = TOOL_MAP[tool_name](**tool_agrs)

            if verbose:
                status = "❌" if "error" in result else "✅"

                if "error" in result:
                    print(f"   {status} {tool_name} 失败:{result['error']}")
                else:
                    print(f"   {status} {tool_name} 成功:(返回{len(result)}个字段)")
            
            messages.append({
                "role":"tool",
                "tool_call_id":tc.id,             
                "content":json.dumps(result,ensure_ascii=False),
                        })
    
    return f"⚠️ 达到最大迭代次数 ({max_iterations}),处理失败"

def main():
    """CLI 入口"""
    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
        run_agent(question)
        return
    
    print("=" * 60)
    print("📊 数据探长 Agent —— CSV 数据分析师")
    print("=" * 60)
    print("请输入你的问题(输入'q'退出)")

    while True:
        try:
            question = input("\n>>> ").strip()
            if question.low() == {'q','quit','exit'}:
               print("再见！")
               break
            if not question:
                continue
            run_agent(question)
        
        except KeyboardInterrupt:
            print("\n再见")
            break

    
if __name__ == "__main__":
    main()
     
    


                    