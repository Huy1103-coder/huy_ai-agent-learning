with open("log.txt","w",encoding="utf-8") as f:
    f.write("第一次写入\n")

with open("log.txt","a",encoding="utf-8") as f:
    f.write("第二次追加\n")
    f.write("第三次追加\n")

with open("log.txt","r",encoding="utf-8") as f:
    print(f.read())