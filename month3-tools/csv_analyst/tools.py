"""
tools.py - CSV 数据分析 Agent 的工具集

工具契约(继承自 Week 2 outdoor_advisor):
- 失败返回 {"error": "..."},不抛异常
- 字段名清晰带语义后缀
- 数值格式化为"人类可读",不返回科学计数法
"""

import pandas as pd
from pathlib import Path

# ============================================================
# DType 适配层
# 屏蔽 pandas 1.x ('object') 和 2.x ('str') 的差异
# 给 LLM 提供统一、人类友好的类型名
# ============================================================

DTYPE_FRIENDLY = {
    # 文本类型
    "object": "text",
    "str": "text",
    "string": "text",
    
    # 整数
    "int64": "integer",
    "int32": "integer",
    "Int64": "integer",     # pandas 可空整数
    
    # 浮点
    "float64": "decimal",
    "float32": "decimal",
    
    # 布尔
    "bool": "boolean",
    "boolean": "boolean",
    
    # 时间
    "datetime64[ns]": "datetime",
    "datetime64[us]": "datetime",
}


def _friendly_dtype(dtype) -> str:
    """
    把 pandas 原始 dtype 翻译成人类友好的名字。
    
    跨 pandas 版本一致:
    - pandas 1.x 的 'object' → 'text'
    - pandas 2.x 的 'str'    → 'text'
    
    未知类型不翻译,原样返回(保留诊断信息)。
    """
    raw = str(dtype)
    return DTYPE_FRIENDLY.get(raw, raw)

def _format_describe(df: pd.DataFrame) -> dict:
    """
    格式化 describe() 输出,
    把 pandas 的科学计数法 (1.5e+06) 转成普通浮点数 (1500000.0)。
    
    这样 LLM 拿到的数字是"无歧义"的。
    """
    desc = df.describe()
    result = {}
    for col in desc.columns:
        result[col] ={stat:round(float(value),2) for stat,value in desc[col].items() }
        
    return result

# ============================================================
# 工具 1:加载 CSV + 返回摘要(不返回完整数据!)
# ============================================================
def load_csv(file_path:str) -> dict:
    """
    加载 CSV 文件,返回数据摘要给 LLM。
    
    返回内容:
    - 文件基本信息(路径、行数、列数)
    - 列名 + 列类型
    - 前 5 行预览
    - 数值列的描述性统计(count / mean / std / min / 25% / 50% / 75% / max)
    """
    # ---- Step 1: 路径合法性检查(防御式编程) ----
    path =Path(file_path)

    if not path.exists():
        return {"error":f"文件不存在：{file_path}"}
    

    if not path.is_file():
        return {"error":f"路径不是文件(可能时目录):{file_path}"}
    
    if path.suffix.lower() != ".csv":
        return {"error":f"不是csv文件：{file_path}(后缀必须是 .csv)"}
    #捕捉问题，文件路径是否存在，存在是否为文件，文件是否为csv
    
    # ---- Step 2: 尝试加载 CSV ----
    try:
        df = pd.read_csv(file_path)
    except pd.errors.EmptyDataError:
        return {"error":"CSV 文件夹是空的（没有任何内容）"}
    except pd.errors.ParserError as e:
        return {"error":f"CSV格式错误{e}"}
    except UnicodeDecodeError:
        return {"error":"文件编码不是 UTF-8，请重新保存为UTF-8格式"}
    except Exception as e:
        return {"error":f"加载失败：{type(e).__name__}:{e}"}
    #将错误分三层，第一层文件是否为空的，格式是否正确，编码是否为UTF-8

    # ---- Step 3: 检查空数据(文件存在但没有数据行) ----
    if df.empty:
        return {"error":"CSV 没有数据行（只有列头或完全为空）"}
    
    # ---- Step 4: 组装返回结果 ----
    return {
        "file_path":str(path),
        "row_count":int(df.shape[0]),
        "column_count":int(df.shape[1]),
        "column_names":df.columns.tolist(),
        "column_types":{col:_friendly_dtype(df[col].dtype) for col in df.columns},
        "preview_first_5":df.head(5).to_dict(orient="records"),
        #to_dict(orient="records") 把 DataFrame 转成 每行一个 dict 的列表，可读性更高
        "numeric_summary":_format_describe(df),
       
    }
"""
        返回给大模型的内容：文件路径，列数，行数；列名，列数据类型；前五行预览，格式化数据样本（精确后的样子）
"""

# ============================================================
# 工具路由表
# ============================================================

TOOL_MAP = {
    "load_csv":load_csv
}