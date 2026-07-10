"""
YOLOv8n + ATGA 集成 — 自适应纹理门控注意力

在 Neck 的 C2f 后插入 ATGA, 聚焦多尺度特征的自适应融合。
Neck 是特征金字塔核心, RGB+纹理融合在这里效果最好。
"""
import torch
import torch.nn as nn
from ultralytics.nn.modules import C2f
from atga import ATGA


def apply_atga(model, verbose=True):
    """
    在 YOLOv8n Neck 的 C2f 后插入 ATGA

    Neck C2f: model.12, model.15, model.18, model.21
    这4个位置处理多尺度融合特征, ATGA 在此最有效
    """
    NECK_POSITIONS = {12, 15, 18, 21}
    inserted = 0

    for idx in sorted(NECK_POSITIONS, reverse=True):
        module = model.model.model[idx]
        if isinstance(module, C2f):
            # 获取输出通道
            if hasattr(module, 'cv2') and hasattr(module.cv2, 'conv'):
                out_ch = module.cv2.conv.out_channels
            else:
                for p in module.parameters():
                    out_ch = p.shape[0]
                    break

            atga = ATGA(out_ch, reduction=max(out_ch // 16, 4))

            wrapped = nn.Sequential(module, atga)
            for attr in ['f', 'i', 'type']:
                if hasattr(module, attr):
                    setattr(wrapped, attr, getattr(module, attr))
            wrapped.f = module.f if hasattr(module, 'f') else -1
            wrapped.i = idx

            model.model.model[idx] = wrapped
            inserted += 1

            if verbose:
                print(f"  model.{idx}: +ATGA(ch={out_ch})")

    if verbose:
        p = sum(p.numel() for p in model.model.parameters()) / 1e6
        print(f"  Inserted {inserted} ATGA, Params: {p:.2f}M")
    return model


if __name__ == '__main__':
    from ultralytics import YOLO

    print("=" * 60)
    print("YOLOv8n + ATGA Integration Test")
    print("=" * 60)

    model = YOLO('yolov8n.pt')
    orig = sum(p.numel() for p in model.model.parameters()) / 1e6
    print(f"Original: {orig:.2f}M")

    apply_atga(model)

    dummy = torch.randn(1, 3, 640, 640)
    model.model.eval()
    with torch.no_grad():
        out = model.model(dummy)
    print(f"Forward OK: {type(out).__name__}")
    print("Done!")
