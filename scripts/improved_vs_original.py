"""
改进补货算法 vs 原始算法 — 消融对比
改进: 乘法公式 + 方差安全σ + 自相关惩罚 + ABC后置控制
所有输入均来自 SQL，无 daily_log 污染
"""
import subprocess, random, math
from datetime import datetime, timedelta

def query(sql):
    r = subprocess.run(['docker','exec','-i','supermarket-mysql',
        'mysql','-uroot','-p123456','-h127.0.0.1','-N','-B','-e',sql],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return [l.split('\t') for l in r.stdout.decode().strip().split('\n') if l]

def run(sql):
    subprocess.run(['docker','exec','-i','supermarket-mysql',
        'mysql','-uroot','-p123456','-h127.0.0.1'],
        input=sql.encode(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# ==== 生成测试数据 ====
prods = [(int(p[0]),p[1],float(p[2])) for p in query("SELECT id,name,price FROM supermarket_product.product")]
n = len(prods)
random.seed(42)
now = datetime.now()

run("UPDATE supermarket_inventory.inventory SET warning_stock=10;")
for i,(pid,nm,pr) in enumerate(prods[:50]):
    for st in [1,2,3]:
        run(f"UPDATE supermarket_inventory.inventory SET stock={random.randint(3,8)} WHERE product_id={pid} AND store_id={st};")
for i,(pid,nm,pr) in enumerate(prods[50:]):
    for st in [1,2,3]:
        run(f"UPDATE supermarket_inventory.inventory SET stock={random.randint(30,80)} WHERE product_id={pid} AND store_id={st};")

oid = 3000; iid = 5000; buf = []; total_o = 0
for day_off in range(14):
    day = now - timedelta(days=day_off)
    wd = day.weekday()
    for st in [1,2,3]:
        n_orders = random.randint(80,130) if wd>=5 else random.randint(50,100)
        for _ in range(n_orders):
            items = []; total = 0
            for __ in range(random.choices([1,2,3,4],weights=[20,40,30,10])[0]):
                r = random.random()
                if r<0.70: idx = random.randint(0,49)
                else: idx = random.randint(50,n-1)
                pid,nm,pr = prods[idx]
                qty = random.randint(1,4)*(2 if wd>=5 else 1)
                if idx<10 and day_off==3: qty = random.randint(8,20)
                if 10<=idx<15 and day_off in [1,12]: qty = random.randint(12,30)
                total += pr*qty; items.append((pid,pr,qty))
            if not items: continue
            ot = day.replace(hour=random.randint(8,22),minute=random.randint(0,59)).strftime('%Y-%m-%d %H:%M:%S')
            buf.append(f"INSERT INTO supermarket_order.`order` VALUES({oid},'T{day.strftime('%m%d')}{oid:06d}',{st},NULL,{total:.0f},0,'{ot}','test','test');")
            for pid,pr,qty in items:
                buf.append(f"INSERT INTO supermarket_order.order_item VALUES({iid},{oid},{pid},{pr},{qty});"); iid+=1
            oid+=1; total_o+=1
            if len(buf)>=1000: run('\n'.join(buf)); buf.clear()
if buf: run('\n'.join(buf))
run("DELETE FROM supermarket_order.product_sales;")
run("""INSERT INTO supermarket_order.product_sales (store_id,product_id,total_quantity)
    SELECT o.store_id,oi.product_id,SUM(oi.quantity) FROM supermarket_order.order_item oi
    JOIN supermarket_order.`order` o ON oi.order_id=o.id GROUP BY 1,2;""")
print(f"生成 {total_o} 笔订单\n")

# ==== 算法对比 ====
inv = query("SELECT product_id,product_name,store_id,stock,warning_stock FROM supermarket_inventory.inventory WHERE stock<warning_stock*3")
s14 = query("""
    SELECT oi.product_id,o.store_id,SUM(oi.quantity),
           COUNT(DISTINCT DATE(o.create_time)),COUNT(DISTINCT o.id)
    FROM supermarket_order.order_item oi
    JOIN supermarket_order.`order` o ON oi.order_id=o.id
    WHERE o.create_time>=DATE_SUB(NOW(),INTERVAL 14 DAY) GROUP BY 1,2
""")
sm = {}; [sm.update({(int(s[0]),int(s[1])):(float(s[2]),int(s[3]),int(s[4]))}) for s in s14]
avg_sale = sum(v[0] for v in sm.values())/max(len(sm),1)

items = []
for row in inv:
    pid,name,sid,stock,warn = int(row[0]),row[1],int(row[2]),int(row[3]),int(row[4])
    k = (pid,sid)
    if k not in sm: continue
    ts,sd,oc = sm[k]
    di = ts/14.0; bi = sd/14.0; ki = min(ts/max(oc,1)/10.0,1.0)
    abc = 1.5 if ts>avg_sale*1.5 else (1.0 if ts>=avg_sale*0.5 else 0.5)

    # σ估算法: 销量越大+间隔越不规律→波动越大
    sigma = di * (1.5 - bi) * 1.5
    cv = sigma/max(di,0.01)

    # 乘法公式 + CV缓冲 + 自相关惩罚
    vol_boost = 1 + min(cv/10, 0.15)  # CV高→加最多15%
    k_final = ki * (0.3 if bi<0.15 and ts>avg_sale else 1.0)
    rec_imp = max(0, round(di*10*(1+bi)*(1+k_final)*abc*vol_boost - stock))

    rec_orig = max(0, round(di*10*(1+bi+ki)*abc - stock))
    rec_di = max(0, round(di*10 - stock))

    items.append({"n":name,"s":stock,"di":di,"dw":di,"bi":bi,"ki":ki,"sig":sigma,
                  "abc":abc,"cv":cv,"orig":rec_orig,"imp":rec_imp,"di_only":rec_di})

def stats(label, recs):
    n = len(recs)
    miss = sum(1 for i in range(n) if recs[i]==0 and items[i]["di"]*10>items[i]["s"])
    over = sum(1 for i in range(n) if items[i]["di"]>0.01 and recs[i]>items[i]["di"]*10*2.5)
    ok = n - miss - over
    return (label, sum(recs)/n, miss, over, ok, sum(recs), n)

r1 = [it["di_only"] for it in items]
r2 = [it["orig"] for it in items]
r3 = [it["imp"] for it in items]

print(f"{'方案':<30} {'均量':>5} {'漏报':>5} {'过度':>5} {'准确':>5} {'总量':>7} {'样本':>5}")
print("-"*65)
for s in [stats("①仅Di",r1), stats("②原算法(Di+Bi+Ki)×ABC",r2), stats("③改进(乘法+σ+自相关)",r3)]:
    print(f"{s[0]:<30} {s[1]:>3.0f}件 {s[2]:>4}件 {s[3]:>4}件 {s[4]:>4}件 {s[5]:>6}件 {s[6]:>5}")
print("-"*65)

# 案例分析
rnd = random.Random(42)
cases = rnd.sample(items, min(5,len(items)))
print(f"\n{'品名':<22} {'库存':>4} {'Di':>5} {'Bi':>5} {'Ki':>5} {'σ':>6} {'ABC':>4} {'仅Di':>5} {'原算法':>6} {'改进':>5}")
print("-"*80)
for c in cases:
    print(f"{c['n']:<22} {c['s']:>4} {c['di']:>5.1f} {c['bi']:>5.2f} {c['ki']:>5.2f} {c['sig']:>6.1f} {c['abc']:>4.1f} {c['di_only']:>5} {c['orig']:>6} {c['imp']:>5}")

s1,s2,s3 = stats("",r1)[2:5],stats("",r2)[2:5],stats("",r3)[2:5]
print(f"\n漏报率: {s1[0]/len(items)*100:.0f}% → {s2[0]/len(items)*100:.0f}% → {s3[0]/len(items)*100:.0f}%")
print(f"过度率: {s1[1]/len(items)*100:.0f}% → {s2[1]/len(items)*100:.0f}% → {s3[1]/len(items)*100:.0f}%")
print(f"准确率: {s1[2]/len(items)*100:.0f}% → {s2[2]/len(items)*100:.0f}% → {s3[2]/len(items)*100:.0f}%")
