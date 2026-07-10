"""
YOLOv8n 基线训练脚本

使用与原始 v5 训练完全相同的参数复现基线模型。
本脚本只定义训练,由用户手动运行。

使用方法:
    python train_baseline.py

输出:
    baseline_runs/yolov8n_baseline/weights/best.pt
    baseline_runs/yolov8n_baseline/results.csv
"""

import os
import sys
from pathlib import Path

# 设置工作目录
WORK_DIR = Path(r'K:\Desktop\yolo_project')
os.chdir(str(WORK_DIR))
sys.path.insert(0, str(WORK_DIR))

from ultralytics import YOLO


BASELINE_DIR = WORK_DIR / 'runs' / 'detect' / 'baseline_runs' / 'yolov8n_baseline'
BASELINE_PT = BASELINE_DIR / 'weights' / 'best.pt'

# ============================================================
# 训练
# ============================================================

def train_baseline():
    """使用与 v5 完全一致的参数训练基线 YOLOv8n"""
    print("=" * 60)
    print("YOLOv8n Baseline Training")
    print("=" * 60)

    model = YOLO(str(WORK_DIR / 'yolov8n.pt'))
    print(f"Model loaded: yolov8n.pt")

    results = model.train(
        data=r'K:\Desktop\dataset\dataset\yolov8_v4\data_fixed.yaml',
        epochs=80,
        batch=16,
        imgsz=640,
        device=0,
        optimizer='auto',
        lr0=0.01,
        lrf=0.01,
        momentum=0.937,
        weight_decay=0.0005,
        warmup_epochs=3.0,
        cos_lr=False,
        hsv_h=0.015,
        hsv_s=0.7,
        hsv_v=0.4,
        degrees=45,
        translate=0.1,
        scale=0.5,
        shear=10,
        flipud=0.0,
        fliplr=0.5,
        mosaic=1.0,
        mixup=0.15,
        copy_paste=0.1,
        erasing=0.4,
        close_mosaic=10,
        amp=True,
        seed=42,
        deterministic=True,
        patience=15,
        project='baseline_runs',
        name='yolov8n_baseline',
        save=True,
        plots=True,
        exist_ok=True,
    )

    # ultralytics saves to runs/detect/<project>/<name>
    actual_dir = Path(results.save_dir)
    print(f"\nBaseline training completed!")
    print(f"Best model: {actual_dir / 'weights' / 'best.pt'}")
    return results


def evaluate_test():
    """在测试集上评估最佳模型"""
    print("\n" + "=" * 60)
    print("Test Set Evaluation")
    print("=" * 60)

    # 查找实际保存路径
    pt_path = BASELINE_PT
    if not pt_path.exists():
        import glob
        candidates = list(WORK_DIR.glob('runs/detect/baseline_runs/*/weights/best.pt'))
        if candidates:
            pt_path = candidates[0]
    print(f"Model: {pt_path}")

    model = YOLO(str(pt_path))

    results_val = model.val(
        data=r'K:\Desktop\dataset\dataset\yolov8_v4\data_fixed.yaml',
        split='val',
        plots=True,
    )

    results_test = model.val(
        data=r'K:\Desktop\dataset\dataset\yolov8_v4\data_fixed.yaml',
        split='test',
        plots=True,
    )

    print(f"\nValidation Set:")
    print(f"  mAP@0.5:       {results_val.box.map50:.5f}")
    print(f"  mAP@0.5:0.95:  {results_val.box.map:.5f}")
    print(f"  Precision:     {results_val.box.p[0] if len(results_val.box.p) > 0 else 'N/A'}")
    print(f"  Recall:        {results_val.box.r[0] if len(results_val.box.r) > 0 else 'N/A'}")

    print(f"\nTest Set:")
    print(f"  mAP@0.5:       {results_test.box.map50:.5f}")
    print(f"  mAP@0.5:0.95:  {results_test.box.map:.5f}")

    # 计算参数量
    params = sum(p.numel() for p in model.model.parameters()) / 1e6
    print(f"\n  Parameters:    {params:.2f}M")

    return results_val, results_test


def export_onnx():
    """导出 ONNX 模型"""
    print("\n" + "=" * 60)
    print("ONNX Export")
    print("=" * 60)

    pt_path = BASELINE_PT
    if not pt_path.exists():
        candidates = list(WORK_DIR.glob('runs/detect/baseline_runs/*/weights/best.pt'))
        if candidates:
            pt_path = candidates[0]
    print(f"Model: {pt_path}")

    model = YOLO(str(pt_path))
    path = model.export(format='onnx', simplify=True, opset=12)

    import os
    size_mb = os.path.getsize(path) / (1024 * 1024)
    print(f"ONNX exported: {path}")
    print(f"File size: {size_mb:.1f}MB")
    return path
    return path


if __name__ == '__main__':
    train_baseline()
    evaluate_test()
    export_onnx()
    print("\n✅ Baseline training complete!")
