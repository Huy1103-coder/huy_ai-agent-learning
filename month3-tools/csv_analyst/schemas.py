"""
schemas.py - LLM 工具调用的 schema 定义

工程原则:
- description 写清字段含义 + 单位
- 边界明确(支持什么不支持什么)
- 字段名 description 必要时用常量统一(本项目工具少,暂时不需要)
"""

tools =[
    {
        "type":"function",
        "function":{
            "name":"load_csv",
            "description":(
                "加载 CSV 文件并且返回数据摘要，包括："
                "文件元信息（路径/行数/列数），"
                "列名列表 + 列类型（text/integer/decimal）,"
                "前 5 行数据预览，"
                "前5行数据预览，"
                "数值列的描述性统计（count/mean/std/min/25%/50%/75%/max)."
                "用于探查未知 CSV 数据，了解数据结构和初步统计特征。"
                "不返回完整数据（避免上下文爆炸）。"
            ),
            "parameters":{
                  "type":"object",
                  "properties":{
                      "file_path":{
                          "type":"string",
                          "description":(
                              "CSV 文件的相对或绝对路径,如 "
                            "'data/sales.csv' 或 'D:/data/report.csv'。"
                            "文件后缀必须是 .csv。"
                          ),
                      },
                  },
                  "required":["file_path"]
            },
        },
    },
]