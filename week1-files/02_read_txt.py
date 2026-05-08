with open("hello.txt","r",encoding ="utf-8") as f:
    content = f.read()
    print("=======一次读全部======")
    print(content)


with open("hello.txt","r",encoding="utf-8") as f:
    print("===按行读===")
    for line_number,line in enumerate(f,start=1):
        print(f"第{line_number}行：{line.strip()}")