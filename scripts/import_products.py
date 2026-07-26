#!/usr/bin/env python3
"""
从 Open Food Facts 下载真实商品数据，生成 product 表的 SQL 导入文件
目标: ~800 条连锁超市常见商品，含条形码、分类、价格
"""

import urllib.request
import json
import time
import random

# ============ 超市常见品类 ============
# Open Food Facts 分类名 → 中文分类 + 价格区间(RMB)
CATEGORIES = [
    # (OFF分类标签, 中文分类, 最低价, 最高价)
    ("beverages", "饮品", 2.5, 8.0),
    ("carbonated-drinks", "饮品", 2.5, 6.0),
    ("fruit-juices", "饮品", 3.0, 12.0),
    ("dairy", "乳制品", 3.0, 15.0),
    ("yogurts", "乳制品", 2.5, 10.0),
    ("cheeses", "乳制品", 8.0, 30.0),
    ("snacks", "零食", 2.0, 15.0),
    ("biscuits", "零食", 3.0, 12.0),
    ("chocolates", "零食", 5.0, 25.0),
    ("candies", "零食", 1.5, 8.0),
    ("cereals", "谷物早餐", 8.0, 25.0),
    ("breads", "烘焙面点", 3.0, 12.0),
    ("instant-noodles", "方便食品", 2.0, 8.0),
    ("canned-foods", "罐头食品", 3.0, 15.0),
    ("sauces", "调味品", 3.0, 15.0),
    ("cooking-oils", "调味品", 15.0, 50.0),
    ("frozen-foods", "冷冻食品", 5.0, 25.0),
    ("ice-creams", "冷冻食品", 3.0, 15.0),
    ("coffees", "饮品", 8.0, 40.0),
    ("teas", "饮品", 5.0, 30.0),
    ("waters", "饮品", 1.0, 3.0),
    ("pastas", "方便食品", 3.0, 12.0),
    ("rices", "主食粮谷", 10.0, 40.0),
    ("spices", "调味品", 3.0, 15.0),
    ("honeys", "调味品", 10.0, 30.0),
    ("jams", "调味品", 5.0, 15.0),
    ("breakfast-cereals", "谷物早餐", 8.0, 25.0),
    ("plant-based-foods", "方便食品", 5.0, 20.0),
    ("nuts", "零食", 8.0, 30.0),
    ("dried-fruits", "零食", 5.0, 20.0),
    ("crisps", "零食", 2.0, 8.0),
    ("baby-foods", "母婴用品", 15.0, 50.0),
    ("pet-foods", "宠物食品", 8.0, 40.0),
    ("toilet-papers", "纸品个护", 8.0, 25.0),
    ("shampoos", "纸品个护", 10.0, 40.0),
    ("soaps", "纸品个护", 3.0, 15.0),
    ("toothpastes", "纸品个护", 5.0, 20.0),
    ("cleaning-products", "家居清洁", 5.0, 25.0),
    ("beers", "饮品", 3.0, 10.0),
    ("wines", "饮品", 20.0, 80.0),
]

BASE_URL = "https://world.openfoodfacts.org/category/{category}.json?page={page}&page_size=50"
MAX_PER_CAT = 22  # 每个分类最多取22条 (38分类 * 22 ≈ 836条)

all_products = []
seen_barcodes = set()

print("=" * 50)
print("开始从 Open Food Facts 下载商品数据...")
print(f"目标: {len(CATEGORIES)} 个分类 × {MAX_PER_CAT} 条 ≈ {len(CATEGORIES) * MAX_PER_CAT} 条")
print("=" * 50)

for cat_en, cat_zh, price_min, price_max in CATEGORIES:
    cat_count = 0
    for page in range(1, 6):  # 最多翻5页
        if cat_count >= MAX_PER_CAT:
            break
        try:
            url = BASE_URL.format(category=cat_en, page=page)
            req = urllib.request.Request(url, headers={
                "User-Agent": "SupermarketThesis/1.0 (educational project; contact@example.com)"
            })
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            for p in data.get("products", []):
                if cat_count >= MAX_PER_CAT:
                    break

                barcode = p.get("code", "").strip()
                name = (p.get("product_name") or p.get("generic_name") or "").strip()
                if not name or not barcode or barcode in seen_barcodes:
                    continue
                # 过滤太长的名字
                if len(name) > 80:
                    name = name[:77] + "..."

                # 生成合理价格
                price = round(random.uniform(price_min, price_max), 2)

                seen_barcodes.add(barcode)
                all_products.append({
                    "barcode": barcode,
                    "name": name,
                    "category": cat_zh,
                    "price": price,
                    "promo_price": round(price * random.uniform(0.78, 0.92), 2),
                })
                cat_count += 1

            time.sleep(0.3)  # 礼貌限速

        except Exception as e:
            print(f"  ⚠ {cat_en} 第{page}页出错: {e}")
            time.sleep(1)
            continue

    print(f"  ✓ {cat_zh}({cat_en}): {cat_count} 条")

print(f"\n总计下载: {len(all_products)} 条商品")

# ============ 生成 SQL ============
sql_path = r"C:\Users\LEGION\Desktop\陆铿全源码\连锁超市微服务管理系统\product_import.sql"

with open(sql_path, "w", encoding="utf-8") as f:
    f.write("-- 连锁超市商品数据导入 (来源: Open Food Facts)\n")
    f.write("-- 生成时间: " + time.strftime("%Y-%m-%d %H:%M:%S") + "\n")
    f.write(f"-- 共 {len(all_products)} 条\n\n")
    f.write("-- 清空旧数据 (可选, 首次导入请取消注释)\n")
    f.write("-- TRUNCATE TABLE product;\n\n")

    for p in all_products:
        # 转义单引号
        safe_name = p["name"].replace("'", "''")
        sql = (
            f"INSERT INTO product (barcode, name, category, price, promo_price, is_local, store_id) "
            f"VALUES ('{p['barcode']}', '{safe_name}', '{p['category']}', "
            f"{p['price']}, {p['promo_price']}, 0, NULL);\n"
        )
        f.write(sql)

print(f"SQL 文件已保存: {sql_path}")
print("前 10 条预览:")
for p in all_products[:10]:
    print(f"  [{p['barcode']}] {p['name']} | {p['category']} | ¥{p['price']}")
