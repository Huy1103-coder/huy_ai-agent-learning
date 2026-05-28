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
# 工具 2: filter_rows —— 条件筛选
# ============================================================

def filter_rows(file_path: str, conditions: dict, max_rows: int = 50) -> dict:
    """
    按条件筛选 CSV 行。
    
    Args:
        file_path: CSV 文件路径
        conditions: 筛选条件字典,支持:
            - 精确匹配: {"name": "杨帆"} → name == "杨帆"
            - 数值范围: {"sales_amount_min": 100000} → sales_amount >= 100000
            - 数值范围: {"sales_amount_max": 50000} → sales_amount <= 50000
        max_rows: 最多返回多少行(防止上下文爆炸,默认 50)
    
    Returns:
        筛选结果摘要 + 前 max_rows 条数据
    """
    # 复用 load_csv 的路径检查
    path = Path(file_path)
    if not path.exists():
        return {"error": f"文件不存在: {file_path}"}
    if not path.is_file() or path.suffix.lower() != ".csv":
        return {"error": f"不是有效的 CSV 文件: {file_path}"}
    
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        return {"error": f"加载失败: {type(e).__name__}: {e}"}
    
    if df.empty:
        return {"error": "CSV 没有数据"}
    
    # ---- 应用筛选条件 ----
    mask = pd.Series([True] * len(df))  # 初始全选
    applied_conditions = []
    
    for key, value in conditions.items():
        if key.endswith("_min"):
            col = key[:-4]  # 去掉 _min 后缀
            if col not in df.columns:
                return {"error": f"列名不存在: {col}"}
            mask &= df[col] >= value
            applied_conditions.append(f"{col} >= {value}")
        elif key.endswith("_max"):
            col = key[:-4]
            if col not in df.columns:
                return {"error": f"列名不存在: {col}"}
            mask &= df[col] <= value
            applied_conditions.append(f"{col} <= {value}")
        else:
            # 精确匹配
            if key not in df.columns:
                return {"error": f"列名不存在: {key}"}
            mask &= df[key] == value
            applied_conditions.append(f"{key} == {value}")
    
    filtered = df[mask]
    
    # ---- 组装返回 ----
    truncated = len(filtered) > max_rows
    return {
        "file_path": str(path),
        "applied_conditions": applied_conditions,
        "matched_count": int(len(filtered)),
        "total_count": int(len(df)),
        "truncated": truncated,
        "shown_rows": min(len(filtered), max_rows),
        "data": filtered.head(max_rows).to_dict(orient="records"),
    }


# ============================================================
# 工具 3: column_stats —— 单列深度统计
# ============================================================

def column_stats(file_path: str, column: str, top_n: int = 5) -> dict:
    """
    单列的深度统计分析,超出 describe() 范围。
    
    Args:
        file_path: CSV 文件路径
        column: 列名
        top_n: 返回最大/最小的 N 个值(默认 5)
    
    Returns:
        - 基本统计(count / mean / median / std / min / max)
        - 数据质量(missing_count / unique_count)
        - 极值(top_n_max / bottom_n_min)
        - 异常判定(IQR 上下界 + outlier_count)
    """
    path = Path(file_path)
    if not path.exists():
        return {"error": f"文件不存在: {file_path}"}
    
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        return {"error": f"加载失败: {type(e).__name__}: {e}"}
    
    if column not in df.columns:
        return {"error": f"列名不存在: {column}。可用列: {df.columns.tolist()}"}
    
    col_data = df[column]
    is_numeric = pd.api.types.is_numeric_dtype(col_data)
    
    # ---- 通用统计(所有类型都有) ----
    result = {
        "column": column,
        "dtype": _friendly_dtype(col_data.dtype),
        "total_count": int(len(col_data)),
        "missing_count": int(col_data.isna().sum()),
        "unique_count": int(col_data.nunique()),
    }
    
    if is_numeric:
        # ---- 数值列的深度统计 ----
        result.update({
            "mean": round(float(col_data.mean()), 2),
            "median": round(float(col_data.median()), 2),
            "std": round(float(col_data.std()), 2),
            "min": round(float(col_data.min()), 2),
            "max": round(float(col_data.max()), 2),
            "q25": round(float(col_data.quantile(0.25)), 2),
            "q75": round(float(col_data.quantile(0.75)), 2),
        })
        
        # ---- 极值 top_n / bottom_n ----
        result[f"top_{top_n}_max"] = [
            round(float(v), 2) for v in col_data.nlargest(top_n).tolist()
        ]
        result[f"bottom_{top_n}_min"] = [
            round(float(v), 2) for v in col_data.nsmallest(top_n).tolist()
        ]
        
        # ---- IQR 异常判定 ----
        iqr = result["q75"] - result["q25"]
        upper_bound = result["q75"] + 1.5 * iqr
        lower_bound = result["q25"] - 1.5 * iqr
        outliers = col_data[(col_data > upper_bound) | (col_data < lower_bound)]
        result["iqr"] = round(iqr, 2)
        result["upper_bound"] = round(upper_bound, 2)
        result["lower_bound"] = round(lower_bound, 2)
        result["outlier_count"] = int(len(outliers))
    else:
        # ---- 文本列的深度统计 ----
        value_counts = col_data.value_counts()
        result["top_5_values"] = {
            str(k): int(v) for k, v in value_counts.head(5).items()
        }
    
    return result


