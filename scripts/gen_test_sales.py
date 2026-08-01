"""
生成 14 天多维度测试销售数据 — 用于补货算法消融实验
模拟真实超市场景：快消品高频、慢消品低频、周末高峰、突发爆量
"""
import subprocess, random, math
from datetime import datetime, timedelta

def mysql(query):
    cmd = ['docker', 'exec', '-i', 'supermarket-mysql',
           'mysql', '-uroot', '-p123456', '-h127.0.0.1', '-N', '-B', '-e', query]
    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out = r.stdout.decode().strip()
    return [l.split('\t') for l in out.split('\n') if l]

products = mysql("SELECT id, name, price, category FROM supermarket_product.product ORDER BY id")
print(f"产品数: {len(products)}")

prods = [(int(p[0]), p[1], float(p[2]), p[3]) for p in products]
n = len(prods)

random.seed(42)
now = datetime.now()
order_id = 3000
item_id = 5000
all_sql = []

# 产品分组（按索引%n循环利用）
fast_movers  = [i for i in range(n) if i % 5 == 0]      # 每天卖
mid_freq     = [i for i in range(n) if i % 5 == 1]      # 隔天卖
weekenders   = [i for i in range(n) if i % 5 == 2]      # 周末型
slow_movers  = [i for i in range(n) if i % 5 == 3]      # 偶尔卖
burst_items  = [i for i in range(n) if i % 5 == 4]      # 突发型

for day_offset in range(14):
    day = now - timedelta(days=day_offset)
    is_weekend = (day.weekday() >= 5)

    for store in [1, 2, 3]:
        # 快消品：天天卖，每天 3-5 笔
        for _ in range(random.randint(3, 5)):
            idx = random.choice(fast_movers)
            pid, name, price, cat = prods[idx]
            qty = random.randint(1, 5) * (2 if is_weekend else 1)
            items = [(item_id, order_id, pid, price, qty)]
            total = price * qty
            ot = day.replace(hour=random.randint(8,21), minute=random.randint(0,59)).strftime('%Y-%m-%d %H:%M:%S')
            no = f"T{day.strftime('%m%d')}{order_id:05d}"
            all_sql.append(f"INSERT INTO supermarket_order.`order` (id,order_no,store_id,total_price,points,create_time) VALUES({order_id},'{no}',{store},{total:.0f},0,'{ot}');")
            for iid, oid, ipid, ipr, iqt in items:
                all_sql.append(f"INSERT INTO supermarket_order.order_item (id,order_id,product_id,price,quantity) VALUES({iid},{oid},{ipid},{ipr},{iqt});")
            order_id += 1; item_id += 1

        # 周末型：仅周末大卖
        if is_weekend and random.random() < 0.8:
            for _ in range(random.randint(1, 3)):
                idx = random.choice(weekenders)
                pid, name, price, cat = prods[idx]
                qty = random.randint(3, 10)
                items = [(item_id, order_id, pid, price, qty)]
                total = price * qty
                ot = day.replace(hour=random.randint(8,21), minute=random.randint(0,59)).strftime('%Y-%m-%d %H:%M:%S')
                no = f"T{day.strftime('%m%d')}{order_id:05d}"
                all_sql.append(f"INSERT INTO supermarket_order.`order` (id,order_no,store_id,total_price,points,create_time) VALUES({order_id},'{no}',{store},{total:.0f},0,'{ot}');")
                for iid, oid, ipid, ipr, iqt in items:
                    all_sql.append(f"INSERT INTO supermarket_order.order_item (id,order_id,product_id,price,quantity) VALUES({iid},{oid},{ipid},{ipr},{iqt});")
                order_id += 1; item_id += 1

        # 中频型
        if random.random() < 0.4:
            idx = random.choice(mid_freq)
            pid, name, price, cat = prods[idx]
            qty = random.randint(1, 3)
            items = [(item_id, order_id, pid, price, qty)]
            total = price * qty
            ot = day.replace(hour=random.randint(8,21), minute=random.randint(0,59)).strftime('%Y-%m-%d %H:%M:%S')
            no = f"T{day.strftime('%m%d')}{order_id:05d}"
            all_sql.append(f"INSERT INTO supermarket_order.`order` (id,order_no,store_id,total_price,points,create_time) VALUES({order_id},'{no}',{store},{total:.0f},0,'{ot}');")
            for iid, oid, ipid, ipr, iqt in items:
                all_sql.append(f"INSERT INTO supermarket_order.order_item (id,order_id,product_id,price,quantity) VALUES({iid},{oid},{ipid},{ipr},{iqt});")
            order_id += 1; item_id += 1

        # 慢消型：14天内仅 2-3 天
        if day_offset in [0, 5, 11] and random.random() < 0.5:
            idx = random.choice(slow_movers)
            pid, name, price, cat = prods[idx]
            qty = random.randint(1, 2)
            items = [(item_id, order_id, pid, price, qty)]
            total = price * qty
            ot = day.replace(hour=random.randint(8,21), minute=random.randint(0,59)).strftime('%Y-%m-%d %H:%M:%S')
            no = f"T{day.strftime('%m%d')}{order_id:05d}"
            all_sql.append(f"INSERT INTO supermarket_order.`order` (id,order_no,store_id,total_price,points,create_time) VALUES({order_id},'{no}',{store},{total:.0f},0,'{ot}');")
            for iid, oid, ipid, ipr, iqt in items:
                all_sql.append(f"INSERT INTO supermarket_order.order_item (id,order_id,product_id,price,quantity) VALUES({iid},{oid},{ipid},{ipr},{iqt});")
            order_id += 1; item_id += 1

        # 突发爆量：某一天大量
        if day_offset == 3 and random.random() < 0.7:
            idx = random.choice(burst_items)
            pid, name, price, cat = prods[idx]
            qty = random.randint(15, 40)
            items = [(item_id, order_id, pid, price, qty)]
            total = price * qty
            ot = day.replace(hour=random.randint(8,21), minute=random.randint(0,59)).strftime('%Y-%m-%d %H:%M:%S')
            no = f"T{day.strftime('%m%d')}{order_id:05d}"
            all_sql.append(f"INSERT INTO supermarket_order.`order` (id,order_no,store_id,total_price,points,create_time) VALUES({order_id},'{no}',{store},{total:.0f},0,'{ot}');")
            for iid, oid, ipid, ipr, iqt in items:
                all_sql.append(f"INSERT INTO supermarket_order.order_item (id,order_id,product_id,price,quantity) VALUES({iid},{oid},{ipid},{ipr},{iqt});")
            order_id += 1; item_id += 1

