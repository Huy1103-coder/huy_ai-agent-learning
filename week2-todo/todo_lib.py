import os
import json
from datetime import datetime
from pathlib import Path

DEFAULT_DATA_FILE = "todos.json"

def load_todos(data_file:str =DEFAULT_DATA_FILE) ->list[dict]:

    if not Path(data_file).exists():
        return []
    
    with open(data_file,"r",encoding="utf-8") as f:
        return json.load(f)
    

def save_todos(todos:list[dict],data_file:str = DEFAULT_DATA_FILE) ->None:
    with open(data_file,"w",encoding="utf-8") as f:
        json.dump(todos,f,ensure_ascii = False,indent = 2)


def get_next_id(todos: list[dict]) -> int:

    if not todos:
        return 1
    return max(t["id"] for t in todos) +1

def add_todo(todos:list[dict],title:str) -> dict:
    if not title.strip():
        raise ValueError("title 不能为空")
    new_todo={
        "id":get_next_id(todos),
        "title":title.strip(),
        "done":False,
        "created_at":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    todos.append(new_todo)
    return new_todo

def find_todo(todos:list[dict],todo_id:int) -> dict|None:
    for todo in todos:
        if todo["id"] == todo_id:
            return todo
    return None

def mark_done(todos:list[dict],todo_id:int) -> dict:
    todo = find_todo(todos,todo_id)
    if todo is None:
        raise ValueError(f"找不到 id={todo_id} 的todo")
    todo["done"] = True
    return todo

def mark_undone(todos:list[dict],todo_id:int) -> dict:
    todo = find_todo(todos,todo_id)
    if todo == None :
        raise ValueError(f"未找到 id={todo_id} 的 todo.")
    todo["done"] = False
    return todo


def delete_todo(todos:list[dict],todo_id:int) -> dict:
    todo = find_todo(todos,todo_id)
    if todo is None:
        raise ValueError(f"找不到 id={todo_id}的 todo")
    todos.remove(todo)
    return todo

def clear_done(todos:list[dict]) -> int:

    done_todos = [t for t in todos if t["done"]]
    for t in done_todos:
        todos.remove(t)
    return len(done_todos)

def stats(todos:list[dict]) ->dict:
    total = len(todos)
    done = sum(1 for t in todos if t["done"])
    return{
       "total":total,
       "done":done,
       "pending":total - done,

    }

