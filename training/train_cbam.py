"""
YOLOv8n + CBAM 注意力训练脚本
适合零售商品细粒度识别: 区分相似包装、聚焦标签区域
"""
import os, sys
from pathlib import Path
from ultralytics import YOLO

WORK_DIR = Path(r'K:\Desktop\yolo_project')
os.chdir(str(WORK_DIR))
sys.path.insert(0, str(WORK_DIR))

from yolov8_cbam import apply_cbam


def train_cbam():
    print("=" * 60)
    print("YOLOv8n + CBAM Training")
    print("=" * 60)

    model = YOLO(str(WORK_DIR / 'yolov8n.pt'))
    orig = sum(p.numel() for p in model.model.parameters()) / 1e6
    print(f"Original: {orig:.2f}M")

    apply_cbam(model, verbose=True)
    new = sum(p.numel() for p in model.model.parameters()) / 1e6
    print(f"+CBAM: {new:.2f}M (+{(new-orig)/orig*100:.1f}%)")

    print("\nTraining...")
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
        warmup_epochs=3,
        cos_lr=False,
        amp=True,
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
        seed=42,
        deterministic=True,
        patience=15,
        project='cbam_runs',
        name='yolov8n_cbam',
        save=True,
        plots=True,
        exist_ok=True,
    )

    print(f"\nDone! {results.save_dir}")


if __name__ == '__main__':
    train_cbam()
