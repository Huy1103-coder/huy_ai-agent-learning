# 📊 CSV 数据分析 Agent(数据探长)

> 一个基于大语言模型的智能 CSV 数据分析助手，能自主选择工具，多轮推理、诚实承认能力边界，输出结构化的分析报告。

把一份CSV丢给它，用自然语言提问(""哪个部门业绩最好?""有哪些异常？")，它会像一名数据分析师一样：**自主调用工具 -> 多角度交叉验证 -> 输出分级报告 + 业务建议**。

---

### 核心亮点

- **5个 production 级数据工具**：加载、筛选、列统计、分组聚合、异常检测，覆盖数据分析的高频需求
- **4 方法投票异常检测**:IQR + Z-score + Modified Z-score + 业务规则,投票分级(极端/严重/中度/轻度),单方法盲区互补
- **Agent 自主多轮推理**:N 轮循环架构,能自主组合工具、交叉验证判断,而非简单"一问一答"
- **诚实工程**:面对超出能力的请求(预测未来、生成图表、发邮件),诚实承认边界并提供替代方案,而非伪造结果
- **性能优化**:DataFrame 缓存(避免重复读取)+ 大文件智能抽样,可处理 10 万行级数据
- **24 个单元测试**:覆盖 5 个工具的正常路径、失败路径、边界 CSV、防回归(召回率 + 精确率双面守护)

---

## 🚀 快速开始

### 环境要求
- Python 3.11+
- DeepSeek API Key(或其他 OpenAI 兼容的 API)

### 安装

\`\`\`bash
# 克隆仓库
git clone https://github.com/你的用户名/csv-analyst.git
cd csv-analyst

# 安装依赖
pip install -r requirements.txt

# 配置 API Key(在项目根目录建 .env 文件)
echo "DEEPSEEK_API_KEY=你的key" > .env
\`\`\`

### 运行

\`\`\`bash
python main.py "data/sales.csv 这份数据有哪些异常?"
\`\`\`

---

## 🏗️ 架构设计

\`\`\`
用户提问
   ↓
main.py(N 轮循环 Agent)
   ↓ LLM 自主决定调用哪些工具
tools.py(5 个工具 + 缓存 + 抽样)
   ↓ 返回结构化数据
LLM 综合推理 → 结构化报告
\`\`\`

### 工具集(tools.py)

| 工具 | 功能 | 设计要点 |
|------|------|---------|
| `load_csv` | 加载数据全景 | 4 层路径检查 + 友好类型适配 |
| `filter_rows` | 按条件筛选 | mask 累加 + min/max 后缀约定 |
| `column_stats` | 单列统计 | 数值/文本双分支 |
| `group_stats` | 分组聚合 | 白名单聚合函数 + 大文件抽样 |
| `detect_anomalies` | 异常检测 | 4 方法投票 + 严重程度分级 |

### 工程亮点

- **DataFrame 缓存**:用文件修改时间(mtime)做失效判断,多工具共享一次加载,实测 5 工具调用提速约 4 倍
- **分工具抽样策略**:统计类工具(group/column)对大文件抽样提速,异常检测/精确查询强制全量(避免异常被稀释)
- **能力边界 prompt 工程**:在 system prompt 显式声明 4 类不可做的事(预测/可视化/外部动作/业务判断),让 Agent 诚实而非伪造
- **报告模板 + 弹性规则**:复杂问题套用结构化 4 段报告(TL;DR / 数据依据 / 关键发现 / 建议下一步),简单问题智能省略

---

## 🧪 测试

\`\`\`bash
pytest test_tools.py -v
\`\`\`

24 个单元测试,约 0.6 秒跑完,覆盖:
- 5 个工具的正常路径 + 失败路径
- 边界 CSV(空文件 / 只有表头 / 非 CSV / 文件不存在)
- 异常检测双面守护:召回率(真异常不漏)+ 精确率(防假阳性)

---

## 📁 项目结构

\`\`\`
csv_analyst/
├── main.py              # Agent 主程序(N 轮循环 + 工具调度)
├── tools.py             # 5 个工具 + 缓存层 + 抽样层
├── schemas.py           # 工具的 JSON Schema 定义
├── prompts.py           # 数据探长 system prompt
├── test_tools.py        # 24 个 pytest 单元测试
├── requirements.txt     # 依赖清单
├── data/
│   └── sales.csv        # 示例数据(240 行)
└── examples/
    ├── 05_agent_stress_test.py   # Agent 能力压力测试(L1-L4)
    ├── 06_perf_test.py           # 缓存性能测试
    ├── 07_test_sampling.py       # 大文件抽样测试
    └── generate_large_data.py    # 生成大测试数据(10 万行)
\`\`\`

---

## 🛠️ 技术栈

- **LLM**:DeepSeek(OpenAI 兼容 API)
- **数据处理**:pandas
- **测试**:pytest
- **架构**:Function Calling + N 轮循环 Agent

---

## 📄 License

MIT

