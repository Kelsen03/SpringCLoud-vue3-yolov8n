"""
消融实验 — 验证 Di(日均销量)、Bi(频率动态)、Ki(订单量级) 的增量贡献
"""
import subprocess, random

def mysql(q):
    r = subprocess.run(['docker','exec','-i','supermarket-mysql',
        'mysql','-uroot','-p123456','-h127.0.0.1','-N','-B','-e',q],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return [l.split('\t') for l in r.stdout.decode().strip().split('\n') if l]

print("=== 补货推荐算法消融实验 ===\n")

# 1. inventory
inv = mysql("SELECT product_id,product_name,store_id,stock,warning_stock FROM supermarket_inventory.inventory WHERE stock<warning_stock*3")
print(f"库存数据: {len(inv)} 条（stock < 3×warning）")

# 2. 14天销售
sales = mysql("""
    SELECT oi.product_id,o.store_id,SUM(oi.quantity),
           COUNT(DISTINCT DATE(o.create_time)),COUNT(DISTINCT o.id)
    FROM supermarket_order.order_item oi
    JOIN supermarket_order.`order` o ON oi.order_id=o.id
    WHERE o.create_time>=DATE_SUB(NOW(),INTERVAL 14 DAY)
    GROUP BY 1,2
""")
print(f"14天销售: {len(sales)} 条\n")

sm = {}
for row in sales:
    sm[(int(row[0]),int(row[1]))] = (float(row[2]),int(row[3]),int(row[4]))

# 3. 三方案 + ABC分类
# ABC: 销量>均值1.5倍→A(1.5), >0.5倍→B(1.0), 其余→C(0.5)
all_sales = [float(sm[k][0]) for k in sm]
avg_sales = sum(all_sales) / max(len(all_sales), 1)

res = {"仅Di":[], "Di+Bi":[], "完整模型":[]}
for row in inv:
    pid, name, sid, stock, warn = int(row[0]),row[1],int(row[2]),int(row[3]),int(row[4])
    key = (pid,sid)
    if key not in sm: continue
    ts, sd, oc = sm[key]
    di = ts/14.0
    bi = sd/14.0
    ki = min(ts/max(oc,1)/10.0, 1.0)
    # ABC分类因子
    abc = 1.5 if ts > avg_sales*1.5 else (1.0 if ts >= avg_sales*0.5 else 0.5)
    d = {"name":name,"stock":stock,"warn":warn,"di":di,"bi":bi,"ki":ki,"abc":abc,"sales":ts}
    d["rec_di"] = max(0, round(di*10 - stock))
    d["rec_dibi"] = max(0, round(di*10*(1+bi) - stock))
    d["rec_full"] = max(0, round(di*10*(1+bi+ki)*abc - stock))  # 完整 = SQL三因子 × ABC
    res["仅Di"].append(d)
    res["Di+Bi"].append(d)
    res["完整模型"].append(d)
    res["Di+Bi"].append(d)
    res["完整模型"].append(d)

# 4. 统计
print("=" * 90)
print(f"{'方案':<18} {'平均建议':>6} {'漏报':>6} {'过度':>6} {'准确':>6} {'消耗/件':>8} {'样本':>5}")
print("=" * 90)
for label in ["仅Di","Di+Bi","完整模型"]:
    items = res[label]
    tot = len(items)
    avg = sum(i[f"rec_{'di' if label=='仅Di' else 'dibi' if label=='Di+Bi' else 'full'}"] for i in items)/max(tot,1)
    fn = sum(1 for i in items if i[f"rec_{'di' if label=='仅Di' else 'dibi' if label=='Di+Bi' else 'full'}"]==0 and i['di']*10>i['stock'])
    fp = sum(1 for i in items if i[f"rec_{'di' if label=='仅Di' else 'dibi' if label=='Di+Bi' else 'full'}"]>i['di']*10*2 and i['di']*10>i['stock'])
    ok = sum(1 for i in items if i[f"rec_{'di' if label=='仅Di' else 'dibi' if label=='Di+Bi' else 'full'}"]>0 and i[f"rec_{'di' if label=='仅Di' else 'dibi' if label=='Di+Bi' else 'full'}"]<=i['di']*10*2)
    total_rec = sum(i[f"rec_{'di' if label=='仅Di' else 'dibi' if label=='Di+Bi' else 'full'}"] for i in items)
    print(f"{label:<18} {avg:>4.0f}件 {fn:>4}件 {fp:>4}件 {ok:>4}件 {total_rec:>6}件  {tot:>5}")
print("=" * 90)

print("""
指标说明:
  漏报 = 建议补0件，但日均销量×10天 > 库存 (该补没补)
  过度 = 建议量 > 日均销量×10天×2      (补太多)
  准确 = 建议量 ∈ (0, 日均销量×10天×2] (合理范围)
  消耗 = 补货方案所需的总补货件数

公式: Di=14天总销量/14  Bi=销售天数/14  Ki=min(销量/订单数/10,1)
  仅Di:    Di × 10 - stock
  Di+Bi:   Di × 10 × (1+Bi) - stock
  完整:    Di × 10 × (1+Bi+Ki) - stock
""")