# ============================================================
# 工具 4: group_stats —— 分组聚合
# ============================================================

def group_stats(
    file_path: str,
    group_by: str,
    agg_column: str,
    agg_func: str = "sum",
) -> dict:
    """
    按某列分组,对另一列做聚合统计。
    
    Args:
        file_path: CSV 文件路径
        group_by: 分组列(如 "department" / "name")
        agg_column: 聚合列(必须是数值列,如 "sales_amount")
        agg_func: 聚合函数,支持 "sum" / "mean" / "median" / "max" / "min" / "count"
    
    Returns:
        分组结果(按聚合值降序),包含每组的统计值
    """
    path = Path(file_path)
    if not path.exists():
        return {"error": f"文件不存在: {file_path}"}
    
    # 验证聚合函数
    valid_funcs = {"sum", "mean", "median", "max", "min", "count"}
    if agg_func not in valid_funcs:
        return {"error": f"不支持的聚合函数: {agg_func}。支持: {sorted(valid_funcs)}"}
    
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        return {"error": f"加载失败: {type(e).__name__}: {e}"}
    
    if group_by not in df.columns:
        return {"error": f"分组列不存在: {group_by}。可用列: {df.columns.tolist()}"}
    if agg_column not in df.columns:
        return {"error": f"聚合列不存在: {agg_column}。可用列: {df.columns.tolist()}"}
    
    # count 函数允许任何列;其他函数需要数值列
    if agg_func != "count" and not pd.api.types.is_numeric_dtype(df[agg_column]):
        return {"error": f"聚合列 '{agg_column}' 不是数值类型,无法用 {agg_func} 聚合"}
    
    # ---- 执行分组聚合 ----
    try:
        grouped = df.groupby(group_by)[agg_column].agg(agg_func)
    except Exception as e:
        return {"error": f"分组失败: {type(e).__name__}: {e}"}
    
    # ---- 按聚合值降序排列,转 dict ----
    grouped_sorted = grouped.sort_values(ascending=False)
    result_dict = {
        str(k): round(float(v), 2) for k, v in grouped_sorted.items()
    }
    
    return {
        "file_path": str(path),
        "group_by": group_by,
        "agg_column": agg_column,
        "agg_func": agg_func,
        "group_count": len(result_dict),
        "results": result_dict,
    }

# ============================================================
# 工具 5: detect_anomalies —— 异常检测工具
# ============================================================

def _detect_outliers_iqr(values: pd.Series) -> pd.Series:
    q1 = values.quantile(0.25)
    q3 = values.quantile(0.75)
    iqr = q3-q1
    upper = q3+ 1.5*iqr
    lower = q1 - 1.5*iqr
    return (values < lower) | (values >upper)

