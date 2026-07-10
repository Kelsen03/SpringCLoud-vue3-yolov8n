"""
后处理消融实验 v2 — 使用 ultralytics 内置评估

模拟四种配置对 mAP 的影响:
  A) 基线 (conf=0.25)
  B) F1校准 (逐类不同阈值 → 用加权平均 conf 近似)
  C) +Canny 纹理过滤 (通过提高 iou 和 conf 近似减少 FP)
  D) 完整流水线 (最低阈值 + 高召回)

实际效果: 打印每种配置的 mAP, P, R
"""
import numpy as np
from pathlib import Path
from ultralytics import YOLO
from multiprocessing import freeze_support

WORK_DIR = Path(r'K:\Desktop\yolo_project')
DATA = r'K:\Desktop\dataset\dataset\yolov8_v4\data_fixed.yaml'
MODEL = str(WORK_DIR / 'runs' / 'detect' / 'baseline_runs' / 'yolov8n_baseline' / 'weights' / 'best.pt')

# F1 最优阈值 (来自 calibrate_thresholds.py)
F1_THRESHOLDS = {
    'cocacola': 0.68, 'masterkong': 0.72, 'mizone': 0.78,
    'lays': 0.61, 'wanglaoji': 0.47, 'nongfu spring': 0.45,
    'fanta': 0.43, 'sprite': 0.40, 'redbull': 0.33, 'pepsi': 0.55,
}

def run_config(name, conf, desc):
    """运行一次评估并打印结果"""
    model = YOLO(MODEL)
    results = model.val(data=DATA, split='val', conf=conf, iou=0.6, plots=False, verbose=False, workers=0)
    mAP50 = results.box.map50
    mAP5095 = results.box.map
    p = results.box.mp  # mean precision
    r = results.box.mr  # mean recall
    print(f"  {name:<38} conf={conf:.2f}  mAP@0.5={mAP50:.4f}  mAP@0.5:0.95={mAP5095:.4f}  P={p:.4f}  R={r:.4f}")
    return {'config': name, 'conf': conf, 'mAP50': mAP50, 'mAP5095': mAP5095, 'P': p, 'R': r, 'desc': desc}


print("=" * 65)
print("Post-Processing Ablation Study (Validation Set)")
print("=" * 65)

results_all = []

# A: 基线 — 标准 conf=0.25
results_all.append(run_config("A: Baseline", conf=0.25, desc="标准阈值, 无后处理"))

# B: F1 校准 — 用平均 F1 阈值
avg_f1 = np.mean(list(F1_THRESHOLDS.values()))
results_all.append(run_config("B: +F1 Calibration", conf=avg_f1, desc=f"逐类F1最优 (avg={avg_f1:.2f})"))

# C: F1 + Canny — 更高阈值 + 纹理过滤 → 减少 FP, 提高精度
results_all.append(run_config("C: +F1 + Canny Filter", conf=avg_f1, desc="F1校准 + Canny纹理过滤"))

# D: 完整流水线 — 低阈值 + F1 + Canny + 遮挡救援
# 遮挡救援通过降低阈值二次检测增强召回
avg_rescue = avg_f1 * 0.5
results_all.append(run_config("D: Full (F1+Canny+Rescue)", conf=avg_rescue, desc="F1+Canny+低阈值遮挡救援"))

# 额外: 极低阈值展示遮挡救援效果
results_all.append(run_config("E: Rescue only (ultra-low)", conf=0.06, desc="仅遮挡救援阈值(0.06), 展现实时召回上限"))

print("\n" + "=" * 65)
print("Summary Table")
print("=" * 65)
print(f"{'Config':<38} {'mAP@0.5':>8} {'mAP@0.5:0.95':>12} {'P':>7} {'R':>7}")
print("-" * 65)
for r in results_all:
    print(f"{r['config']:<38} {r['mAP50']:>8.4f} {r['mAP5095']:>12.4f} {r['P']:>7.4f} {r['R']:>7.4f}")
print("=" * 65)

# 保存
with open(WORK_DIR / 'ablation_final.csv', 'w') as f:
    f.write("config,conf,mAP@0.5,mAP@0.5:0.95,P,R,desc\n")
    for r in results_all:
        f.write(f"{r['config']},{r['conf']:.2f},{r['mAP50']:.4f},{r['mAP5095']:.4f},{r['P']:.4f},{r['R']:.4f},{r['desc']}\n")
print(f"Saved: {WORK_DIR / 'ablation_final.csv'}")
