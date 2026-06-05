"""
generate_large_data.py - 生成大测试数据(约 10 万行)
用于测试缓存和抽样功能。

运行: python examples/generate_large_data.py
"""

import csv
import random

random.seed(42)

names = ['张伟', '王芳', '李娜', '刘洋', '陈静', '杨帆', '黄磊', '周宇', '吴敏', '徐磊',
         '孙莉', '马超', '朱琳', '胡军', '郭涛', '何静', '高翔', '林森', '罗杰', '梁丽']
depts = ['华东区', '华北区', '华南区', '华中区']

with open('data/sasles_large.csv','w',encoding='utf-8-sig',newline= '') as f:
    w = csv.writer(f)
    w.writerow(['order_id','name','department','month','sales_amount','deals_count'])

    count = 0
    for year in range(5):
        for i in range(20):
            for month in range(1,13):
                for order in range(83):
                    count += 1
                    order_id = f"ORD{count:07d}"
                    name = names[i]
                    dept = depts[i % 4]
                    sales = random.randint(1000,50000)
                    deals = random.randint(1,10)
                    if count % 25000 == 0:
                        sales = 5000000 # 埋异常
                    w.writerow([order_id,name,dept,month,sales,deals])
                

print(f'✅ sales_large.csv 生成完成,{count} 行')