import json

tools = [
    {"name": "Cursor",  "purpose": "AI 增强代码编辑器", "free": True},
    {"name": "Claude",  "purpose": "对话和写代码",       "free": False},
    {"name": "Ollama",  "purpose": "本地跑大模型",       "free": True},
]

# 写入 tools.json（文件名要和内容对应）
with open("tools.json", "w", encoding="utf-8") as f:
    json.dump(tools, f, ensure_ascii=False, indent=2)
print("tools.json 写入成功")

# 读出
with open("tools.json", "r", encoding="utf-8") as f:
    loaded_tools = json.load(f)

# 直接遍历元素，更 Pythonic
for tool in loaded_tools:
    free_str = "免费" if tool['free'] else "付费"
   
    print(f"{tool['name']} ({free_str}): {tool['purpose']}")