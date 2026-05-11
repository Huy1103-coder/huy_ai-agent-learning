# AI Agent Learning Journey

> 我的 AI Agent 应用开发学习记录，从零基础到能上线 Agent 应用。

## 📅 学习计划

跟着自己制定的《8 个月修正版学习计划》（v3 综合 GPT 与第三方评审两轮迭代），每月一个核心能力，一个可演示项目。

| 月份 | 主题 | 状态 |
|---|---|---|
| 第 1 个月 | Python 小项目 + API 基础 | 🚧 进行中 |
| 第 2 个月 | LLM 应用开发 + Transformer 概念 | ⏳ |
| 第 3 个月 | Tool Calling + 初级 Agent | ⏳ |
| 第 4 个月 | RAG 与知识库 | ⏳ |
| 第 5 个月 | 单 Agent 框架 | ⏳ |
| 第 6 个月 | 多 Agent + 前端 | ⏳ |
| 第 7 个月 | 工程化部署 MVP | ⏳ |
| 第 8 个月 | 作品集打磨 / 进阶 | ⏳ |

## 📂 项目结构

```text
ai-learning/
├── week1-files/                  # 第 1 周练习:Python 文件读写、JSON
│   ├── 01_write_txt.py
│   ├── 02_read_txt.py
│   ├── 03_append_txt.py
│   ├── 04_json_basic.py
│   └── 05_practice.py
├── week1-weather/                # 第 1 周项目:天气查询脚本
│   ├── 01_weather_basic.py       # 基础版:跑通 API 调用
│   ├── 02_weather_pretty.py      # 进阶版:格式化输出
│   ├── 03_weather_robust.py      # 健壮版:异常处理
│   ├── 04_weather_logging.py     # 工程版:日志记录
│   ├── weather_lib.py            # 可测试的库代码
│   ├── test_basic.py             # pytest 入门示例
│   └── test_weather_lib.py       # 单元测试用例
└── hello.py                      # 第一个 Python 测试文件
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