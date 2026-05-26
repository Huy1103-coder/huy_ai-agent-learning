"""
main.py - 户外活动顾问 Agent 主程序

运行方式:
    python main.py                    # 交互式 CLI
    python main.py "北京天气怎么样?"  # 直接传入问题
"""

import os
import sys
import json
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path

# 项目内部模块
from tools import TOOL_MAP
from prompts import SYSTEM_PROMPT
from schemas import tools

env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)


def run_agent(user_question: str, max_iterations: int = 10, verbose: bool = True) -> str:
    """
    N 轮循环 Agent
    
    Args:
        user_question: 用户输入的问题
        max_iterations: 最大循环次数(防爆)
        verbose: 是否打印过程日志
    
    Returns:
        最终自然语言回答
    """
    if verbose:
        print(f"\n{'=' * 60}")
        print(f"用户提问: {user_question}")
        print(f"{'=' * 60}")
    
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_question},
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
            print(f">>> 模型选择调用 {len(message.tool_calls)} 个工具")
        
        for tc in message.tool_calls:
            tool_name = tc.function.name
            tool_args = json.loads(tc.function.arguments)
            
            if verbose:
                print(f"   - {tool_name}({tool_args})")
            
            result = TOOL_MAP[tool_name](**tool_args)
            
            if verbose:
                status = "❌" if "error" in result else "✅"
                print(f"   {status} {tool_name} 返回: {result}")
            
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": json.dumps(result, ensure_ascii=False),
            })
    
    return f"⚠️ 达到最大迭代次数 ({max_iterations}),处理失败"


def main():
    """CLI 入口"""
    # 模式 1:命令行参数传问题
    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
        run_agent(question)
        return
    
    # 模式 2:交互式
    print("=" * 60)
    print("🌤️  户外通 Agent —— 专业户外活动顾问")
    print("=" * 60)
    print("输入你的问题(输入 'q' 退出):")
    
    while True:
        try:
            question = input("\n>>> ").strip()
            if question.lower() in {"q", "quit", "exit"}:
                print("再见!")
                break
            if not question:
                continue
            run_agent(question)
        except KeyboardInterrupt:
            print("\n再见!")
            break


if __name__ == "__main__":
    main()