# 批量导入
print(f"生成 {len(all_sql)} 条 SQL，写入中...")
batch_size = 50
for start in range(0, len(all_sql), batch_size):
    batch = '\n'.join(all_sql[start:start+batch_size])
    r = subprocess.run(
        ['docker', 'exec', '-i', 'supermarket-mysql', 'mysql', '-uroot', '-p123456', '-h127.0.0.1'],
        input=batch.encode(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if r.returncode != 0:
        err = r.stderr.decode()[:200]
        if 'Duplicate' not in err:
            print(f"错误: {err}")
            break

# 更新 product_sales
mysql("DELETE FROM supermarket_order.product_sales;")
mysql("""
    INSERT INTO supermarket_order.product_sales (store_id, product_id, total_quantity)
    SELECT o.store_id, oi.product_id, SUM(oi.quantity)
    FROM supermarket_order.order_item oi
    JOIN supermarket_order.`order` o ON oi.order_id = o.id
    GROUP BY o.store_id, oi.product_id;
""")

orders = mysql("SELECT COUNT(*) FROM supermarket_order.`order` WHERE order_no LIKE 'T%'")
items = mysql("SELECT COUNT(*) FROM supermarket_order.order_item WHERE id >= 5000")
print(f"导入完成: {orders[0][0]} 笔测试订单, {items[0][0]} 条测试明细")

# --- 重置所有库存为 200（统一基线），然后压低有销售的商品库存 ---
print("重置库存为 200...")
mysql("UPDATE supermarket_inventory.inventory SET stock=200, warning_stock=10")

print("压低有销售的商品库存，制造补货需求...")
mysql("""
    UPDATE supermarket_inventory.inventory i
    JOIN (
        SELECT oi.product_id, o.store_id, SUM(oi.quantity) AS sold
        FROM supermarket_order.order_item oi
        JOIN supermarket_order.`order` o ON oi.order_id = o.id
        WHERE o.create_time >= DATE_SUB(NOW(), INTERVAL 14 DAY)
        GROUP BY oi.product_id, o.store_id
    ) s ON i.product_id = s.product_id AND i.store_id = s.store_id
    SET i.stock = FLOOR(RAND() * 12) + 1
""")
low = mysql("SELECT COUNT(*) FROM supermarket_inventory.inventory WHERE stock < warning_stock")
print(f"低库存商品: {low[0][0]} 件（stock < 10）")
print("可运行 python3 scripts/ablation_test.py 进行消融实验")
