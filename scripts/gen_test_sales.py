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

products = mysql("SELECT id, name, price, category FROM supermarket_product.product ORDER BY id LIMIT 50")
print(f"选前 50 个产品生成测试数据")

prods = [(int(p[0]), p[1], float(p[2]), p[3]) for p in products]

random.seed(42)
now = datetime.now()
order_id = 3000
item_id = 5000
all_sql = []

# 产品角色分配（索引 0-49）
fast_movers  = [0,1,2,3,4]              # 每天都有销售（可乐、雪碧等）
weekenders   = [5,6,7,8,9]              # 周末高峰型（零食、冰淇淋）
mid_freq     = [10,11,12,13,14,15]      # 3-4天/周
slow_movers  = [16,17,18,19,20,21]      # 1-2天/14天
big_basket   = [22,23,24,25]            # 大量购买（整箱/家庭装）→ K_i 高
small_basket = [26,27,28,29,30]         # 少量多次（口香糖/小零食）→ K_i 低
burst_items  = [31,32,33]               # 某天突然爆发

for day_offset in range(14):
    day = now - timedelta(days=day_offset)
    is_weekend = (day.weekday() >= 5)
    day_factor = 1.5 if is_weekend else 1.0

    for store in [1, 2, 3]:
        store_factor = random.uniform(0.8, 1.2)

        # --- 快消品：天天卖，每天 2-4 笔 ---
        if random.random() < 0.95:
            for _ in range(random.randint(2, 4)):
                idx = random.choice(fast_movers)
                pid, name, price, cat = prods[idx]
                qty = round(random.randint(1, 3) * day_factor * store_factor)
                if qty < 1: continue
                items = [(item_id + len(all_sql), order_id, pid, price, qty)]
                total = price * qty
                ot = day.replace(hour=random.randint(8,21), minute=random.randint(0,59)).strftime('%Y-%m-%d %H:%M:%S')
                no = f"T{day.strftime('%m%d')}{order_id:05d}"
                all_sql.append(f"INSERT INTO supermarket_order.`order` (id,order_no,store_id,total_price,points,create_time) VALUES({order_id},'{no}',{store},{total:.0f},0,'{ot}');")
                for iid, oid, ipid, ipr, iqt in items:
                    all_sql.append(f"INSERT INTO supermarket_order.order_item (id,order_id,product_id,price,quantity) VALUES({iid},{oid},{ipid},{ipr},{iqt});")
                order_id += 1
                item_id += len(items)

        # --- 周末型：仅周末大量销售 ---
        if is_weekend and random.random() < 0.8:
            for _ in range(random.randint(1, 3)):
                idx = random.choice(weekenders)
                pid, name, price, cat = prods[idx]
                qty = random.randint(3, 8)
                items = [(item_id + len(all_sql), order_id, pid, price, qty)]
                total = price * qty
                ot = day.replace(hour=random.randint(8,21), minute=random.randint(0,59)).strftime('%Y-%m-%d %H:%M:%S')
                no = f"T{day.strftime('%m%d')}{order_id:05d}"
                all_sql.append(f"INSERT INTO supermarket_order.`order` (id,order_no,store_id,total_price,points,create_time) VALUES({order_id},'{no}',{store},{total:.0f},0,'{ot}');")
                for iid, oid, ipid, ipr, iqt in items:
                    all_sql.append(f"INSERT INTO supermarket_order.order_item (id,order_id,product_id,price,quantity) VALUES({iid},{oid},{ipid},{ipr},{iqt});")
                order_id += 1
                item_id += len(items)

        # --- 中频型：每周 3-4 天 ---
        if random.random() < 0.35:
            idx = random.choice(mid_freq)
            pid, name, price, cat = prods[idx]
            qty = round(random.randint(1, 4) * day_factor * store_factor)
            if qty < 1: continue
            items = [(item_id + len(all_sql), order_id, pid, price, qty)]
            total = price * qty
            ot = day.replace(hour=random.randint(8,21), minute=random.randint(0,59)).strftime('%Y-%m-%d %H:%M:%S')
            no = f"T{day.strftime('%m%d')}{order_id:05d}"
            all_sql.append(f"INSERT INTO supermarket_order.`order` (id,order_no,store_id,total_price,points,create_time) VALUES({order_id},'{no}',{store},{total:.0f},0,'{ot}');")
            for iid, oid, ipid, ipr, iqt in items:
                all_sql.append(f"INSERT INTO supermarket_order.order_item (id,order_id,product_id,price,quantity) VALUES({iid},{oid},{ipid},{ipr},{iqt});")
            order_id += 1
            item_id += len(items)

        # --- 慢消型：14天中仅 1-3 天 ---
        if day_offset in [0, 5, 11] and random.random() < 0.6:
            idx = random.choice(slow_movers)
            pid, name, price, cat = prods[idx]
            qty = random.randint(1, 2)
            items = [(item_id + len(all_sql), order_id, pid, price, qty)]
            total = price * qty
            ot = day.replace(hour=random.randint(8,21), minute=random.randint(0,59)).strftime('%Y-%m-%d %H:%M:%S')
            no = f"T{day.strftime('%m%d')}{order_id:05d}"
            all_sql.append(f"INSERT INTO supermarket_order.`order` (id,order_no,store_id,total_price,points,create_time) VALUES({order_id},'{no}',{store},{total:.0f},0,'{ot}');")
            for iid, oid, ipid, ipr, iqt in items:
                all_sql.append(f"INSERT INTO supermarket_order.order_item (id,order_id,product_id,price,quantity) VALUES({iid},{oid},{ipid},{ipr},{iqt});")
            order_id += 1
            item_id += len(items)

        # --- 大单型：单次买巨量（低 K_i）---
        if random.random() < 0.15:
            idx = random.choice(big_basket)
            pid, name, price, cat = prods[idx]
            qty = random.randint(8, 15)
            items = [(item_id + len(all_sql), order_id, pid, price, qty)]
            total = price * qty
            ot = day.replace(hour=random.randint(8,21), minute=random.randint(0,59)).strftime('%Y-%m-%d %H:%M:%S')
            no = f"T{day.strftime('%m%d')}{order_id:05d}"
            all_sql.append(f"INSERT INTO supermarket_order.`order` (id,order_no,store_id,total_price,points,create_time) VALUES({order_id},'{no}',{store},{total:.0f},0,'{ot}');")
            for iid, oid, ipid, ipr, iqt in items:
                all_sql.append(f"INSERT INTO supermarket_order.order_item (id,order_id,product_id,price,quantity) VALUES({iid},{oid},{ipid},{ipr},{iqt});")
            order_id += 1
            item_id += len(items)

        # --- 小单型：少量多次（高 K_i）---
        if random.random() < 0.25:
            idx = random.choice(small_basket)
            pid, name, price, cat = prods[idx]
            qty = random.randint(1, 2)
            items = [(item_id + len(all_sql), order_id, pid, price, qty)]
            total = price * qty
            ot = day.replace(hour=random.randint(8,21), minute=random.randint(0,59)).strftime('%Y-%m-%d %H:%M:%S')
            no = f"T{day.strftime('%m%d')}{order_id:05d}"
            all_sql.append(f"INSERT INTO supermarket_order.`order` (id,order_no,store_id,total_price,points,create_time) VALUES({order_id},'{no}',{store},{total:.0f},0,'{ot}');")
            for iid, oid, ipid, ipr, iqt in items:
                all_sql.append(f"INSERT INTO supermarket_order.order_item (id,order_id,product_id,price,quantity) VALUES({iid},{oid},{ipid},{ipr},{iqt});")
            order_id += 1
            item_id += len(items)

        # --- 突发爆量：某一天突然卖很多 ---
        if day_offset == 3 and random.random() < 0.9:
            idx = random.choice(burst_items)
            pid, name, price, cat = prods[idx]
            qty = random.randint(20, 40)  # 爆量！
            items = [(item_id + len(all_sql), order_id, pid, price, qty)]
            total = price * qty
            ot = day.replace(hour=random.randint(8,21), minute=random.randint(0,59)).strftime('%Y-%m-%d %H:%M:%S')
            no = f"T{day.strftime('%m%d')}{order_id:05d}"
            all_sql.append(f"INSERT INTO supermarket_order.`order` (id,order_no,store_id,total_price,points,create_time) VALUES({order_id},'{no}',{store},{total:.0f},0,'{ot}');")
            for iid, oid, ipid, ipr, iqt in items:
                all_sql.append(f"INSERT INTO supermarket_order.order_item (id,order_id,product_id,price,quantity) VALUES({iid},{oid},{ipid},{ipr},{iqt});")
            order_id += 1
            item_id += len(items)

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
print("可运行 python3 scripts/ablation_test.py 进行消融实验")
