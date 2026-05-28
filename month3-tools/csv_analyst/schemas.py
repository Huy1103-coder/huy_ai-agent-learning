"""
schemas.py - LLM 工具调用的 schema 定义

工程原则:
- description 写清字段含义 + 单位
- 边界明确(支持什么不支持什么)
- 字段名 description 必要时用常量统一(本项目工具少,暂时不需要)
"""
"""schemas.py - LLM 工具调用的 schema 定义"""

tools = [
    {
        "type": "function",
        "function": {
            "name": "load_csv",
            "description": (
                "加载 CSV 文件并返回数据摘要(行数/列数/列名/列类型/前 5 行/数值列统计)。"
                "用于第一次探查未知 CSV 数据。不返回完整数据。"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "CSV 文件路径,如 'data/sales.csv'。后缀必须是 .csv。",
                    },
                },
                "required": ["file_path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "filter_rows",
            "description": (
                "按条件筛选 CSV 行,用于精确查询某些数据。"
                "conditions 字典支持 3 种条件:"
                "(1) 精确匹配 {'name': '杨帆', 'month': 8};"
                "(2) 数值下限 {'sales_amount_min': 100000} 表示 >= 100000;"
                "(3) 数值上限 {'sales_amount_max': 50000} 表示 <= 50000。"
                "多个条件用 AND 组合。最多返回 50 行(truncated 字段提示是否截断)。"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "CSV 文件路径",
                    },
                    "conditions": {
                        "type": "object",
                        "description": (
                            "筛选条件字典。键是列名(或加 _min/_max 后缀),值是要匹配的值。"
                            "例如 {'name': '杨帆', 'month': 8} 或 {'sales_amount_min': 200000}"
                        ),
                    },
                    "max_rows": {
                        "type": "integer",
                        "description": "最多返回多少行,默认 50",
                    },
                },
                "required": ["file_path", "conditions"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "column_stats",
            "description": (
                "对某一列做深度统计分析,超出 load_csv 的 describe 范围。"
                "数值列返回: count/mean/median/std/min/max/q25/q75/top_n_max/bottom_n_min/IQR 异常判定。"
                "文本列返回: count/missing/unique 数量,以及前 5 个最常见值。"
                "用于用户问'这一列详细情况''最大的 5 个''异常值数量'等具体问题时。"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "CSV 文件路径",
                    },
                    "column": {
                        "type": "string",
                        "description": "要分析的列名,如 'sales_amount' 或 'department'",
                    },
                    "top_n": {
                        "type": "integer",
                        "description": "返回最大/最小的 N 个值,默认 5",
                    },
                },
                "required": ["file_path", "column"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "group_stats",
            "description": (
                "按某列分组,对另一列做聚合统计。"
                "类似 SQL 的 GROUP BY + 聚合函数。"
                "用于'各部门销售总额对比''每个员工平均成交数'等分组统计问题。"
                "聚合函数支持 sum/mean/median/max/min/count。"
                "结果按聚合值降序排列。"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "CSV 文件路径",
                    },
                    "group_by": {
                        "type": "string",
                        "description": "分组列,如 'department' 或 'name'",
                    },
                    "agg_column": {
                        "type": "string",
                        "description": "聚合列(必须是数值列,count 除外),如 'sales_amount'",
                    },
                    "agg_func": {
                        "type": "string",
                        "description": "聚合函数:sum/mean/median/max/min/count,默认 sum",
                    },
                },
                "required": ["file_path", "group_by", "agg_column"],
            },
        },
    },
    {
    "type":"function",
    "function":{
        "name":"detect_anomalies",
        "description":("综合 4 种异常检测方法,精准识别数据中的离群点。"
            "使用 IQR/ Z-score / Modified Z-score / 业务规则 4 种方法投票,"
            "按 4 票/3 票/2 票/1 票 把异常分为 极端/严重/中度/轻度 4级。"
            "比 column_stats 的单一 IQR 方法更精准，能发现 IQR 漏掉的低端异常。"
            "用于用户明确问'有哪些异常''异常集体是哪些记录'等问题。"
        ),
        "parameters":{
          "type":"object",
          "properties":{
              "file_path":{
                        "type": "string",
                        "description": "CSV 文件路径",
                    },
                    "column": {
                        "type": "string",
                        "description": "要检测异常的列名,必须是数值列",
                    },
                    "max_anomalies": {
                        "type": "integer",
                        "description": "最多返回多少个异常行,默认 20",
                    },
          },
          "required":["file_path","column"],
        },
      },
    },
]