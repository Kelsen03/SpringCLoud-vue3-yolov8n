"""
消融实验 — 完整复现论文算法（SQL三因子 + Java ABC分类）
"""
import subprocess

def mysql(q):
    r = subprocess.run(['docker','exec','-i','supermarket-mysql',
        'mysql','-uroot','-p123456','-h127.0.0.1','-N','-B','-e',q],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return [l.split('\t') for l in r.stdout.decode().strip().split('\n') if l]

inv = mysql("SELECT product_id,product_name,store_id,stock,warning_stock FROM supermarket_inventory.inventory WHERE stock<warning_stock*3")
sales = mysql("""
    SELECT oi.product_id,o.store_id,SUM(oi.quantity),
           COUNT(DISTINCT DATE(o.create_time)),COUNT(DISTINCT o.id)
    FROM supermarket_order.order_item oi
    JOIN supermarket_order.`order` o ON oi.order_id=o.id
    WHERE o.create_time>=DATE_SUB(NOW(),INTERVAL 14 DAY)
    GROUP BY 1,2
""")

sm = {}
for s in sales:
    sm[(int(s[0]),int(s[1]))] = (float(s[2]),int(s[3]),int(s[4]))

# ABC阈值
all_ts = [v[0] for v in sm.values()]
avg_sale = sum(all_ts)/max(len(all_ts),1)

items = []
for row in inv:
    pid,name,sid,stock,warn = int(row[0]),row[1],int(row[2]),int(row[3]),int(row[4])
    k = (pid,sid)
    if k not in sm: continue
    ts,sd,oc = sm[k]
    di = ts/14.0
    bi = sd/14.0
    ki = min(ts/max(oc,1)/10.0, 1.0)
    abc = 1.5 if ts>avg_sale*1.5 else (1.0 if ts>=avg_sale*0.5 else 0.5)
    items.append({"name":name,"s":stock,"w":warn,"di":di,"bi":bi,"ki":ki,"abc":abc,"ts":ts})

def stats(label, recs):
    n = len(recs)
    if n==0: return (label,0,0,0,0,0)
    avg = sum(recs)/n
    miss = sum(1 for i in range(n) if recs[i]==0 and items[i]["di"]*10>items[i]["s"])
    over = sum(1 for i in range(n) if recs[i]>items[i]["di"]*10*2 and items[i]["di"]*10>items[i]["s"])
    ok = sum(1 for i in range(n) if recs[i]>0 and recs[i]<=items[i]["di"]*10*2)
    total = sum(recs)
    return (label,avg,miss,over,ok,total,n)

r1 = [max(0,round(it["di"]*10-it["s"])) for it in items]
r2 = [max(0,round(it["di"]*10*(1+it["bi"])-it["s"])) for it in items]
r3 = [max(0,round(it["di"]*10*(1+it["bi"]+it["ki"])*it["abc"]-it["s"])) for it in items]

print(f"\n库存:{len(inv)} 销售:{len(sales)} 有数据:{len(items)} 均值销量:{avg_sale:.0f}\n")
print(f"{'方案':<22} {'建议':>5} {'漏报':>5} {'过度':>5} {'准确':>5} {'总量':>7} {'样本':>5}")
print("-"*60)
for s in [stats("①仅Di",r1), stats("②Di+Bi",r2), stats("③完整(Di+Bi+Ki)×ABC",r3)]:
    print(f"{s[0]:<22} {s[1]:>3.0f}件 {s[2]:>4}件 {s[3]:>4}件 {s[4]:>4}件 {s[5]:>6}件 {s[6]:>5}")
print("-"*60)

print("""
ABC分类: A(>均值×1.5)→×1.5  B(均值×0.5~1.5)→×1.0  C(<均值×0.5)→×0.5
完整模型 = Di × 10 × (1 + Bi + Ki) × ABC因子 - stock
""")
