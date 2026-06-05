"""07——test——sampling.py - 验证大文件抽样"""

import json
import time
from tools import group_stats, column_stats,detect_anomalies

LARGE_FILE = "data/sales_large.csv"

print("="*60)
print("测试 1: group_stats 大文件(应触发抽样)")
print("="*60)
t = time.time()
result = group_stats(LARGE_FILE,"department","sales_amount","mean")
print(f"是否抽样:{result['sampling_info']['sampled']}")
print(f"原始行数:{result['sampling_info']['total_rows']:,}")
print(f"分析行数:{result['sampling_info']['analyzed_rows']:,}")
print(f"各部门均值:{result['results']}")

# ============================================================
# 测试 2: detect_anomalies 大文件(应全量,不抽样)
# ============================================================
print("\n" + "=" * 60)
print("测试 2: detect_anomalies 大文件(应全量分析)")
print("=" * 60)
t = time.time()
result = detect_anomalies(LARGE_FILE,"sales_amount")
print(f"耗时:{time.time() - t:.3f} 秒")
print(f"total_rows: {result['total_rows']:,}")
print(f"找到异常数: {result['total_anomalies']}")
print(f"(异常是每 25000 行 1 个 500 万，10 万行应有约 4 个)")
print(f"严重程度分布：{result['severity_summary']}")