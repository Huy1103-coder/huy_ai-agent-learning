import json
from tools import detect_anomalies
print("="*60)
print("测试1： 检测sales_amount 列异常")

print("=" * 60)
print("测试1：检测sales_amount 列异常")
print("=" * 60)
result =detect_anomalies("data/sales.csv","sales_amount")
print(json.dumps(result,ensure_ascii=False, indent=2))


print("\n" + "=" * 60)
print("测试 2：检测deals_count 列（预期较少的异常）")
print("=" * 60)
result = detect_anomalies("data/sales.csv","deals_count")
print(json.dumps(result,ensure_ascii=False,indent= 2))

# ============================================================
# 测试 3: 检测文本列(应该返回 error)
# ============================================================
print("\n" + "="*60)
print("测试 3:文本列异常检测(应返回error)")
print("="*60)
result = detect_anomalies("data/sales.csv","name")
print(json.dumps(result,ensure_ascii=False,indent=2))





