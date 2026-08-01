"""
真实超市补货场景模拟 — 消融实验专用
50 个高频品占 70% 销量，其余 360+ 品分散
"""
import subprocess, random, json
from datetime import datetime, timedelta

def mysql(q):
    r = subprocess.run(['docker','exec','-i','supermarket-mysql','mysql','-uroot','-p123456','-h127.0.0.1','-N','-B','-e',q],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return r.stdout.decode().strip()

def run(sql):
    subprocess.run(['docker','exec','-i','supermarket-mysql','mysql','-uroot','-p123456','-h127.0.0.1'],
                   input=sql.encode(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)

products = mysql("SELECT id,name,price FROM supermarket_product.product").strip().split('\n')
prods_all = [(int(p.split('\t')[0]), p.split('\t')[1], float(p.split('\t')[2])) for p in products]
n = len(prods_all)
random.seed(42)

# === 50 个核心品（索引 0-49）占 70% 销量 ===
core = prods_all[:50]
rest = prods_all[50:]

# === 现实库存：核心品库存低(1-8)，非核心库存正常(20-80) ===
run("UPDATE supermarket_inventory.inventory SET warning_stock=10;")
for pid, name, price in core:
    for store in [1,2,3]:
        run(f"UPDATE supermarket_inventory.inventory SET stock={random.randint(1,8)} WHERE product_id={pid} AND store_id={store};")
for pid, name, price in rest:
    for store in [1,2,3]:
        run(f"UPDATE supermarket_inventory.inventory SET stock={random.randint(20,80)} WHERE product_id={pid} AND store_id={store};")

now = datetime.now()
oid, iid = 3000, 5000
buf = []
total_o, total_i = 0, 0

for day_off in range(14):
    day = now - timedelta(days=day_off)
    weekend = day.weekday() >= 5

    for store in [1, 2, 3]:
        # 每店每天 80-150 笔订单
        for _ in range(random.randint(100, 170) if weekend else random.randint(70, 120)):
            items = []
            total = 0
            # 每单 1-4 件
            for __ in range(random.choices([1,2,3,4], weights=[20,40,30,10])[0]):
                if random.random() < 0.70:
                    # 核心品 — 销量集中
                    idx = random.randint(0, 49)
                    pid, name, price = core[idx]
                    qty = random.randint(1, 4) * (2 if weekend else 1)
                else:
                    idx = random.randint(50, n - 1)
                    pid, name, price = prods_all[idx]
                    qty = random.randint(1, 2)

                total += price * qty
                items.append((pid, price, qty))

            ot = day.replace(hour=random.randint(8,22), minute=random.randint(0,59)).strftime('%Y-%m-%d %H:%M:%S')
            no = f"T{day.strftime('%m%d')}{oid:06d}"
            buf.append(f"INSERT INTO supermarket_order.`order` VALUES({oid},'{no}',{store},NULL,{total:.0f},0,'{ot}','test','test');")
            for pid, price, qty in items:
                buf.append(f"INSERT INTO supermarket_order.order_item VALUES({iid},{oid},{pid},{price},{qty});")
                iid += 1
                total_i += 1
            oid += 1
            total_o += 1

            if len(buf) >= 1000:
                run('\n'.join(buf))
                buf.clear()

if buf: run('\n'.join(buf))

# 更新 product_sales
run("DELETE FROM supermarket_order.product_sales;")
run("""INSERT INTO supermarket_order.product_sales (store_id,product_id,total_quantity)
    SELECT o.store_id,oi.product_id,SUM(oi.quantity) FROM supermarket_order.order_item oi
    JOIN supermarket_order.`order` o ON oi.order_id=o.id GROUP BY 1,2;""")

print(f"核心品(50): 库存 1-8, 占 70% 销量")
print(f"非核心({n-50}): 库存 20-80, 占 30% 销量")
print(f"生成: {total_o} 笔订单, {total_i} 条明细")
print(f"低库存品: {mysql('SELECT COUNT(*) FROM supermarket_inventory.inventory WHERE stock<10')} 件")
print("运行: python3 scripts/ablation_test.py")
