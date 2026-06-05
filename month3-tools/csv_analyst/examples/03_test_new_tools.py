"""03_test_new_tools.py - 验证 3 个新工具"""
import json
from tools import filter_rows, column_stats, group_stats

# ============================================================
# 测试 1: filter_rows
# ============================================================
print("="*60)
print("测试1：筛选杨帆8月数据")
print("="*60)
result = filter_rows("data/sales.csv",{"name":"杨帆","month":8})
print(json.dumps(result,ensure_ascii=False,indent=2))


# ============================================================
# 测试 2: filter_rows 数值范围
# ============================================================
print("\n" + "="*60)
print("测试2:筛选销售额超 50万的记录")
print("="*60)
result = filter_rows("data/sales.csv",{"sales_amount_min":500000})
print(json.dumps(result,ensure_ascii=False,indent=2))

# ============================================================
# 测试 3: column_stats 数值列
# ============================================================
print("\n" + "=" * 60)
print("测试 3:sales_amount 列深度统计")
print("=" *60)
result = column_stats("data/sales.csv","sales_amount")
print(json.dumps(result,ensure_ascii=False,indent=2))

# ============================================================
# 测试 4: column_stats 文本列
# ============================================================
print("\n" + "="*60)
print("测试4:department列(文本)统计")
print("="*60)
result  = column_stats("data/sales.csv","department")
print(json.dumps(result,ensure_ascii=False,indent=2))

# ============================================================
# 测试 4: column_stats 文本列
# ============================================================
print("\n" + "=" * 60)
print("测试 5:各部门销售总额")
print("=" * 60)
result = group_stats("data/sales.csv","department","sales_amount","sum")
print(json.dumps(result,ensure_ascii=False,indent=2))


# ============================================================
# 测试 6: group_stats 员工平均成交数
# ============================================================
print("\n" + "=" * 60)
print("测试 6:各员工平均成交数(前 5 名)")
print("="*60)
result = group_stats("data/sales.csv","name","deals_count","mean")
print(json.dumps(result,ensure_ascii=False,indent=2))