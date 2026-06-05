"""
test_tools.py - csv_analyst 工具的 pytest 测试套件

运行: pytest test_tools.py -v
"""

import os
import tempfile
import pytest
import pandas as pd

from tools import (
    load_csv,
    filter_rows,
    column_stats,
    group_stats,
    detect_anomalies,
)

@pytest.fixture
def normal_csv():
    content ="""name,department,sales_amount,deals_count
张三,华东,100000,20
李四,华东,120000,25
王五,华南,90000,18
赵六,华南,5000000,5
钱七,华北,80000,15
"""
    fd,path = tempfile.mkstemp(suffix=".csv")
    with os.fdopen(fd,"w",encoding="utf-8") as f:
        f.write(content)
    yield path
    os.remove(path)

@pytest.fixture
def empty_csv():

    content = "name,department,sales_amount\n"
    fd,path = tempfile.msktemp(suffix=".csv")
    with os.fdopen(fd,"w",encoding="utf-8") as f:
        f.write(content)
    yield path
    os.remove(path)


@pytest.fixture
def truly_empty_csv():
    """造一个完全空的CSV(连表头都没有)"""
    fd, path = tempfile.mkstemp(suffix=".csv") 
    with os.fdopen(fd,"w",encoding="utf-8") as f:
        f.write("")
    yield path
    os.remove(path)

# ============================================================
# load_csv 测试
# ============================================================

def test_load_csv_returns_dict(normal_csv):
    """工具永远返回 dict"""
    result = load_csv(normal_csv)
    assert isinstance(result,dict)

def test_load_csv_correct_row_count(normal_csv):
    """正确返回行数(5 行数据)"""
    result = load_csv(normal_csv)
    assert result["row_count"] == 5

def test_load_csv_correct_column_count(normal_csv):
    """正确返回列数(4 列)"""
    result = load_csv(normal_csv)
    assert result["column_count"] == 4

def test_load_csv_column_types_friendly(normal_csv):
    """列类型用友好名(text/integer,不是object/int64)"""
    result = load_csv(normal_csv)
    types = result["column_types"]
    assert types["name"] == "text"
    assert types["sales_amount"] == "integer"

def test_load_csv_file_not_found():
    """文件不存在返回 error,不崩溃"""
    result = load_csv("不存在的文件.csv")
    assert "error" in result

def test_load_csv_not_csv_extension():
    """非csv 后缀返回error"""
    result = load_csv("test_tools.py")
    assert "error" in result

def test_load_csv_truly_empty(truly_empty_csv):
    """完全空文件返回 error,不崩溃"""
    result = load_csv(truly_empty_csv)
    assert "error" in result

# ============================================================
# filter_rows 测试
# ============================================================

def test_filter_rows_exact_match(normal_csv):
    "精确匹配:华东部门有 2 人"
    result = filter_rows(normal_csv,{"department":"华东"})
    assert result["matched_count"] == 2


def test_filter_rows_numeric_min(normal_csv):
    """数值下限：销售额 >= 100000 有 3 人(10万/12万/500万)"""
    result = filter_rows(normal_csv,{"sales_amount_min":100000})
    assert result["matched_count"] == 3


def test_filter_rows_combined(normal_csv):
    """组合条件:=销售额 <= 90000 有 2 人(9万/8万)"""
    result = filter_rows(normal_csv,{"sales_amount_max":90000})
    assert result["matched_count"] == 2

def test_filter_rows_invalid(normal_csv):
    """组合条件:华南 + 销售额 >= 100000 有 1 人(赵六500万)"""
    result = filter_rows(normal_csv,{"department":"华南","sales_amount_min":100000})
    assert result["matched_count"] == 1

def test_filter_rows_invalid_column(normal_csv):
    result = filter_rows(normal_csv,{"不存在的列":"x"})
    assert "error" in result


def test_filter_rows_no_match(normal_csv):
    """无匹配返回0，不崩溃"""
    result = filter_rows(normal_csv,{"department":"火星区"})
    assert result["matched_count"] == 0

# ============================================================
# column_stats 测试
# ============================================================
def test_column_stats_numeric(normal_csv):
    """数值列返回 mean/median/std 等"""
    result = column_stats(normal_csv,"sales_amount")
    assert "mean" in result
    assert "median" in result
    assert "max" in result

def test_column_stats_text(normal_csv):
    """文本列返回 top_5_values"""
    result = column_stats(normal_csv,"department")
    assert "top_5_values" in result

def test_column_stats_unique_count(normal_csv):
    """department 有 3 个唯一值(华东/华南/华北)"""
    result = column_stats(normal_csv,"department")
    assert result["unique_count"] == 3

def test_column_stats_invalid_column(normal_csv):
    """不存在的列返回 error"""
    result = column_stats(normal_csv,"不存在")
    assert "error" in result

# ============================================================
# group_stats 测试
# ============================================================

def test_group_stats_sum(normal_csv):
    """华东总销售 = 100000 + 120000 = 220000"""
    result = group_stats(normal_csv,"department","sales_amount","sum")
    assert result["results"]["华东"] == 220000

def test_group_stats_count(normal_csv):
    """按部门 count:华东 2,华南 2,华北 1"""
    result = group_stats(normal_csv, "department", "sales_amount", "count")
    assert result["results"]["华东"] == 2
    assert result["results"]["华北"] == 1

def test_group_stats_invalid_func(normal_csv):
    """非法聚合函数返回 error"""
    result = group_stats(normal_csv,"department","sales_amount","average")
    assert "error" in result

def test_group_stats_text_agg_column(normal_csv):
    """对文本列做sum返回 error(count 除外)"""
    result = group_stats(normal_csv,"department","name","sum")
    assert "error" in result

# ============================================================
# detect_anomalies 测试(防 648 假阳性回归!)
# ============================================================

def test_group_stats_count(normal_csv):
    """按部门 count:华东 2,华南 2,华北 1"""
    result = group_stats(normal_csv, "department", "sales_amount", "count")
    assert result["results"]["华东"] == 2
    assert result["results"]["华北"] == 1

def test_detect_anomalies_text_column(normal_csv):

    result = detect_anomalies(normal_csv,"name")
    assert "error" in result

def test_detect_anomalies_finds_extreme(normal_csv):
    """500 万那条必须被检测为极端异常(守护召回率)"""
    result = detect_anomalies(normal_csv, "sales_amount")
    # 赵六 500 万是极端异常,extreme_count 至少 1
    high_conf =(
        result["severity_summary"]["extreme_count"]
        + result["severity_summary"]["severe_count"]
    )
    assert high_conf >= 1,f"500万应被检测为异常，实际 severity_summary={result['severity_summary']}"


def test_detect_anomalies_total_is_high_confidence(normal_csv):
    """
     total_anomalies 只统计高置信度(2+ 票),不含 mild
     主要进行BUG的固定,每修理一个BUG,就要写一个测试,防止死灰复燃   
    """
    result = detect_anomalies(normal_csv,"sales_amount")
    
    result = detect_anomalies(normal_csv, "sales_amount")
    # total_anomalies 应该是高置信度的,等于 extreme + severe + moderate
    high_conf = (
        result["severity_summary"]["extreme_count"]
        + result["severity_summary"]["severe_count"]
        + result["severity_summary"]["moderate_count"]
    )
    assert result["total_anomalies"] == high_conf

