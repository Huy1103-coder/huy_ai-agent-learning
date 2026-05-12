import argparse
import sys
from todo_lib import (
    load_todos,
    save_todos,
    add_todo,
    mark_done,
    mark_undone,
    delete_todo,
    clear_done,
    stats,
) 

def format_todo(todo: dict) -> str:
    """把一个 todo 字典格式化成单行字符串"""
    status = status = "✓" if todo["done"] else "○"
    return f"[{status}]{todo['id']:>3}. {todo['title']}"


def print_todos(todos: list[dict]) -> None:

    if not todos:
        print("  (没有 todo, 用 add 命令添加一个吧)")
        return
    
    print("="*50)
    print(f"  你的待办事项（共{len(todos)}条）")
    print("="*50)

    pending = [t for t in todos if not t["done"]]
    done = [t for t in todos if t["done"]]

    if pending:
        print("\n 已完成：")
        for todo in pending:
            print(format_todo(todo))


    if done:
        print("\n 已完成")
        for todo in done:
            print(format_todo(todo))

    print("=" * 50)


def cmd_add(args) -> None:
    """处理 add 命令"""
    todos = load_todos()
    try:
        new_todo = add_todo(todos, args.title)
    except ValueError as e:
        print(f"❌ 添加失败: {e}")
        sys.exit(1)
    
    save_todos(todos)
    print(f"✅ 已添加: #{new_todo['id']} {new_todo['title']}")

def cmd_list(args) ->None:
    """处理 list 命令"""
    todos = load_todos()
    print_todos(todos)


def cmd_done(args) ->None:
    """处理 done 命令"""
    todos = load_todos()
    try:
        todo = mark_done(todos,args.todo_id)
    except ValueError as e:
        print(f"❌ 操作失败: {e}")
        sys.exit(1)

    save_todos(todos)
    print(f"✅ 已标记完成: #{todo['id']} {todo['title']}")

def cmd_undone(args) -> None:
    """处理 undone 命令"""
    todos = load_todos()
    try:
        todo = mark_undone(todos,args.todo_id)
    except ValueError as e:
        print(f"❌ 操作失败: {e}")
        sys.exit(1)

    save_todos(todos)
    print(f"✅ 已标记未完成: #{todo['id']} {todo['title']}")



def cmd_delete(args)  -> None:
    """处理 delete 命令"""
    todos = load_todos()
    try:
        todo  = delete_todo(todos,args.todo_id)
    except ValueError as e:
        print(f"❌ 删除失败: {e}")
        sys.exit(1)

    save_todos(todos)

def cmd_clear(args) -> None:
    """处理 clear 命令"""
    todos = load_todos()
    count = clear_done(todos)
    save_todos(todos)

    if count == 0:
        print("  没有已完成的 todo 需要清除")
    else:
        print(f"✅ 已清除 {count} 条已完成的 todo")

def cmd_stats(args) ->None:

    todos = load_todos()
    result = stats(todos)

    print("="*30)
    print(f"  待办事项统计")
    print("=" * 30)
    print(f"  总数      : {result['total']}")
    print(f"  已完成    : {result['done']}")
    print(f"  未完成    : {result['pending']}")

    if result["total"] >0:
        progress = result["done"] / result["total"] * 100
        bar_length = 20
        filled = int(bar_length * result["done"] / result["total"])
        bar =  "█" * filled + "░" * (bar_length - filled)
        print(f"  完成进度 ：[{bar}] {progress:.0f}%")
    print("=" * 30)

def main():
    parser = argparse.ArgumentParser(
        prog = "todo",
        description="一个简单的命令行 todo 工具",
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    
    add_p = subparsers.add_parser("add", help="添加一个 todo")
    add_p.add_argument("title", help="todo 的内容")
    add_p.set_defaults(func=cmd_add)

    list_p = subparsers.add_parser("list", help="列出所有 todo")
    list_p.set_defaults(func=cmd_list)

    done_p = subparsers.add_parser("done",help="标记某个todo 为完成")
    done_p.add_argument("todo_id",type = int,help = "要标记的 todo id")
    done_p.set_defaults(func=cmd_done)


    undone_p = subparsers.add_parser("undone",help = "标记某个 todo 为未完成")
    undone_p.add_argument("todo_id",type=int,help="要标记的todo id")
    undone_p.set_defaults(func = cmd_undone)

    del_p = subparsers.add_parser("delete", help="删除某个 todo")
    del_p.add_argument("todo_id", type=int, help="要删除的 todo id")
    del_p.set_defaults(func=cmd_delete)

    clear_p = subparsers.add_parser("clear", help="清除所有已完成的 todo")
    clear_p.set_defaults(func=cmd_clear)

    stats_p = subparsers.add_parser("stats", help="显示统计信息")
    stats_p.set_defaults(func=cmd_stats)

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    
    args.func(args)

if __name__ == "__main__":
     main()
    



    

