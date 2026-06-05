"""
02_test_tools.py - 临时验证 load_csv 工具

不是 Agent,只是直接调工具看输出。
"""
import json
from tools import load_csv

# ============================================================
# 测试 1:正常路径
# ============================================================

print("=" * 60)
print("测试 1: 正常加载 data/sales.csv")
print("=" * 60)
result = load_csv("data/sales.csv")
print(json.dumps(result,ensure_ascii=False,indent=2))


# ============================================================
# 测试 2:文件不存在
# ============================================================
print("\n"+"="*60)
print("测试 2： 文件不存在")
print("=" * 60)
result = load_csv("data/not_exist.csv")
print(json.dumps(result, ensure_ascii=False, indent=2))

# ============================================================
# 测试 3:传目录路径
# ============================================================
print("\n" + "=" * 60)
print("测试 3: 传目录路径")
print("=" * 60)
result = load_csv("data")
print(json.dumps(result, ensure_ascii=False, indent=2))


# ============================================================
# 测试 4:不是 csv 后缀
# ============================================================
print("\n" + "=" * 60)
print("测试 4: 不是 csv 后缀")
print("=" * 60)
result = load_csv("01_csv_basics.py")  # 这是个 py 文件
print(json.dumps(result, ensure_ascii=False, indent=2))