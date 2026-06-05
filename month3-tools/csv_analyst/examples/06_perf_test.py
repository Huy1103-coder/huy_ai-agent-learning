import time
from tools import load_csv,filter_rows,column_stats,group_stats,detect_anomalies

FILE = "data/sales_large.csv"

print("="*60)
print("优化后的的性能测试)")
print("="* 60)

start = time.time()

t1 = time.time()
load_csv(FILE)
print(f"load_csv:   {time.time() - t1:.3f} 秒")

t2 = time.time()
filter_rows(FILE,{"department":"华南区"})
print(f"filter_rows:    {time.time() - t2:.3f} 秒")

t3 = time.time()
column_stats(FILE, "sale_amount")
print(f"group_stats:    {time.time() - t3:.3f} 秒")

t4 = time.time()
group_stats(FILE,"sales_amount","sum")
print(f"group——stats:    {time.time() - t4:.3f} 秒")

t5 = time.time()
detect_anomalies(FILE,"sales_amount")
print(f"detect_anomalies:    {time.time() - t5:.3f}秒")

total = time.time()
print("-"*60)
print(f"总耗时:    {total - start:.3f} 秒(使用了缓存)")