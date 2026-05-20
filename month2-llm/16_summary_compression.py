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

SUMMARIZE_PROMPT = """你是对话摘要助手。请把下面这段对话压缩成一段话(不超过 100 字),
保留:
1. 用户的关键信息(姓名、需求、决策)
2. 已经讨论过的主要话题
3. 重要的结论或承诺

省略:
1. 寒暄
2. 详细解释的内容
3. 重复信息

只输出摘要,不要其他文字。"""

def summarize_history(messages: list) -> str:
    """让 LLM 总结一段对话历史"""
    history_text = "\n".join(
        f"{m['role']}: {m['content']}" for m in messages if m['role'] != 'system'
    )
    
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": SUMMARIZE_PROMPT},
            {"role": "user", "content": history_text},
        ],
        max_tokens=200,
        temperature=0.3,
    )
    return response.choices[0].message.content

class SmartConversationManager:
    """带"滚动窗口 + 摘要压缩"的对话管理器"""
    def __init__(
        self,
        system_prompt: str,
        window_size: int = 3,          # 窗口大小
        summarize_threshold: int = 6,   # 历史超过几轮就压缩
    ):
        self.system = {"role": "system", "content": system_prompt}
        self.window_size = window_size
        self.summarize_threshold = summarize_threshold
        self.history = []           # 最近的对话(未压缩)
        self.summary = ""           # 累积的摘要
    
    def add_user(self, content: str):
        self.history.append({"role": "user", "content": content})
    
    def add_assistant(self, content: str):
        self.history.append({"role": "assistant", "content": content})
        
        # 检查是否需要压缩
        rounds = len(self.history) // 2
        if rounds > self.summarize_threshold:
            self._compress()
    
    def _compress(self):
        """把早期对话压缩成摘要,只保留最近 window_size 轮"""
        keep_count = self.window_size * 2
        
        to_summarize = self.history[:-keep_count]
        recent = self.history[-keep_count:]

        if self.summary:
            combined = (
                f"已有摘要:{self.summary}\n\n"
                f"新对话:\n" +
                "\n".join(f"{m['role']}: {m['content']}" for m in to_summarize)
            )
            self.summary = summarize_history(
                [{"role": "user", "content": combined}]
            )
        else:
            self.summary = summarize_history(to_summarize)

        self.history = recent
        
        print(f"  [📦 触发摘要压缩,摘要长度:{len(self.summary)} 字]")
    
    def get_messages(self) -> list:
        """组装发给 LLM 的 messages"""
        messages = [self.system]

        if self.summary:
            messages.append({
                "role": "system",
                "content": f"以下是之前的对话摘要:{self.summary}",
            })
        

        messages.extend(self.history)
        return messages


SYSTEM = "你是简洁的助手,回答不超过 30 字。"
USER_QUESTIONS = [
    "我叫张明,准备学 Python",
    "建议从哪里开始?",
    "需要学多久?",
    "推荐书或课程?",
    "学完能找什么工作?",
    "薪资大概多少?",
    "我刚才说叫什么名字?",       
    "我学的是什么语言?",
    "你刚才推荐了什么资源?",
    "我应该开始了吗?",
]


def run_with_smart_manager() -> dict:
    """测试摘要压缩版"""
    manager = SmartConversationManager(
        SYSTEM,
        window_size=3,
        summarize_threshold=5,
    )
    total_input = 0
    total_output = 0
    
    print("=" * 60)
    print("智能管理器(滚动窗口 + 摘要压缩)")
    print("=" * 60)
    
    for i, question in enumerate(USER_QUESTIONS, 1):
        manager.add_user(question)
        
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=manager.get_messages(),
            max_tokens=60,
            temperature=0,
        )
        
        answer = response.choices[0].message.content
        manager.add_assistant(answer)
        
        total_input += response.usage.prompt_tokens
        total_output += response.usage.completion_tokens
        
        print(f"\n轮 {i}:{question}")
        print(f"  模型:{answer}")
        print(f"  本轮 token:输入 {response.usage.prompt_tokens}, 输出 {response.usage.completion_tokens}")
    
    return {
        "total_input": total_input,
        "total_output": total_output,
        "summary": manager.summary,
    }


if __name__ == "__main__":
    result = run_with_smart_manager()
    
    print("\n" + "=" * 60)
    print("📊 总结")
    print("=" * 60)
    print(f"总输入 token:{result['total_input']}")
    print(f"总输出 token:{result['total_output']}")
    print(f"\n最终累积摘要:\n{result['summary']}")