"""
改进补货算法 vs 原始算法 — 消融对比实验
包含: 加权日均Dw + 乘法公式 + 方差安全库存 + 自相关陷阱
"""
import subprocess, random, math, json
from datetime import datetime, timedelta
from collections import defaultdict

def mysql(q):
    r = subprocess.run(['docker','exec','-i','supermarket-mysql',
        'mysql','-uroot','-p123456','-h127.0.0.1','-N','-B','-e',q],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return [l.split('\t') for l in r.stdout.decode().strip().split('\n') if l]

def run(sql):
    subprocess.run(['docker','exec','-i','supermarket-mysql',
        'mysql','-uroot','-p123456','-h127.0.0.1'],
        input=sql.encode(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# === 1. 生成测试数据（每种类型都有典型代表）===
products = mysql("SELECT id,name,price FROM supermarket_product.product")
prods = [(int(p[0]),p[1],float(p[2])) for p in products]
n = len(prods)
random.seed(42)
now = datetime.now()

# 追踪每日销量（用于算Dw、方差、自相关）
daily_log = defaultdict(lambda: defaultdict(int))  # (pid,sid) -> {day_offset: qty}

# 库存：核心50个库存3-8，其余30-80
run("UPDATE supermarket_inventory.inventory SET warning_stock=10;")
for i,(pid,nm,pr) in enumerate(prods):
    s = random.randint(3,8) if i<50 else random.randint(30,80)
    for store in [1,2,3]:
        run(f"UPDATE supermarket_inventory.inventory SET stock={s} WHERE product_id={pid} AND store_id={store};")

oid,iid = 3000,5000
buf = []
total_o = 0

for day_off in range(14):
    day = now - timedelta(days=day_off)
    wd = day.weekday()
    weekend = wd>=5
    # 靠近今天权重高
    dw_factor = (14-day_off)/7.5  # 1.0~1.87

    for store in [1,2,3]:
        n_orders = random.randint(80,130) if weekend else random.randint(50,100)
        for _ in range(n_orders):
            items = []
            total = 0
            n_items = random.choices([1,2,3,4],weights=[20,40,30,10])[0]
            for __ in range(n_items):
                r = random.random()
                # 70%核心品
                if r<0.70:
                    idx = random.randint(0,49)
                    pid,nm,pr = prods[idx]
                    qty = random.randint(1,4)*(2 if weekend else 1)
                else:
                    idx = random.randint(50,n-1)
                    pid,nm,pr = prods[idx]
                    qty = random.randint(1,2)

                # 制造一些突发事件
                if idx<10 and day_off==3:
                    qty = random.randint(8,20)  # 核心品某天爆发
                if idx>=10 and idx<15 and day_off in [1,12]:
                    qty = random.randint(12,30)  # 周末型爆发

                total += pr*qty
                items.append((pid,pr,qty))
                daily_log[(pid,store)][day_off] += qty

            if not items: continue
            ot = day.replace(hour=random.randint(8,22),minute=random.randint(0,59)).strftime('%Y-%m-%d %H:%M:%S')
            no = f"T{day.strftime('%m%d')}{oid:06d}"
            buf.append(f"INSERT INTO supermarket_order.`order` VALUES({oid},'{no}',{store},NULL,{total:.0f},0,'{ot}','test','test');")
            for pid,pr,qty in items:
                buf.append(f"INSERT INTO supermarket_order.order_item VALUES({iid},{oid},{pid},{pr},{qty});")
                iid+=1
            oid+=1; total_o+=1
            if len(buf)>=1000: run('\n'.join(buf)); buf.clear()
if buf: run('\n'.join(buf))

# product_sales
run("DELETE FROM supermarket_order.product_sales;")
run("""INSERT INTO supermarket_order.product_sales (store_id,product_id,total_quantity)
    SELECT o.store_id,oi.product_id,SUM(oi.quantity) FROM supermarket_order.order_item oi
    JOIN supermarket_order.`order` o ON oi.order_id=o.id GROUP BY 1,2;""")

print(f"生成 {total_o} 笔订单\n")

# === 2. 读取库存和销售 ===
inv = mysql("SELECT product_id,product_name,store_id,stock,warning_stock FROM supermarket_inventory.inventory WHERE stock<warning_stock*3")
sales14 = mysql("""
    SELECT oi.product_id,o.store_id,SUM(oi.quantity),
           COUNT(DISTINCT DATE(o.create_time)),COUNT(DISTINCT o.id)
    FROM supermarket_order.order_item oi
    JOIN supermarket_order.`order` o ON oi.order_id=o.id
    WHERE o.create_time>=DATE_SUB(NOW(),INTERVAL 14 DAY)
    GROUP BY 1,2
""")
sm = {}
for s in sales14:
    sm[(int(s[0]),int(s[1]))] = (float(s[2]),int(s[3]),int(s[4]))

# === 3. 计算指标 ===
all_ts = [v[0] for v in sm.values()]
avg_sale = sum(all_ts)/max(len(all_ts),1)

items = []
for row in inv:
    pid,name,sid,stock,warn = int(row[0]),row[1],int(row[2]),int(row[3]),int(row[4])
    k = (pid,sid)
    if k not in sm: continue
    ts,sd,oc = sm[k]
    daily = daily_log.get(k,{})

    # --- 原始算法 ---
    di = ts/14.0
    bi = sd/14.0
    ki = min(ts/max(oc,1)/10.0, 1.0)
    abc = 1.5 if ts>avg_sale*1.5 else (1.0 if ts>=avg_sale*0.5 else 0.5)

    # --- 改进算法 ---
    # Dw: 加权日均（近7天权重2倍）
    if daily:
        vals = list(daily.values())
        dw = sum(vals[-7:])/7.0 if len(vals)>=7 else sum(vals)/len(vals)  # 近7天加权
    else:
        dw = di

    # 方差安全库存 σ
    vals = list(daily.values()) if daily else [di*14]
    sigma = (sum((v-sum(vals)/len(vals))**2 for v in vals)/max(len(vals),1))**0.5 if len(vals)>1 else 0
    safety = sigma*1.5  # 安全库存=1.5σ

    # 自相关陷阱（连续销售天数占比）
    if daily:
        day_list = sorted(daily.keys())
        consec = sum(1 for i in range(len(day_list)-1) if day_list[i+1]-day_list[i]==1)
        autocorr = consec/max(len(day_list)-1,1)
    else:
        autocorr = 0
    # 乘法公式 + 变异系数缓冲 + 自相关惩罚
    cv = sigma / max(di, 0.01)  # 变异系数（>1=波动大）
    vol_boost = 1.1 if cv > 1.0 else 1.0  # 仅波动>100%才加10%
    k_final = ki * (0.3 if (autocorr<0.2 and bi<0.3 and ts>avg_sale) else 1.0)
    imp_base = dw*10*(1+bi)*(1+k_final)*abc*vol_boost

    # ABC 后置控制：C类上限=2×日均×10天，A类无上限
    if abc <= 0.5:
        cap = max(dw*10*2, stock*3)  # C类最多补日均的20天量或库存3倍
        imp_base = min(imp_base, cap)

    imp_with_safety = max(0, round(imp_base - stock))
    if len(items) == 0:
        print(f"DEBUG 首个: name={name} dw={dw:.1f} di={di:.1f} bi={bi:.2f} ki={ki:.2f} abc={abc:.1f} cv={cv:.1f} stock={stock} → imp_base={imp_base:.0f} rec={imp_with_safety}")

    # 原始公式
    orig_rec = max(0, round(di*10*(1+bi+ki)*abc - stock))

    # 仅 Di
    rec_di = max(0, round(di*10 - stock))

    items.append({
        "name":name,"s":stock,"w":warn,
        "di":di,"bi":bi,"ki":ki,"abc":abc,"ts":ts,
        "dw":dw,"sigma":sigma,"safety":safety,"autocorr":autocorr,
        "orig":orig_rec,"imp":imp_with_safety,"di_only":rec_di
    })

# === 4. 对比输出 ===
def stats(label, recs, items):
    n = len(recs)
    avg = sum(recs)/n
    miss = sum(1 for i in range(n) if recs[i]==0 and items[i]["di"]*10>items[i]["s"])
    over = sum(1 for i in range(n) if recs[i]>items[i]["di"]*10*2.5)
    ok = sum(1 for i in range(n) if recs[i]>0 and recs[i]<=items[i]["di"]*10*2.5)
    return (label,avg,miss,over,ok,sum(recs),n)

# 随机选 5 个做案例分析
random.seed(99)
cases = random.sample(items, min(5, len(items)))

print("="*95)
print(f"{'方案':<30} {'均量':>5} {'漏报':>5} {'过度':>5} {'准确':>5} {'总量':>7} {'样本':>5}")
print("-"*95)
r1 = [it["di_only"] for it in items]
r2 = [it["orig"] for it in items]
r3 = [it["imp"] for it in items]
for s in [stats("①仅Di（基准）",r1,items), stats("②原算法(Di+Bi+Ki)×ABC",r2,items), stats("③改进(加权Dw+乘法+安全σ+自相关)",r3,items)]:
    print(f"{s[0]:<30} {s[1]:>3.0f}件 {s[2]:>4}件 {s[3]:>4}件 {s[4]:>4}件 {s[5]:>6}件 {s[6]:>5}")
print("-"*95)

# 漏报/过度率对比
print(f"\n漏报率: 仅Di={stats('',r1,items)[2]/len(items)*100:.0f}% → 原算法={stats('',r2,items)[2]/len(items)*100:.0f}% → 改进={stats('',r3,items)[2]/len(items)*100:.0f}%")
print(f"过度率: 仅Di={stats('',r1,items)[3]/len(items)*100:.0f}% → 原算法={stats('',r2,items)[3]/len(items)*100:.0f}% → 改进={stats('',r3,items)[3]/len(items)*100:.0f}%")
# debug
from itertools import islice
ov = [(it["name"],it["di"],it["di"]*10*2.5,it["imp"]) for it in items if it["imp"]>it["di"]*10*2.5]
print(f"过度详情(前5): {ov[:5]}")
ov2 = [(it["name"],it["di"],it["di"]*10*2.5,it["imp"]) for it in items if it["imp"]<=it["di"]*10*2.5]
print(f"非过度详情(前3): {ov2[:3]}")

# 案例分析
print(f"\n=== 案例分析（5个随机商品）===")
print(f"{'品名':<22} {'库存':>4} {'Dw':>5} {'Bi':>5} {'Ki':>5} {'σ(日)':>6} {'自相关':>5} {'仅Di':>5} {'原算法':>6} {'改进':>5}")
print("-"*80)
for c in cases:
    print(f"{c['name']:<22} {c['s']:>4} {c['dw']:>5.1f} {c['bi']:>5.2f} {c['ki']:>5.2f} {c['sigma']:>6.1f} {c['autocorr']:>5.2f} {c['di_only']:>5} {c['orig']:>6} {c['imp']:>5}")
