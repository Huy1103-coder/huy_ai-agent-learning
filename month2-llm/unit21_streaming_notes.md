## 一、核心定位

**流式输出 = 非流式输出的"分期付款版"**

总耗时几乎一样,但用户拿到"第一笔钱(首字)"的时间快得多。
所有 LLM 产品(ChatGPT/Claude/Cursor 等)的标配体验。
## 二、流式 vs 非流式:六大差异

| 维度 | 非流式 | 流式 |
|---|---|---|
| API 参数 | 无 stream | stream=True |
| 返回值 | 完整 ChatCompletion 对象 | 迭代器 |
| 接收方式 | 直接拿 response | for chunk in stream |
| 内容字段 | response.choices[0].**message**.content | chunk.choices[0].**delta**.content |
| 内容性质 | 完整回答 | 增量(每块只有"新增"字) |
| 用户体验 | 空白 → 突然全部出现 | 立刻开始打字 → 逐字出现 |

**关键洞察**:用户的"快慢感" ≠ 实际耗时。
优化首字延迟比优化总耗时更影响产品口碑。

## 三、代码模式(必背)

### 基础流式调用

\```python
stream = client.chat.completions.create(
    model="deepseek-chat",
    messages=[{"role": "user", "content": "..."}],
    stream=True,
)

for chunk in stream:
    delta = chunk.choices[0].delta
    if delta.content:
        print(delta.content, end="", flush=True)
\```

### 4 个关键点

1. `stream=True` - 启动流式
2. `for chunk in stream` - 迭代器,只能消费一次
3. `delta` 不是 `message` - 取增量内容
4. `if delta.content:` - 过滤 None

## 四、Delta 增量内容详解

**Delta = 这一小块新增的内容**(不是完整回答)

### 拆解过程

LLM 回答 "你好,我是 DeepSeek" 会拆成:
- chunk 1:role="assistant", content=**None** (开始信号)
- chunk 2:content="你"
- chunk 3:content="好"
- chunk 4:content=","
- chunk 5:content="我"
- chunk 6:content="是"
- chunk 7:content="DeepSeek"
- chunk 8:content=**None**, finish_reason="stop" (结束信号)
- chunk 9(如果开了 stream_options):usage 信息,content=None

### delta.content 何时为 None

1. **第一个 chunk**:只声明 role="assistant",没有实际内容
2. **最后一个 chunk**:结束信号,带 finish_reason
3. **再加一个 chunk**(如果开了 usage):只带 usage 信息

**必须用 `if delta.content:` 过滤**,否则 print(None) 会打印 "None" 4 个字符到屏幕。

## 五、print 三参数(最容易踩坑)

\```python
print(delta.content, end="", flush=True)
\```

| 参数 | 作用 | 缺了会怎样 |
|---|---|---|
| delta.content | 打印当前块的字 | 没字出来 |
| end="" | 不换行 | 每字一行(竖直输出) |
| flush=True | 立刻显示不缓冲 | 攒一波突然全部出现(失去流式感) |

**记忆口诀**:`end='' flush=True` 是流式的两个翅膀,缺一不可。

### 为什么需要 flush=True

Python 的 print 默认有**输出缓冲**——会攒一段再一次性显示。
流式输出不能有缓冲(攒了就不流了)——`flush=True` 强制立刻刷到屏幕。

## 六、TTFT(首字延迟)

**TTFT = Time To First Token**
从用户按回车到看到第一个字的时间。

### 测量代码

\```python
import time

start = time.time()
first_chunk_time = None

for chunk in stream:
    delta = chunk.choices[0].delta
    if delta.content:
        if first_chunk_time is None:        # 只在第一次记录
            first_chunk_time = time.time() - start
        print(delta.content, end="", flush=True)

print(f"首字延迟:{first_chunk_time:.2f} 秒")
\```

### 关键点

- `first_chunk_time = None` 初始化,not `= 0`
- 用 `is None` 判断未初始化
- **正确写法**:`time.time() - start`(现在 - 起点 = 正数)
- **错误写法**:`start - time.time()`(会得到负数 bug)

### 典型数值
- 流式 TTFT:0.3-1.5 秒
- 流式总耗时:3-10 秒

**为什么 TTFT 重要**:用户敏感度远超总耗时。
- 5 秒后才出现的产品 → "卡"
- 0.5 秒出现的产品 → "流畅"
- 生产优化优先级:TTFT > 吞吐率 > 总耗时

## 七、流式 + Token 统计

### 必须加参数

\```python
stream = client.chat.completions.create(
    model="deepseek-chat",
    messages=[...],
    stream=True,
    stream_options={"include_usage": True},   # 关键!
)

usage_info = None

for chunk in stream:
    if chunk.choices and chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
    
    if chunk.usage:                # 最后一个 chunk 包含 usage
        usage_info = chunk.usage

print(f"输入 token:{usage_info.prompt_tokens}")
print(f"输出 token:{usage_info.completion_tokens}")
print(f"总计 token:{usage_info.total_tokens}")
\```

### 为什么必须用

生产代码必须**记录每次调用的成本**——按 token 计费。
没有 token 信息 = 不知道花了多少钱 = 没法计费/告警/优化。

### 实测数据感(DeepSeek 中文)

- 155 字回答 ≈ 74 token
- **粗算公式:汉字数 ÷ 2 = token 数**

以后估算 LLM 应用成本时,中文场景按"字数 ÷ 2"粗算就够准。

## 八、错误处理:三层架构

### 完整模板

\```python
from openai import OpenAI, APIError, APIConnectionError, RateLimitError

def safe_streaming_chat(question: str) -> str:
    full_text = ""
    try:                                        # 外层:整体错误
        stream = client.chat.completions.create(...)
        
        for chunk in stream:
            try:                                # 内层:单 chunk 错误
                if chunk.choices and chunk.choices[0].delta.content:
                    text = chunk.choices[0].delta.content
                    full_text += text
                    print(text, end="", flush=True)
            except Exception as e:
                print(f"\n 解析 chunk 失败:{e}")
                continue                        # 关键:continue 不要 break
        
        return full_text
    
    except RateLimitError as e:                # 限流
        print(f"\n 限流:{e}")
        return ""
    except APIConnectionError as e:            # 网络
        print(f"\n 网络错误:{e}")
        return ""
    except APIError as e:                      # API 错误
        print(f"\n API 错误:{e}")
        return ""
    except Exception as e:                     # 兜底
        print(f"\n 未知错误:{e}")
        return ""
\```

### 三层逻辑

1. **外层 try**:整个流的失败(网络断/限流/认证错)
2. **内层 try**:单个 chunk 解析失败,**不中断后续 chunk**
3. **分类捕获**:不同异常给用户不同提示

### 为什么用 continue 不用 break

- continue:跳过这个坏 chunk,继续接收后面的好 chunk
- break:立刻退出 for 循环,后面的好 chunk 也不要了
- 单 chunk 错通常是偶发的(网络抖动)
- "扔掉一个字"比"扔掉整段回答"用户体验好得多

## 九、流式不适用的场景

**判断标准**:
- 边收边显示 → 用流式
- 收齐再处理 → 用非流式

### 不适合流式的场景

| 场景 | 原因 |
|---|---|
| 结构化输出(JSON 提取) | JSON 需要完整字符串才能解析 |
| Pydantic 校验 | 需要完整数据才能校验 |
| 整段后处理(翻译/总结) | 需要全文才能做整体操作 |
| LLM 输出再作为下一步输入 | 中间结果碎片化没意义 |

## 十、踩过的 bug 与教训

### Bug 1:减法颠倒(-0.62 秒)

\```python
# 错
first_chunk_time = start - time.time()       # 起点 - 现在 = 负数

# 对
first_chunk_time = time.time() - start       # 现在 - 起点 = 正数
\```

**教训**:永远是"现在 - 过去 = 时间差"。
看到负时间立刻追究,不要"觉得可能正常"就跳过。

### Bug 2:`__main__` 拼写错误

\```python
# 错(if 永远不成立,脚本看似没跑)
if __name__ == "main":

# 对
if __name__ == "__main__":
\```

**教训**:Python 的 dunder 名字**前后各 2 个下划线**。
常见错误:"main"、"_main_"、"__main"、"main__"、"__MAIN__"
症状:代码不报错,但脚本运行后屏幕完全空白(if 永远 False)。

### Bug 3:函数定义但忘了调用

\```python
def streaming_chat():
    ...

if __name__ == "__main__":
    non_streaming_chat()
    # 忘了 streaming_chat()
\```

**教训**:`def` 只定义,`function_name()` 才执行。
脚本"看似没跑"时,先检查"我调用它了吗"。

### Bug 4:`chunk` 写成 `chunks`

\```python
for chunks in stream:   # 不报错,但命名误导
    ...
\```

**教训**:Python 命名约定——`for X in Y` 中,X 是单数(单个元素)。

## 十一、自测题(凭印象答,不查代码)

1. `for chunk in stream:` 这一行,stream 是什么类型?
2. `delta.content` 什么时候会是 None?(至少 2 种情况)
3. 如果去掉 `if delta.content:` 这一行,屏幕上会出现什么?
4. `stream_options={"include_usage": True}` 不加的话,流式调用还能拿到 token 数据吗?
5. 为什么单 chunk 错误用 `continue` 而不是 `break`?

### 参考答案

1. **迭代器**(只能消费一次,遍历完就空了)
2. **第一个 chunk**(只有 role 信息)、**最后一个 chunk**(结束信号)、**usage chunk**(如果开了 stream_options)
3. 屏幕上打印出 **"None"** 4 个英文字符(不是空白,是真实文字),破坏打字效果
4. **拿不到**——不加这个参数,chunk.usage 一直是 None
5. **continue 跳过这个坏 chunk 但保留后续好 chunk**;break 会让整个流提前结束,后面的内容也丢了

## 十二、核心心智模型(一句话总结)

**流式输出 = 非流式输出的"分期付款版"**

- 总价格一样(总耗时近似)
- 但用户拿到第一笔钱(首字)的时间快得多
- 实现关键:`stream=True` 启动 + `for chunk in stream` 迭代 + `print(end="", flush=True)` 立刻显示

## 十三、应用场景速查表

| 我想做的事 | 用哪种 |
|---|---|
| 聊天对话(给用户看) | 流式 |
| 长文生成(写文章/邮件) | 流式 |
| 提取 JSON 字段 | 非流式 |
| Pydantic 数据校验 | 非流式 |
| 翻译整段文字 | 非流式 |
| 工具调用决策(Tool Calling) | 非流式 |
| 多步骤推理(中间结果给下一步) | 非流式 |

## 十四、扩展知识(留给以后学)

- **流式 + Markdown 渲染**:终端用 `rich` 库的 Live + Markdown,可以边收边渲染
- **流式 + 重试机制**:中途断了如何续上(第 5 月学 Agent 时遇到)
- **流式 + 并发**:多个流并发处理,避免阻塞
- **流式 + 日志**:每次调用记录 TTFT、总耗时、token 量到日志,方便监控

## 文件清单(本单元产出)

- `11_streaming_basic.py` - 流式 vs 非流式对比
- `12_streaming_with_usage.py` - 流式 + token 统计
- `13_streaming_with_error.py` - 流式 + 错误处理

学习日期:2026 年 5 月
单元状态:已完成
笔记编号:#121-126