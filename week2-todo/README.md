# Todo CLI

一个用 Python 写的命令行待办事项管理工具,作为 AI Agent 学习路线第 2 周的第一个项目。

## 功能

- ✅ 添加、删除、列出 todo
- ✅ 标记完成 / 未完成
- ✅ 清除所有已完成
- ✅ 进度统计
- ✅ JSON 文件持久化
- ✅ 19 个 pytest 单元测试覆盖

## 安装

```bash
cd week2-todo
# 不需要额外依赖,只用 Python 标准库
```

## 使用

```bash
# 添加
python todo_cli.py add "学完第 2 周"
python todo_cli.py add "推到 GitHub"

# 列出所有
python todo_cli.py list

# 标记完成
python todo_cli.py done 1

# 标记未完成
python todo_cli.py undone 1

# 删除
python todo_cli.py delete 2

# 清除所有已完成
python todo_cli.py clear

# 查看统计
python todo_cli.py stats

# 查看帮助
python todo_cli.py --help
python todo_cli.py add --help
```

## 项目结构

```text
week2-todo/
├── todo_lib.py        # 核心逻辑库(纯函数,可测试)
├── todo_cli.py        # 命令行入口(argparse 解析)
├── test_todo_lib.py   # pytest 测试套件
└── todos.json         # 数据文件(运行时自动生成)
```

## 设计原则

- **库代码与界面代码分离**:todo_lib 处理逻辑,todo_cli 处理交互
- **纯函数优先**:核心逻辑不碰文件 IO,便于测试
- **异常通过抛出而非打印**:让上层决定如何展示错误
- **依赖注入**:文件路径作为参数,测试时用临时路径

## 测试

```bash
python -m pytest test_todo_lib.py -v
```

应该看到 19 个用例全部通过。

## 学习要点

第 2 周通过这个项目实践了:
- argparse 命令行参数解析(主 parser + 子命令)
- pytest fixture 和 tmp_path 减少测试重复
- 三层测试覆盖:正常 / 边界 / 异常
- 字符串不可变性与"边界净化"原则
- CLI 输出格式化与用户体验