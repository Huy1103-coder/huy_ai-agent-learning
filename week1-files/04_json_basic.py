import json

data= {
    "name":"Alice",
    "age":30,
    "skills":["Python","AI"],
    "address":None
}

with open("user.json","w",encoding="utf-8") as f:
    json.dump(data,f,ensure_ascii=False,indent=2)

print("json已经生成")


with open("user.json","r",encoding="utf-8") as f:
    loaded = json.load(f)

print("读出来的内容是：")
print(loaded)
print(f"姓名是：{loaded['name']}")
print(f"第一个技能是：{loaded['skills'][0]}")
