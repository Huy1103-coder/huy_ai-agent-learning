from fastapi import FastAPI

app = FastAPI(title ="我的第一个API")

@app.get("/")
def read_root():
    return {"message":"Hello,FastAPI!"}

@app.get("/hello/{name}")
def say_hello(name:str):

    return {"message":f"你好，{name}"}


