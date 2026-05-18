# AI Agent Learning Journey

> 我的 AI Agent 应用开发学习记录，从零基础到能上线 Agent 应用。

## 📅 学习计划

跟着自己制定的《8 个月修正版学习计划》（v3 综合 GPT 与第三方评审两轮迭代），每月一个核心能力，一个可演示项目。

| 月份 | 主题 | 状态 |
|---|---|---|
| 第 1 个月 | Python 小项目 + API 基础 | ✅ 已完成 |
| 第 2 个月 | LLM 应用开发 + Transformer 概念 | 🚧 进行中 |
| 第 3 个月 | Tool Calling + 初级 Agent | ⏳ |
| 第 4 个月 | RAG 与知识库 | ⏳ |
| 第 5 个月 | 单 Agent 框架 | ⏳ |
| 第 6 个月 | 多 Agent + 前端 | ⏳ |
| 第 7 个月 | 工程化部署 MVP | ⏳ |
| 第 8 个月 | 作品集打磨 / 进阶 | ⏳ |

## 📂 项目结构

```text
ai-learning/
├── week1-files/            # 第 1 周练习
├── week1-weather/          # 第 1 周项目:天气查询
├── week2-todo/             # 第 2 周项目 1:Todo CLI
├── week2-fastapi/          # 第 2 周项目 2:FastAPI Web 服务
├── month2-llm/             # 第 2 个月项目:LLM 应用开发 ⭐ NEW
│   ├── 01-04_*.py              # API 基础 + 多轮对话
│   ├── 05-07_*.py              # Prompt 工程实战
│   ├── 08-09_*.py              # 结构化输出基础
│   └── 10_resume_extractor.py  # AI 简历提取器(作品级)
└── hello.py
```

## 🛠 技术栈

- **语言**：Python 3.11
- **环境管理**：Miniconda
- **HTTP 调用**:`requests`
- **环境变量**:`python-dotenv`
- **测试**:`pytest`
- **日志**:Python 标准库 `logging`

## 🚀 快速开始

### 1. 克隆仓库
```bash
git clone https://github.com/Huy1103-coder/huy_ai-agent-learning.git
cd huy_ai-agent-learning
```

### 2. 创建虚拟环境
```bash
conda create -n ai-learning python=3.11
conda activate ai-learning
```

### 3. 安装依赖
```bash
pip install requests python-dotenv pytest
```

### 4. 配置 API Key
在根目录创建 `.env` 文件:

## ✅ 已交付项目

- **week1-files**:Python 文件读写、JSON 处理练习
- **week1-weather**:天气查询 CLI 工具(13 个 pytest)
- **week2-todo**:命令行 Todo 管理工具(19 个 pytest)
- **week2-fastapi**:三个 FastAPI Web 服务示例
- **month2-llm**:LLM 应用开发实战集(10 个程序,含 AI 简历提取器)⭐ NEW