#!/usr/bin/env python3
"""
从 Kaggle Superstore Management 数据集提取商品数据
生成 product 表 INSERT SQL
"""

import csv
import random
random.seed(42)

csv_path = r"C:\Users\LEGION\Desktop\论文\图\Superstore_Management_system.csv"

# 商品缓存: {product_name: (category, avg_price, avg_cost)}
products = {}

with open(csv_path, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        name = row["Product Name"].strip()
        cat = row["Category"].strip()
        price = float(row["Unit Price"]) / 100  # 单位分 → 元
        cost = float(row["Cost Price"]) / 100

        if name not in products:
            products[name] = {"cat": cat, "prices": [], "costs": []}
        products[name]["prices"].append(price)
        products[name]["costs"].append(cost)

print(f"CSV 读取完成: {sum(1 for _ in open(csv_path))} 行")
print(f"提取唯一商品: {len(products)} 个")

# ============ 类别映射 ============
CAT_MAP = {
    "Grocery": "食品杂货",
    "Electronics": "电子产品",
    "Furniture": "家具家居",
    "Office Supplies": "办公用品",
    "Clothing": "服装鞋帽",
    "Sports": "运动户外",
}

# ============ 生成 EAN-13 ============
def gen_ean13(seed):
    random.seed(seed)
    prefix = random.choice(["690", "691", "692", "693", "694", "695", "697"])
    body = "".join([str(random.randint(0, 9)) for _ in range(9)])
    odd = sum(int(body[i]) for i in range(0, 12, 2) if i < len(body)) + sum(int(prefix[i]) for i in range(0, 3, 2))
    # recalculate
    code12 = prefix + body
    odd = sum(int(code12[i]) for i in range(0, 12, 2))
    even = sum(int(code12[i]) for i in range(1, 12, 2))
    check = (10 - (odd + even * 3) % 10) % 10
    return code12 + str(check)

# ============ 生成 SQL ============
sql_path = r"C:\Users\LEGION\Desktop\陆铿全源码\连锁超市微服务管理系统\product_import_kaggle.sql"
count = 0

with open(sql_path, "w", encoding="utf-8") as f:
    f.write("-- ==========================================\n")
    f.write("-- 连锁超市商品数据 (来源: Kaggle Superstore Management)\n")
    f.write(f"-- 唯一商品数: {len(products)}\n")
    f.write("-- 用法: mysql -u root -p supermarket_product < product_import_kaggle.sql\n")
    f.write("-- ==========================================\n\n")

    for idx, (name, data) in enumerate(sorted(products.items())):
        avg_price = sum(data["prices"]) / len(data["prices"])
        cat_en = data["cat"]
        cat_zh = CAT_MAP.get(cat_en, cat_en)

        # 零售价取均价上浮10-30%
        retail = round(avg_price * random.uniform(1.1, 1.3), 2)
        if retail < 1.0:
            retail = round(avg_price + random.uniform(0.5, 3.0), 2)
        promo = round(retail * random.uniform(0.78, 0.92), 2)

        barcode = gen_ean13(idx + 10000)
        safe_name = name.replace("'", "''").replace('"', '""')

        f.write(
            f"INSERT INTO product (barcode, name, category, price, promo_price, is_local, store_id) "
            f"VALUES ('{barcode}', '{safe_name}', '{cat_zh}', "
            f"{retail}, {promo}, 0, NULL);\n"
        )
        count += 1

print(f"\nSQL 文件: {sql_path}")
print(f"商品总数: {count}\n")

# 统计分类
cats = {}
for data in products.values():
    c = CAT_MAP.get(data["cat"], data["cat"])
    cats[c] = cats.get(c, 0) + 1
for c, n in sorted(cats.items(), key=lambda x: -x[1]):
    print(f"  {c}: {n} 条")

print(f"\n前10条预览:")
for idx, (name, data) in enumerate(sorted(products.items())):
    if idx >= 10:
        break
    avg = sum(data["prices"]) / len(data["prices"])
    print(f"  {name:30s} | {CAT_MAP.get(data['cat'], data['cat']):8s} | ¥{avg:.2f}")
