## 一、核心定位
**这一单元解决:多轮对话的 token 怎么管?怎么省钱?怎么避免崩溃?**
第 2 个月的"集大成"单元——之前所有内容(多轮对话、流式、错误处理、OOP)在这里被组合用上。

## 二、Token 累积是平方级,不是线性
### 单轮 vs 多轮的成本差异
每轮对话的输入 token 大约是线性增长(每轮多 20-30 token),但**多轮对话的总成本是平方级**——因为每轮都要带上前面所有历史。
### 数学公式
单轮输入 token ≈ 20 × N (线性) 
N 轮总输入 token ≈ 10 × N² (平方级!)
### 实测数据(10 轮独立问答)
| 数据点 | 数值 |
|---|---|
| 第 1 轮输入 | 18 token |
| 第 10 轮输入 | 215 token |
| 单轮增长 | 11.9x |
| 10 轮总输入 | 1063 token |
| 10 轮总成本 | ¥0.000753 |
### 外推到大规模
| 轮数 | 总输入 token | 相比 10 轮 |
|---|---|---|
| 10 轮 | 1,000 | 1x(基准) |
| 50 轮 | 25,000 | **22x** |
| 100 轮 | 100,000 | **88x** |
| 500 轮 | 2,500,000 | **2200x** |
**记忆点**:每多聊 1 轮,不止多花 1 轮的钱,是多花"前面所有轮的钱"。
### 生产意义
- 不优化:用户量稍大就破产
- 优化好:几行代码省 30-50% 成本
- 1 万用户 × 100 轮/天 × 不优化 → 月成本 ¥21,000
- 同规模 + 滚动窗口 → 月成本 ¥10,000-15,000(省一半)

## 三、4 种历史管理策略
### 策略 ①:滚动窗口(Sliding Window)⭐ 最常用
**思路**:只保留最近 N 轮对话,更早的丢掉。
**优点**:
- 简单,零额外成本
- 实现只需几行代码
- 效果立竿见影
**缺点**:
- 丢失早期信息(用户开头说的名字、需求会被遗忘)
**适用**:独立问答(客服 FAQ、知识查询)
### 策略 ②:摘要压缩(Summarization)
**思路**:历史超过阈值时,让 LLM 自己生成一段摘要替代旧消息。
**优点**:
- 保留关键信息(姓名、意图、决策)
- 支持超长对话不爆 context window
**缺点**:
- 需要额外 LLM 调用(摘要本身也花钱)
- 可能丢细节
- 实现更复杂
**适用**:长对话、咨询、教学
### 策略 ③:关键消息保留(Important Message Pinning)
**思路**:总保留 system + 第一条 user 消息(用户初始意图),中间的滚动丢弃。
**优点**:保留用户初始意图,不失焦
**缺点**:不灵活
**适用**:任务型对话(订单、填表、多步骤流程)
### 策略 ④:混合策略 ⭐ 生产标准
**思路**:组合上面三种,按情况切换。
正常情况:滚动窗口(便宜) 
对话超过 N 轮:触发摘要 
关键消息:永远保留(system、首条 user)
**适用**:生产级 AI 应用

