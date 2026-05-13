# Week 2 FastAPI Project

第 2 周 FastAPI 入门项目,演示从 CLI 工具到 Web API 的演进。

## 三个示例服务

### 1. Hello World (`01_hello.py`)
最简单的 FastAPI 应用,演示 GET 接口和路径参数。

### 2. 文本统计 API (`02_text_api.py`)
演示 POST 接口、Pydantic 请求体校验、响应模型、HTTPException 错误处理。

### 3. 天气查询 API (`03_weather_api.py`)
复用第 1 周 weather_lib.py 的代码,把 CLI 工具改造成 Web API。

## 关键学习点

- **GET vs POST**:数据少用 GET + 路径/查询参数,数据多用 POST + JSON body
- **Pydantic 校验**:类型注解自动生成校验规则,缺字段自动 422
- **自动文档**:Swagger UI(`/docs`) 和 ReDoc(`/redoc`) 同时可用
- **HTTPException**:用标准状态码 + detail 返回结构化错误
- **库代码与界面分离**:同一份 weather_lib 既被 CLI 用,又被 Web API 用

## 安装

```bash
cd week2-fastapi
pip install fastapi "uvicorn[standard]" python-dotenv requests
```

## 运行

```bash
# Hello World
uvicorn 01_hello:app --reload

# 文本统计
uvicorn 02_text_api:app --reload

# 天气查询(需要 OPENWEATHER_API_KEY 环境变量)
uvicorn 03_weather_api:app --reload
```

启动后访问:
- API 根路径: http://127.0.0.1:8000/
- Swagger UI 文档: http://127.0.0.1:8000/docs
- ReDoc 文档: http://127.0.0.1:8000/redoc

## 接口示例

### 文本统计

```bash
curl -X POST http://127.0.0.1:8000/text/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello\n你好", "language": "zh"}'
```

返回:
```json
{
  "char_count": 8,
  "char_count_no_space": 8,
  "word_count": 8,
  "line_count": 2,
  "language": "zh"
}
```

### 天气查询

```bash
curl http://127.0.0.1:8000/weather/Beijing
```

返回:
```json
{
  "city": "Beijing",
  "country": "CN",
  "temp": 18.5,
  "is_comfortable": true,
  "temp_category": "凉爽",
  ...
}
```

## 项目结构

```text
week2-fastapi/
├── 01_hello.py          # Hello World 示例
├── 02_text_api.py       # 文本统计 API
├── 03_weather_api.py    # 天气查询 API(复用 weather_lib)
├── weather_lib.py       # 从 week1-weather 复制过来的库代码
└── README.md
```

## debug 记录

修复过一个 `NameError: 'HTTPException' is not defined` 导致的 500 错误:
- 现象:正常查询(/weather/Beijing)工作,异常分支(/weather/FakeCityXYZ)崩溃
- 原因:漏 import HTTPException,异常路径触发时 NameError
- 教训:Python 是动态语言,import 缺失要到运行时才暴露,必须测试异常路径