"""
YOLOv8n + ATGA 训练脚本

ATGA (自适应纹理门控注意力):
- 可学习边缘检测器替代手工 Canny
- 通道级门控动态融合 RGB+纹理特征
- 专门针对透明瓶身商品 (脉动/农夫山泉/雪碧)
"""
import os, sys
from pathlib import Path
from ultralytics import YOLO

WORK_DIR = Path(r'K:\Desktop\yolo_project')
os.chdir(str(WORK_DIR))
sys.path.insert(0, str(WORK_DIR))

from yolov8_atga import apply_atga


def train_atga():
    print("=" * 60)
    print("YOLOv8n + ATGA Training")
    print("=" * 60)

    model = YOLO(str(WORK_DIR / 'yolov8n.pt'))
    orig = sum(p.numel() for p in model.model.parameters()) / 1e6
    print(f"Original: {orig:.2f}M")

    apply_atga(model, verbose=True)
    new = sum(p.numel() for p in model.model.parameters()) / 1e6
    print(f"+ATGA: {new:.2f}M (+{(new-orig)/orig*100:.1f}%)")

    print("\nTraining...")
    results = model.train(
        data=r'K:\Desktop\dataset\dataset\yolov8_v4\data_fixed.yaml',
        epochs=80, batch=16, imgsz=640, device=0,
        optimizer='auto', lr0=0.01, lrf=0.01,
        momentum=0.937, weight_decay=0.0005,
        warmup_epochs=3, cos_lr=False, amp=True,
        hsv_h=0.015, hsv_s=0.7, hsv_v=0.4,
        degrees=45, translate=0.1, scale=0.5, shear=10,
        flipud=0.0, fliplr=0.5,
        mosaic=1.0, mixup=0.15, copy_paste=0.1, erasing=0.4,
        close_mosaic=10,
        seed=42, deterministic=True, patience=15,
        project='atga_runs', name='yolov8n_atga',
        save=True, plots=True, exist_ok=True,
    )

    print(f"\nDone! {results.save_dir}")


if __name__ == '__main__':
    train_atga()
