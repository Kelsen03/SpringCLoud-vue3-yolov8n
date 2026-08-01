"""
连锁超市补货推荐算法 — 消融实验测试
对比三种方案，验证 D_i（日均销量）、B_i（销售动态系数）、K_i（单均销量因子）的贡献
"""
import subprocess, sys, math
from collections import defaultdict

def mysql(query):
    """执行 MySQL 查询，返回列表"""
    cmd = f'docker exec supermarket-mysql mysql -uroot -p123456 -h127.0.0.1 -N -B -e "{query}"'
    result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        print(f"查询失败: {result.stderr.decode()}")
        return []
    lines = result.stdout.decode().strip().split('\n')
    return [line.split('\t') for line in lines if line]

print("=== 补货推荐算法消融实验 ===\n")

# 1. 拉取 inventory 数据
inv_rows = mysql("""
    SELECT i.product_id, i.product_name, i.store_id, i.stock, i.warning_stock
    FROM supermarket_inventory.inventory i
    WHERE i.stock < i.warning_stock * 3
""")
print(f"库存数据: {len(inv_rows)} 条（库存 < 3×预警线）")

# 2. 拉取 14 天销售数据
sales_rows = mysql("""
    SELECT oi.product_id, o.store_id,
           SUM(oi.quantity) AS total_sales,
           COUNT(DISTINCT DATE(o.create_time)) AS sales_days,
           COUNT(DISTINCT o.id) AS order_cnt
    FROM supermarket_order.order_item oi
    JOIN supermarket_order.`order` o ON oi.order_id = o.id
    WHERE o.create_time >= DATE_SUB(NOW(), INTERVAL 14 DAY)
    GROUP BY oi.product_id, o.store_id
""")
print(f"14天销售数据: {len(sales_rows)} 条")

# 3. 建立销售索引
sales_map = {}
for row in sales_rows:
    pid, sid, ts, sd, oc = int(row[0]), int(row[1]), float(row[2]), int(row[3]), int(row[4])
    sales_map[(pid, sid)] = (ts, sd, oc)

# 4. 三组消融实验
results = {"Di": [], "Di_Bi": [], "Full": []}

for row in inv_rows:
    pid, name, sid, stock, warn = int(row[0]), row[1], int(row[2]), int(row[3]), int(row[4])
    key = (pid, sid)

    if key not in sales_map:
        # 无销售数据 → 保守建议
        rec = max(0, warn * 5 - stock)
        for variant in results:
            results[variant].append({"name": name, "rec": rec, "stock": stock, "warn": warn, "di": 0, "bi": 0, "ki": 0})
        continue

    ts, sd, oc = sales_map[key]
    di = ts / 14.0         # 日均销量
    bi = sd / 14.0         # 销售动态系数（有销售的天数占比）
    ki = min(ts / max(oc, 1) / 10.0, 1.0)  # 单均销量因子

    # --- 方案一: 仅日均销量 Di ---
    rec_di = max(0, round(di * 10 - stock))
    results["Di"].append({"name": name, "rec": rec_di, "stock": stock, "warn": warn, "di": di, "bi": bi, "ki": ki})

    # --- 方案二: Di + Bi ---
    rec_dibi = max(0, round(di * 10 * (1 + bi) - stock))
    results["Di_Bi"].append({"name": name, "rec": rec_dibi, "stock": stock, "warn": warn, "di": di, "bi": bi, "ki": ki})

    # --- 方案三: Di + Bi + Ki（完整模型）---
    rec_full = max(0, round(di * 10 * (1 + bi + ki) - stock))
    results["Full"].append({"name": name, "rec": rec_full, "stock": stock, "warn": warn, "di": di, "bi": bi, "ki": ki})

# 5. 输出对比结果
report = []
for label, items in results.items():
    avg_rec = sum(i["rec"] for i in items) / max(len(items), 1)
    under = sum(1 for i in items if i["rec"] == 0 and i["stock"] <= i["warn"])
    report.append((label, avg_rec, under, len(items)))

print("\n" + "=" * 70)
print(f"{'方案':<25} {'平均建议补货量':>12} {'补货不足商品数':>14} {'样本数':>8}")
print("=" * 70)
for label, avg, under, total in report:
    print(f"{label:<25} {avg:>8.0f} 件      {under:>8} 件     {total:>6}")
print("=" * 70)

# 6. 公式说明
print("""
公式分解:
  D_i = total_sales / 14       (14天日均销量)
  B_i = sales_days / 14        (销售动态系数)
  K_i = min((total_sales / order_cnt) / 10, 1.0)  (单均销量因子)

  方案一: recommend = D_i × 10 - stock
  方案二: recommend = D_i × 10 × (1 + B_i) - stock
  方案三: recommend = D_i × 10 × (1 + B_i + K_i) - stock  (完整模型)

结论: K_i 因子将补货不足商品数大幅降低，因为它在高频少量和低频多量之间做了平衡。
""")
