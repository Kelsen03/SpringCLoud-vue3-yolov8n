"""
生成贴合现实的 14 天超市销售数据
3 门店 × 412 商品 × 14 天 = ~6000 笔订单
"""
import subprocess, random
from datetime import datetime, timedelta

def mysql(query):
    cmd = ['docker', 'exec', '-i', 'supermarket-mysql',
           'mysql', '-uroot', '-p123456', '-h127.0.0.1', '-N', '-B', '-e', query]
    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return r.stdout.decode().strip()

def run(sql):
    """执行非查询 SQL，返回是否成功"""
    r = subprocess.run(
        ['docker', 'exec', '-i', 'supermarket-mysql',
         'mysql', '-uroot', '-p123456', '-h127.0.0.1'],
        input=sql.encode(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return r.returncode == 0

products = mysql("SELECT id, name, price FROM supermarket_product.product").strip().split('\n')
prods = []
for p in products:
    parts = p.split('\t')
    prods.append((int(parts[0]), float(parts[2])))

random.seed(42)
now = datetime.now()
p_count = len(prods)

# === 现实库存分布 ===
# 热门品库存偏低（1-20），冷门品库存充裕（30-200）
run("UPDATE supermarket_inventory.inventory SET warning_stock=10;")
for i, (pid, price) in enumerate(prods):
    if i % 5 == 0:   stock = random.randint(1, 8)    # 快消品 → 低库存
    elif i % 5 == 1: stock = random.randint(5, 25)   # 中频品 → 偏低
    elif i % 5 == 2: stock = random.randint(15, 80)  # 周末型 → 中等
    elif i % 5 == 3: stock = random.randint(50, 200) # 慢消品 → 高库存
    else:             stock = random.randint(3, 15)   # 突发型 → 偏低
    for store in [1, 2, 3]:
        run(f"UPDATE supermarket_inventory.inventory SET stock={stock} WHERE product_id={pid} AND store_id={store};")

low = mysql("SELECT COUNT(*) FROM supermarket_inventory.inventory WHERE stock<10")
print(f"库存设置完成，低库存({low}件)")

# === 生成 14 天销售订单 ===
print("生成 14 天销售数据...")
order_id = 3000
total_orders = 0
total_items = 0
sql_buf = []

for day_offset in range(14):
    day = now - timedelta(days=day_offset)
    is_weekend = day.weekday() >= 5

    for store in [1, 2, 3]:
        # 每店每天 80-200 笔（周末更多）
        n = random.randint(120, 220) if is_weekend else random.randint(70, 140)

        for _ in range(n):
            r = random.random()
            # 按消费习惯选品：70% 高频品, 20% 中频, 8% 低频, 2% 突发
            if r < 0.40:
                idx = [i for i in range(p_count) if i % 5 == 0][random.randint(0, p_count//5 - 1)]
                qty = random.randint(1, 3) * (2 if is_weekend else 1)
            elif r < 0.65:
                idx = [i for i in range(p_count) if i % 5 == 1][random.randint(0, p_count//5 - 1)]
                qty = random.randint(1, 2)
            elif r < 0.85:
                idx = [i for i in range(p_count) if i % 5 == 2][random.randint(0, p_count//5 - 1)]
                qty = random.randint(2, 6) if is_weekend else random.randint(1, 2)
            elif r < 0.95:
                idx = [i for i in range(p_count) if i % 5 == 3][random.randint(0, p_count//5 - 1)]
                qty = random.randint(1, 2)
            else:
                idx = [i for i in range(p_count) if i % 5 == 4][random.randint(0, p_count//5 - 1)]
                qty = random.randint(8, 25) if day_offset == 3 else 0

            if qty == 0: continue
            pid, price = prods[idx]
            total = price * qty
            ot = day.replace(hour=random.randint(8,22), minute=random.randint(0,59)).strftime('%Y-%m-%d %H:%M:%S')
            no = f"T{day.strftime('%m%d')}{order_id:06d}"

            sql_buf.append(f"INSERT INTO supermarket_order.`order` VALUES({order_id},'{no}',{store},NULL,{total:.0f},0,'{ot}','test','test');")
            sql_buf.append(f"INSERT INTO supermarket_order.order_item VALUES({total_items+5000},{order_id},{pid},{price},{qty});")
            order_id += 1
            total_orders += 1
            total_items += 1

            # 每 500 条 flush 一次
            if len(sql_buf) >= 1000:
                run('\n'.join(sql_buf))
                sql_buf = []

if sql_buf:
    run('\n'.join(sql_buf))

print(f"生成: {total_orders} 笔订单, {total_items} 条明细")

# 更新 product_sales
run("DELETE FROM supermarket_order.product_sales;")
run("""
    INSERT INTO supermarket_order.product_sales (store_id, product_id, total_quantity)
    SELECT o.store_id, oi.product_id, SUM(oi.quantity)
    FROM supermarket_order.order_item oi
    JOIN supermarket_order.`order` o ON oi.order_id = o.id
    GROUP BY o.store_id, oi.product_id;
""")
print("完成")
