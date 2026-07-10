"""
DynamicConv-YOLOv8n v4 (C2f Bottleneck + Temperature Annealing)
"""
import os, sys
from pathlib import Path
from ultralytics import YOLO

WORK_DIR = Path(r'K:\Desktop\yolo_project')
os.chdir(str(WORK_DIR))
sys.path.insert(0, str(WORK_DIR))

from yolov8_dynamic import apply_dynamic_conv, set_temperature
from dynamic_conv import DynamicConv2d


class TemperatureAnnealing:
    """温度退火回调: 每 N 轮降低温度 T, 让门控从软→硬逐步过渡"""
    def __init__(self, model, T_start=30, T_end=1, anneal_every=10):
        self.model = model
        self.T = T_start
        self.T_end = T_end
        self.anneal_every = anneal_every
        self.step_count = 0
        set_temperature(model, T_start)

    def __call__(self, trainer):
        self.step_count += 1
        if self.step_count % self.anneal_every == 0 and self.T > self.T_end:
            self.T = max(self.T - 2, self.T_end)
            set_temperature(self.model, self.T)
            print(f"\n  [Temp Anneal] epoch {trainer.epoch}: T={self.T:.0f}")


def train_dynamic():
    print("=" * 60)
    print("DynamicConv-YOLOv8n v4 (C2f + Temperature)")
    print("=" * 60)

    model = YOLO(str(WORK_DIR / 'yolov8n.pt'))
    orig = sum(p.numel() for p in model.model.parameters()) / 1e6
    print(f"Original: {orig:.2f}M")

    apply_dynamic_conv(model, verbose=True, K=4)
    new = sum(p.numel() for p in model.model.parameters()) / 1e6
    print(f"DynamicConv: {new:.2f}M")

    # 温度退火回调
    annealer = TemperatureAnnealing(model.model, T_start=30, T_end=1, anneal_every=8)
    model.add_callback("on_fit_epoch_end", annealer)

    print("\nTraining...")
    results = model.train(
        data=r'K:\Desktop\dataset\dataset\yolov8_v4\data_fixed.yaml',
        epochs=150,
        batch=16,
        imgsz=640,
        device=0,
        pretrained=False,
        optimizer='auto',
        lr0=0.002,
        lrf=0.0001,
        momentum=0.937,
        weight_decay=0.0005,
        warmup_epochs=5,
        cos_lr=True,
        amp=False,
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
        patience=30,
        project='dynamic_runs',
        name='yolov8n_dynamic_v4',
        save=True,
        plots=True,
        exist_ok=True,
    )

    print(f"\nDone! {results.save_dir}")


if __name__ == '__main__':
    train_dynamic()
