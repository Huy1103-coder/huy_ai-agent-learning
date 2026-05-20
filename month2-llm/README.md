# Month 2: LLM 应用开发

第 2 个月的 LLM API 调用、Prompt 工程、结构化输出、流式响应、Token 优化实战项目集合。

## 学习成果

完成了 16 个递进式的实战程序 + 2 份深度复习笔记,覆盖 LLM 应用开发的核心能力。

## 文件清单

### 基础 API 调用
- **01_hello_llm.py** — 第一次调用 DeepSeek API,理解 messages 结构
- **02_no_memory.py** — 验证 LLM 是无状态的(模型"金鱼记忆"实验)
- **02b_fake_memory.py** — 伪造历史让模型"以为"记得(理解上下文即真相)
- **03_with_memory.py** — 通过维护 messages 列表实现多轮对话

### 参数控制
- **04_temperature_test.py** — temperature=0 vs 1.5 的输出差异对比

### Prompt 工程
- **05_system_prompt.py** — 同一问题,3 种 system prompt 演绎不同人设
- **06_prompt_comparison.py** — 好 prompt vs 差 prompt 的输出质量差异
- **07_my_customer_service.py** — 生产级电商客服 prompt,6 场景压力测试

### 结构化输出
- **08_structured_basic.py** — 纯 prompt 引导 vs response_format JSON 模式
- **09_structured_with_pydantic.py** — LLM + Pydantic 完整流程
- **10_resume_extractor.py** ⭐ — AI 简历信息提取器(嵌套 Pydantic 模型)

### 流式输出(Streaming)
- **11_streaming_basic.py** — 流式 vs 非流式对比 + TTFT 测量
- **12_streaming_with_usage.py** — 流式 + token 统计
- **13_streaming_with_error.py** — 流式 + 三层错误处理

### Token 优化与成本控制
- **14_token_growth.py** — 实测多轮对话的 token 平方级增长
- **15_sliding_window.py** ⭐ — 滚动窗口实现(节省 37% token)
- **16_summary_compression.py** ⭐ — 摘要压缩(保留早期信息)

### 深度复习笔记
- **unit21_streaming_notes.md** — 流式输出完整知识体系
- **unit22_token_optimization_notes.md** — Token 优化完整知识体系

## 核心收获

### 1. LLM 是无状态纯函数
模型本身没有记忆,"记得"是因为客户端把完整对话历史每次都发过去。
所有 Agent 框架的"记忆功能"本质都是在管理 messages 列表。

### 2. system prompt 是"剧本",不是开场白
90% 的 Prompt 工程工作都在调 system prompt。
PRCF 四要素:Persona / Rules / Context / Format。

### 3. 结构化输出的 4 道防线
- Prompt 引导(弱约束)
- response_format JSON 模式(API 层强制)
- Pydantic schema 校验(结构约束)
- 业务代码异常处理(兜底)

### 4. 流式输出的核心代码 3 件套
- `stream=True` 启动
- `for chunk in stream` 迭代
- `print(end="", flush=True)` 立刻显示

### 5. Token 累积是平方级,不是线性
N 轮对话总输入 ≈ 10 × N²。50 轮是 10 轮的 22 倍,100 轮是 88 倍。
不优化的 AI 客服,用户量稍大就破产。

### 6. 历史管理的 trade-off
- 滚动窗口:简单,丢失早期信息
- 摘要压缩:复杂,保留早期信息
- 生产级混合:system + 关键消息 + 摘要 + 滚动窗口

### 7. LLM 推理能力是双刃剑
能从碎片信息推理(自动算工作年限),但也会编造原文没有的内容(幻觉)。
对策:更硬的 prompt + temperature=0 + 业务校验函数。

## 技术栈

- **LLM**: DeepSeek V3(API 兼容 OpenAI 协议)
- **SDK**: `openai` Python 库
- **校验**: `pydantic` v2
- **配置**: `python-dotenv`

## 安装

\```bash
cd month2-llm
pip install openai pydantic python-dotenv
\```

## 配置 API Key

在项目根目录(上一层)创建 `.env` 文件:

\```
DEEPSEEK_API_KEY=sk-你的_DeepSeek_API_Key
\```

[注册 DeepSeek API](https://platform.deepseek.com)

## 运行示例

\```bash
# 基础 API 调用
python 01_hello_llm.py

# AI 简历提取器(作品级项目)
python 10_resume_extractor.py

# 流式输出对比
python 11_streaming_basic.py

# Token 增长曲线
python 14_token_growth.py

# 滚动窗口 + 摘要压缩
python 15_sliding_window.py
python 16_summary_compression.py
\```

## 已完成单元

- [x] 单元 16: 第一次 LLM API 调用
- [x] 单元 17: messages 数组与多轮对话
- [x] 单元 18: 多轮对话历史管理
- [x] 单元 19: Prompt 工程入门
- [x] 单元 20: 结构化输出 + Pydantic
- [x] 单元 21: Streaming 流式输出
- [x] 单元 22: Token 优化与成本控制

## 待完成

- [ ] 单元 23: Transformer 概念笔记(B 线,选学)

## 学习笔记编号

本月累计学习笔记: #83 ~ #139(共 57 条)。
两份完整复习笔记:
- [单元 21:Streaming 流式输出](./unit21_streaming_notes.md)
- [单元 22:Token 优化与成本控制](./unit22_token_optimization_notes.md)