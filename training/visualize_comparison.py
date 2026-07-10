"""
检测结果可视化对比脚本

生成 vanilla YOLOv8n vs DynamicConv-YOLOv8n 的并排检测对比图。
选取典型测试图片，展示改进效果。

使用方法:
    python visualize_comparison.py
"""

import os
import sys
from pathlib import Path

WORK_DIR = Path(r'K:\Desktop\yolo_project')
os.chdir(str(WORK_DIR))
sys.path.insert(0, str(WORK_DIR))

import cv2
import numpy as np
from ultralytics import YOLO
from yolov8_dynamic import apply_dynamic_conv

CLASS_NAMES_CN = {
    0: '可口可乐', 1: '芬达', 2: '乐事薯片', 3: '康师傅',
    4: '脉动', 5: '农夫山泉', 6: '百事可乐', 7: '红牛',
    8: '雪碧', 9: '王老吉',
}

COLORS = [
    (0, 0, 255), (0, 255, 0), (255, 0, 0), (255, 255, 0),
    (255, 0, 255), (0, 255, 255), (128, 0, 128), (128, 128, 0),
    (0, 128, 128), (128, 0, 0),
]


def draw_detections(image, results, label_prefix=""):
    """在图片上绘制检测框"""
    img = image.copy()
    if results[0].boxes is not None:
        boxes = results[0].boxes.data.cpu().numpy()
        for box in boxes:
            x1, y1, x2, y2, conf, cls = box
            cls = int(cls)
            color = COLORS[cls % len(COLORS)]
            cv2.rectangle(img, (int(x1), int(y1)), (int(x2), int(y2)), color, 3)
            label = f"{CLASS_NAMES_CN.get(cls, str(cls))} {conf:.2f}"
            cv2.putText(img, label, (int(x1), int(y1)-5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

    # 添加标签
    cv2.putText(img, label_prefix, (10, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 3)
    return img


def create_comparison(baseline_model_path, dynamic_model_path, test_images_dir, output_dir, num_samples=4):
    """创建并排对比图"""
    print("=" * 60)
    print("Detection Visualization Comparison")
    print("=" * 60)

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 加载模型
    print("\nLoading models...")
    model_baseline = YOLO(baseline_model_path)

    # DynamicConv 模型
    model_dynamic = YOLO(dynamic_model_path)
    # 重新应用 DynamicConv 结构 (因为加载的权重需要对应结构)
    try:
        apply_dynamic_conv(model_dynamic, verbose=False)
    except Exception as e:
        print(f"  Note: Could not re-apply DynamicConv structure: {e}")
        print(f"  Using model as-is...")

    # 选取测试图片
    test_dir = Path(test_images_dir)
    image_files = sorted(list(test_dir.glob('*.jpg')))[:num_samples * 2]

    # 选取有代表性的 (取中间几张, 避免前几张太简单)
    if len(image_files) > num_samples:
        step = len(image_files) // num_samples
        selected = [image_files[i * step] for i in range(num_samples)]
    else:
        selected = image_files[:num_samples]

    print(f"\nSelected {len(selected)} images for comparison:")

    for i, img_path in enumerate(selected):
        print(f"\n  [{i+1}/{len(selected)}] {img_path.name}")

        image = cv2.imread(str(img_path))
        if image is None:
            print(f"    ⚠️ Cannot read image, skipping")
            continue

        h, w = image.shape[:2]
        print(f"    Size: {w}x{h}")

        # 基线模型检测
        results_baseline = model_baseline(image, conf=0.20, verbose=False)
        img_baseline = draw_detections(image, results_baseline, "YOLOv8n Baseline")

        # DynamicConv 模型检测
        results_dynamic = model_dynamic(image, conf=0.20, verbose=False)
        img_dynamic = draw_detections(image, results_dynamic, "DynamicConv-YOLOv8n")

        # 并排拼接
        comparison = np.hstack([img_baseline, img_dynamic])

        # 保存
        output_path = output_dir / f'comparison_{i+1}_{img_path.stem}.jpg'
        cv2.imwrite(str(output_path), comparison)
        print(f"    Saved: {output_path}")

    print(f"\n✅ Visualizations saved to: {output_dir}")


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--baseline', type=str,
                        default=str(WORK_DIR / 'baseline_runs' / 'yolov8n_baseline' / 'weights' / 'best.pt'))
    parser.add_argument('--dynamic', type=str,
                        default=str(WORK_DIR / 'dynamic_runs' / 'yolov8n_dynamic' / 'weights' / 'best.pt'))
    parser.add_argument('--images', type=str,
                        default=str(WORK_DIR / 'dataset' / 'yolov8_v4' / 'test' / 'images'))
    parser.add_argument('--output', type=str,
                        default=str(WORK_DIR / 'comparison_images'))
    parser.add_argument('--samples', type=int, default=4)
    args = parser.parse_args()

    create_comparison(args.baseline, args.dynamic, args.images, args.output, args.samples)