## 四、滚动窗口的实现(OOP 入门)
### 核心类设计
\```python
class ConversationManager:
    """带滚动窗口的对话管理器"""
    
    def __init__(self, system_prompt: str, window_size: int = 5):
        self.system = {"role": "system", "content": system_prompt}
        self.window_size = window_size
        self.history = []   # 不含 system,只含 user/assistant 对
    
    def add_user(self, content: str):
        self.history.append({"role": "user", "content": content})
    
    def add_assistant(self, content: str):
        self.history.append({"role": "assistant", "content": content})
    
    def get_messages(self) -> list:
        """返回 [system] + [最近 N 轮对话]"""
        keep_count = self.window_size * 2   # 1 轮 = 2 条消息
        if len(self.history) > keep_count:
            recent = self.history[-keep_count:]
        else:
            recent = self.history
        return [self.system] + recent
\```
### 关键设计要点
| 要点 | 含义 |
|---|---|
| `window_size * 2` | 1 轮对话 = user + assistant = 2 条消息 |
| `self.history[-N:]` | 切片取最后 N 条 |
| `[self.system] + recent` | 列表拼接,system 永远在最前 |
| 每个对象独立 history | 多用户场景每人一个 manager,互不干扰 |
### 实测节省效果(10 轮对话)
| 策略 | 总输入 token | 节省率 |
|---|---|---|
| 无窗口(全保留) | 1063 | 0%(基准) |
| 滚动窗口=5 | 885 | **16.7%** |
| 滚动窗口=3 | 668 | **37.2%** |

## 五、摘要压缩的实现
### 核心思想
原始历史:[50 条消息, 5000 token] 
↓ 
发给 LLM 让它总结 
↓
 摘要:"用户名叫张明,问了 3 个 Python 问题..." (200 token) 
↓ 
新 messages = [ system, {"role": "system", "content": f"以下是之前的对话摘要:{摘要}"}, 最近 N 条原始消息, ]
### 智能管理器架构
\```python
class SmartConversationManager:
    def __init__(self, system_prompt, window_size=3, summarize_threshold=6):
        self.system = {"role": "system", "content": system_prompt}
        self.window_size = window_size
        self.summarize_threshold = summarize_threshold
        self.history = []      # 最近对话(未压缩)
        self.summary = ""      # 累积的摘要
    
    def add_assistant(self, content):
        self.history.append({...})
        # 检查是否需要压缩
        if len(self.history) // 2 > self.summarize_threshold:
            self._compress()
    
    def _compress(self):
        keep_count = self.window_size * 2
        to_summarize = self.history[:-keep_count]    # 早期(要压缩)
        recent = self.history[-keep_count:]           # 最近(保留)
        
        self.summary = summarize_history(to_summarize)
        self.history = recent
    
    def get_messages(self) -> list:
        messages = [self.system]
        if self.summary:
            messages.append({
                "role": "system",
                "content": f"以下是之前的对话摘要:{self.summary}"
            })
        messages.extend(self.history)
        return messages
\```
### 摘要 Prompt 模板
\```
你是对话摘要助手。请把下面这段对话压缩成一段话(不超过 100 字),
保留:
1. 用户的关键信息(姓名、需求、决策)
2. 已经讨论过的主要话题
3. 重要的结论或承诺
省略:
1. 寒暄
2. 详细解释的内容
3. 重复信息
只输出摘要,不要其他文字。
\```
### 实测效果(10 轮对话)
- 触发了 2 次压缩(第 5 轮后、第 8 轮后)
- 第 7 轮"我叫什么名字?" → 模型答对 ✅
- 第 8 轮"我学的是什么语言?" → 模型答对 ✅
- 第 9 轮"你推荐了什么资源?" → 模型答对 ✅
- 最终摘要保留:用户名、推荐资源、就业方向、薪资范围

---

## 六、两种策略的 trade-off
| 维度 | 滚动窗口 | 摘要压缩 |
|---|---|---|
| 实现复杂度 | 简单(几行代码) | 复杂(需额外 LLM 调用) |
| Token 节省 | 高(直接丢弃) | 中(摘要也占空间) |
| 早期信息保留 | ❌ 丢失 | ✅ 保留 |
| 适合对话深度 | 5-15 轮 | 15+轮 |
| 适合场景 | 独立问答 | 长对话、咨询 |
### 选择指南
- 对话深度 <10 轮:**滚动窗口足够**
- 对话深度 10-20 轮:**根据信息保留重要度选**
- 对话深度 >20 轮:**摘要压缩必须开**
- 生产级综合应用:**混合策略**

## 七、Token 节省 ≠ 成本节省
### 计费的两个维度
LLM 计费分**输入**和**输出**,**单价不同**:
| 类型 | DeepSeek 单价 |
|---|---|
| 输入 token | ¥0.5 / 百万 |
| 输出 token | ¥2 / 百万(贵 4 倍) |
### 实测对比
窗口=3 vs 无窗口:
输入 token 节省 37.2%
输出 token 没变
总成本节省 21.9%
### 工程含义
- 优化历史管理只省输入 token
- 想真省成本,还要让模型输出更短(prompt 控制)
- 报告优化效果时说清楚"输入节省"还是"总成本节省"
### 输出 token 优化(隐藏知识点)
- 在 system 加 "回答不超过 N 字"
- 用 `max_tokens=N` 强制截断
- 让模型用 bullet 而不是段落

## 八、踩过的 bug 与教训
### Bug 1:硬编码 vs 命名变量
\```python
# 错(硬编码 10,改 window_size 不生效)
recent = self.history[-10:] if len(self.history) > keep_count else self.history
# 对
recent = self.history[-keep_count:] if len(self.history) > keep_count else self.history
\```
**教训**:代码里的每个魔法数字,都是未来 bug 的种子。
### Bug 2:漏单位转换
\```python
# 错(漏 *100,百分比变成小数)
saved_pct = (1 - result["total_input"] / baseline)
# 输出:0.2%(其实是 16.7%)
# 对
saved_pct = (1 - result["total_input"] / baseline) * 100
\```
**教训**:数字异常时手算一遍验证。看到"节省 0.2%"应该警觉。
### Bug 3:模型名拼写
\```python
# 错
model="deppseek-chat"   # 两个 p
# 对
model="deepseek-chat"
\``
**教训**:API 字段名要从官方文档复制,不要凭记忆敲。
### Bug 4:role 字段拼写
\```python
# 错
{"role": "assitant", ...}   # 少一个 s
# 对
{"role": "assistant", ...}
\```
**教训**:LLM API 的字段值也要精确,assistant/user/system 一个字母都不能错。

## 九、面向对象编程(OOP)入门
### 核心三件套
\```python
class ConversationManager:                    # 1. class 定义模板
    def __init__(self, ...):                   # 2. __init__ 构造函数
        self.history = []                      # 3. self 代表当前对象
\```
### 类 vs 函数的选择
**用函数**:输入→输出,无状态,做完就完
**用类**:需要状态(数据)、多个独立实例、操作和数据强相关
### 类的核心价值
1. **多实例独立状态**——每个用户一个 manager,互不影响
2. **封装实现细节**——调用者只需要 add_user/add_assistant/get_messages
3. **代码组织清晰**——所有对话相关逻辑都在一个类里

### 关键概念
- **`__init__`**:构造函数,创建对象时自动调用
- **`self`**:对当前对象自己的引用("我自己")
- **属性(self.x)**:对象的"状态",持久存在
- **方法(def func(self))**:对象的"动作",自带 self 参数
- **`__init__` 必须初始化所有属性**:否则用时抛 AttributeError

## 十、自测题(凭印象答)
1. **N 轮对话的总输入 token 是线性增长还是平方级增长?**
2. **`window_size = 5` 意味着保留多少条消息?**
3. **滚动窗口和摘要压缩,哪个更适合"客服 FAQ"场景?哪个更适合"长期咨询"场景?**
4. **`self.history[-10:]` 这个切片如果 history 只有 5 条,会怎样?**
5. **滚动窗口节省了 37% 输入 token,总成本是不是也节省了 37%?为什么?**
6. **`__init__` 不写 `self.history = []`,后续 `add_user` 会发生什么?**
### 参考答案
1. **平方级**——单轮线性增长,但总成本是平方(每轮带上前面所有历史)
2. **10 条**——1 轮 = user + assistant = 2 条
3. **客服 FAQ → 滚动窗口**(独立问题,不需要记早期);**长期咨询 → 摘要压缩**(早期信息重要)
4. **返回全部 5 条**——Python 切片很宽容,索引超出不报错,有多少给多少
5. **不是**——输入和输出单价不同(输出贵 4 倍),输入节省 37% 但输出没动,总成本节省更少(约 22%)
6. **抛 AttributeError**——`self.history` 属性不存在,Python 不允许访问未初始化的属性

## 十一、核心心智模型(一句话总结)
**Token 优化的本质是"上下文管理"**:
- 模型本身无状态,所有"记忆"都靠你塞进 messages 列表
- 塞得越多,越贵
- 塞得越少,越笨
- 工程的核心:**用最少的 token 让模型表现最聪明**

## 十二、应用场景速查表
| 场景 | 推荐策略 |
|---|---|
| 客服 FAQ(独立问答) | 滚动窗口=5 |
| 简单聊天助手 | 滚动窗口=10 |
| Python 学习陪练 | 摘要压缩(轮数多,需要记历史) |
| 订单/表单流程 | 关键消息保留 + 滚动窗口 |
| 长文档分析 | 摘要压缩 |
| 实时翻译 | 滚动窗口=3(短上下文足够) |
| 心理咨询(高质量) | 混合策略(摘要 + 关键 + 滚动) |
| 一次性任务(写文档) | 不需要历史管理 |

## 十三、扩展知识(以后学)
- **异步摘要**:后台压缩,不阻塞用户
- **增量摘要**:只总结新增部分,不重做
- **多级摘要**:超早期再压缩成更短摘要
- **向量召回**:把历史存向量库,根据当前问题召回相关片段(第 4 个月 RAG)
- **关键消息提取**:用 LLM 自动识别"哪些消息必须保留"
- **混合存储**:近期消息原文 + 中期消息摘要 + 长期消息向量

## 十四、本单元产出
### 文件清单
- `14_token_growth.py` - 测真实 token 增长曲线
- `15_sliding_window.py` - 滚动窗口实现
- `16_summary_compression.py` - 摘要压缩实现
### 知识点累积
- 笔记编号:#127 ~ #139(共 13 条)
- 完成时间:2026 年 5 月
- 状态:已完成
### 引入新概念
- 面向对象编程(OOP)入门
- 类(class)、构造函数(__init__)、self 引用
- Python 切片的宽容性
- 重构未完成 bug 模式