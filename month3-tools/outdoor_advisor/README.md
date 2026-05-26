# 🌤️ 户外通 Agent

> 基于 LLM Function Calling 的户外活动顾问 Agent  
> 第 3 个月主线项目 · AI Agent 应用开发学习路径

## ✨ 项目简介

"户外通" 是一个能根据**实时天气和空气质量**判断**是否适合户外活动**的 AI Agent。

不同于传统天气查询应用,它不只是播报数据,而是基于天气、空气质量、风速等多个维度,**给出明确的活动建议**——推荐 / 谨慎 / 不推荐,并主动指出风险人群、提供可执行建议。

### 演示
用户:今天上海能晨跑吗?
户外通:
⚠️ 谨慎户外活动 — 可以跑,但要注意条件
结论:不太推荐在白天高强度晨跑,如果一定要跑,建议选清晨 5-6 点
判断依据:

气温 31.9°C(偏热)
体感 37.5°C(非常闷热)
AQI 良(2级,PM2.5 仅 13)  ← 空气质量很好
多云、无雨

具体建议:

时间:清晨 5:00-7:00 最佳
强度:降速!不建议高强度或长距离
补水:跑前 200-300ml 水
人群:健康成年人 OK,老人/儿童/心血管疾病者不建议
地点:选树荫多的公园(世纪公园、中山公园)

## 🏗️ 技术架构
┌─────────────────────────────────────────┐
│           main.py (CLI 入口)            │
│  - run_agent()  N 轮循环                │
│  - max_iterations 防爆护栏              │
└──────────┬──────────────────────────────┘
│
┌──────┴──────┬──────────────┐
│             │              │
┌───▼────┐  ┌────▼─────┐  ┌────▼─────┐
│tools.py│  │schemas.py│  │prompts.py│
│        │  │          │  │          │
│工具实现 │  │ LLM 协议 │  │ 角色定义  │
└────┬───┘  └──────────┘  └──────────┘
│
│ HTTP
▼
┌─────────────────┐
│  OpenWeather    │
│  · Weather API  │
│  · Air Quality  │
└─────────────────┘

### 核心设计

- **N 轮循环 Agent**:模型可在工具失败时自主"再试一次",而非固定 2 轮
- **工具失败优雅返回**:所有工具失败返回 `{"error": "..."}`,Agent 不崩溃
- **字段命名工程化**:`temp_celsius` / `wind_speed_ms` / `pm2_5_ugm3` 防单位幻觉
- **多工具参数 DRY**:`CITY_PARAM_DESC` 常量统一所有 city 描述
- **System Prompt 角色化**:把"通用助手"塑造成"户外活动顾问"

## 🚀 快速开始

### 1. 环境要求

- Python 3.11+
- DeepSeek API key([注册](https://platform.deepseek.com))
- OpenWeather API key([注册](https://openweathermap.org/api),免费)

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置 .env

在项目**根目录**(`ai-learning/`)创建 `.env` 文件:

```bash
DEEPSEEK_API_KEY=sk-xxxxx
OPENWEATHER_API_KEY=xxxxx
```

### 4. 运行

**交互模式**:
```bash
cd outdoor_advisor
python main.py
```

**单次查询模式**:
```bash
python main.py "今天北京天气怎么样?"
```

## 🧪 运行测试

```bash
pytest test_tools.py -v
```

应看到 10 个测试全部 PASSED。

## 📁 项目结构
outdoor_advisor/
├── main.py           # Agent 主程序 + CLI 入口
├── tools.py          # 工具实现(get_weather, get_aqi)
├── schemas.py        # LLM 工具 schema
├── prompts.py        # System Prompt 和参数描述常量
├── test_tools.py     # pytest 单元测试(10 个)
├── requirements.txt  # 依赖清单
└── README.md         # 本文档

## 🎓 学习要点

本项目实践了以下 Agent 工程核心概念:

1. **Function Calling 协议** —— 模型决策、代码执行、结果回喂的 N 轮循环
2. **工具设计** —— 字段单位标注、错误处理契约、内部辅助函数命名
3. **System Prompt 工程** —— 角色化、决策规则显式化、行为锁定
4. **DRY 原则** —— 多工具公共参数抽常量
5. **测试覆盖** —— 单元测试 + 边界测试(失败路径)

## 🛣️ 后续改进方向

- [ ] 接入预报 API(支持"明早跑步"这类时间敏感问题)
- [ ] 加入 HITL 机制(高风险结论前的人工确认)
- [ ] Streamlit Web UI(替代 CLI)
- [ ] 多语言城市名映射(支持纯中文输入)
- [ ] 历史查询记录持久化

## 📝 项目背景

本项目是个人 AI Agent 应用开发学习路径的第 3 个月主线项目,完成单元 24-31 的所有知识点实践。

学习时间:2026 年 4-5 月  
GitHub:[huy_ai-agent-learning](https://github.com/Huy1103-coder/huy_ai-agent-learning)

