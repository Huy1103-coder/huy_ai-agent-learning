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

class ConversationManager:

    def __init__(self,system_prompt:str,window_size:int =5):
        self.system = {"role":"system","content":system_prompt}
        self.window_size = window_size
        self.history=[]


    def add_user(self,content:str):
        self.history.append({"role":"user","content":content})


    def add_assistant(self,content:str):
        self.history.append({"role":"assistant","content":content})

    def get_message(self)->list:
         keep_count = self.window_size * 2
         recent = self.history[-keep_count:] if len(self.history) > keep_count else self.history

         return [self.system] + recent
    
    def chat_count(self) -> int:
        return len(self.history)
    

SYSTEM= "你是简洁的助手,回答不超过 30 字。"
USER_QUESTIONS =[
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

def run_with_window(window_size: int) ->dict:

    manager = ConversationManager(SYSTEM,window_size=window_size)
    total_input = 0
    total_output = 0

    for question in USER_QUESTIONS:
        manager.add_user(question)
        response = client.chat.completions.create(
            model = "deepseek-chat",
            messages = manager.get_message(),
            max_tokens=60,
            temperature=0,
        )

        answer = response.choices[0].message.content
        manager.add_assistant(answer)

        total_input += response.usage.prompt_tokens
        total_output += response.usage.completion_tokens

    
    return{
        "total_input":total_input,
        "total_output":total_output,
        "cost":total_input*0.5/1_000_000+total_output*2/1_000_000,
    }

print("=" * 60)
print("不同窗口大小的 token 与成本对比")
print("=" * 60)
print()

strategies= [
    (999, "无窗口(全保留所有历史)"),
    (5, "滚动窗口=5(保留最近 5 轮)"),
    (3, "滚动窗口=3(保留最近 3 轮)"),
]

results =[]
for size,name in strategies:
    print(f"测试：{name}")
    result = run_with_window(size)
    results.append((name,result))
    print(f"  总输入 token:{result['total_input']}")
    print(f"  总输出 token:{result['total_output']}")
    print(f"  总成本:¥{result['cost']:.6f}")
    print()



print("=" * 60)
print("📊 节省效果")
print("=" * 60)
baseline = results[0][1]["total_input"]
for name,result in results:
    saved_pct = (1 - result["total_input"] / baseline)*100
    print(f"  {name}:节省 {saved_pct:.1f}% 输入 token")




