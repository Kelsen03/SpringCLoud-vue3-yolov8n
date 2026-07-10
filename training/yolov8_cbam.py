"""
YOLOv8n + CBAM 注意力集成

在 C2f 模块后插入 CBAM, 增强细粒度特征判别能力。
适用于零售商品识别: 区分相似包装、聚焦标签区域。
"""
import torch
import torch.nn as nn
from ultralytics.nn.modules import C2f
from cbam import CBAM


def apply_cbam(model, verbose=True):
    """
    在 YOLOv8n 的 Backbone+Neck 每个 C2f 后插入 CBAM

    YOLOv8n C2f 位置:
      Backbone: model.2, model.4, model.6, model.8
      Neck:     model.12, model.15, model.18, model.21
    共8个 C2f → 插入8个 CBAM
    """
    C2F_POSITIONS = {2, 4, 6, 8, 12, 15, 18, 21}

    inserted = 0
    for idx in sorted(C2F_POSITIONS, reverse=True):  # 从后往前插入, 不影响索引
        module = model.model.model[idx]
        if isinstance(module, C2f):
            # 获取 C2f 输出通道
            if hasattr(module, 'cv2') and hasattr(module.cv2, 'conv'):
                out_ch = module.cv2.conv.out_channels
            elif hasattr(module, 'cv3') and hasattr(module.cv3, 'conv'):
                out_ch = module.cv3.conv.out_channels
            else:
                # fallback: 从参数形状推断
                for p in module.parameters():
                    out_ch = p.shape[0]
                    break

            # 计算合适的 reduction ratio
            reduction = 16 if out_ch >= 64 else max(out_ch // 4, 2)
            cbam = CBAM(out_ch, reduction=reduction)

            # 构建 Sequential: C2f → CBAM
            wrapped = nn.Sequential(module, cbam)
            # 复制 YOLO 元数据
            for attr in ['f', 'i', 'type']:
                if hasattr(module, attr):
                    setattr(wrapped, attr, getattr(module, attr))
            wrapped.f = module.f if hasattr(module, 'f') else -1
            wrapped.i = idx

            model.model.model[idx] = wrapped
            inserted += 1

            if verbose:
                print(f"  model.{idx}: +CBAM(ch={out_ch}, r={reduction})")

    if verbose:
        p = sum(p.numel() for p in model.model.parameters()) / 1e6
        print(f"  Inserted {inserted} CBAM, Params: {p:.2f}M")
    return model


if __name__ == '__main__':
    from ultralytics import YOLO

    print("=" * 60)
    print("YOLOv8n + CBAM Integration Test")
    print("=" * 60)

    model = YOLO('yolov8n.pt')
    orig = sum(p.numel() for p in model.model.parameters()) / 1e6
    print(f"Original: {orig:.2f}M")

    apply_cbam(model)

    # 验证
    dummy = torch.randn(1, 3, 640, 640)
    model.model.eval()
    with torch.no_grad():
        out = model.model(dummy)
    print(f"Forward OK: {type(out).__name__}")
    print("Done!")