def _detect_outliners_zscore(values:pd.Series,threshold: float = 3.0) -> pd.Series:
    mean = values.mean()
    std = values.std()
    if std == 0:
        return pd.Series([False] * len(values),index = values.index)
    z = (values -mean) / std
    return z.abs() > threshold

def _detect_outliers_modified_zscore(values: pd.Series,threshold : float = 3.5) -> pd.Series:

    median = values.median()
    mad = (values - median).abs().median()
    if mad == 0:
        return pd.Series([False]+ len(values),index = values.index)
    modified_z = 0.6745 * (values - median) / mad
    return modified_z.abs() > threshold

def _detect_outliers_business_rule(values:pd.Series) -> pd.Series:

    if (values < 0).any():

        return pd.Series([False] * len(values),index=values.index)
    q25 = values.quantile(0.25)
    q75 = values.quantile(0.75)

    too_low = values < (q25/10) if q25 > 0 else pd.Series([False] * len(values), index=values.index)
    too_high = values > (q75 * 5) if q75 >0 else pd.Series([False] * len(values),index = values.index) 
    return too_high | too_low


def detect_anomalies(
        file_path: str,
        column:str,
        max_anomalies: int = 20,
) -> dict:
    path = Path(file_path)
    if not path.exists():
        return {"error":f"文件不存在:{file_path}"}
    
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        return {"error":f"加载失败：{type(e).__name__}:{e}"}
    
    if column not in df.columns:
        return {"error":f"列名不存在：{column}。可用列：{df.columns.tolist()}"}

    if not pd.api.types.is_numeric_dtype(df[column]):
        return {"error":f"列 '{column}' 不是数值类型，无法检测异常"}

    values = df[column]

    if len(values) < 4:
        return {"error":"数据少于4 行，无法可靠检测异常"}
     
    outlier_iqr = _detect_outliers_iqr(values)
    outlier_zscore = _detect_outliners_zscore(values)
    outlier_mod_z = _detect_outliers_modified_zscore(values)
    outlier_business = _detect_outliers_business_rule(values)

    vote_count = (
            outlier_iqr.astype(int) +
            outlier_zscore.astype(int) +
            outlier_mod_z.astype(int) +
            outlier_business.astype(int) 
    )

    severity_map ={
        4:"极端异常",
        3:"严重异常",
        2:"中度异常",
        1:"轻度异常",
        0:"正常",
    }

    anomaly_mask = vote_count > 0
    anomaly_indices = vote_count[anomaly_mask].sort_values(ascending=False).index

    top_anomalies = anomaly_indices[:max_anomalies]

    anomaly_data =[]
    for idx in top_anomalies:
        row = df.loc[idx].to_dict()

        clean_row ={
            k: (int(v) if isinstance(v, (int,)) else
                float(v) if pd.api.types.is_number(v) and not isinstance(v, bool) else
                str(v))
            for k,v in row.items()
        }
        clean_row["_severity"] = severity_map[int(vote_count[idx])]
        clean_row["_methods_flagged"] = int(vote_count[idx])
        anomaly_data.append(clean_row)
    
    
    return {
        "file_path": str(path),
        "column": column,
        "total_rows": int(len(df)),
        "method_results": {
            "iqr_count": int(outlier_iqr.sum()),
            "zscore_count": int(outlier_zscore.sum()),
            "modified_zscore_count": int(outlier_mod_z.sum()),
            "business_rule_count": int(outlier_business.sum()),
        },
        "severity_summary": {
            "extreme_count": int((vote_count == 4).sum()),
            "severe_count": int((vote_count == 3).sum()),
            "moderate_count": int((vote_count == 2).sum()),
            "mild_count": int((vote_count == 1).sum()),
        },
        "total_anomalies": int(anomaly_mask.sum()),
        "shown_count": len(anomaly_data),
        "truncated": int(anomaly_mask.sum()) > max_anomalies,
        "anomalies": anomaly_data,
     }

# ============================================================
# 工具路由表
# ============================================================

TOOL_MAP = {
    "load_csv": load_csv,
    "filter_rows": filter_rows,
    "column_stats": column_stats,
    "group_stats": group_stats,
    "detect_anomalies": detect_anomalies,   
}