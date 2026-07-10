"""
YOLOv8n-DynamicConv v4 — C2f Bottleneck cv1 替换 + 温度退火
"""
import torch
import torch.nn as nn
from ultralytics.nn.modules import C2f
from dynamic_conv import DynamicConv2d


def apply_dynamic_conv(model, verbose=True, K=4):
    """
    YOLOv8n C2f Bottleneck cv1 → DynamicConv2d
    仅替换深层 C2f (128+通道)
    """
    DEEP_MODULES = {'model.8', 'model.12', 'model.15', 'model.18', 'model.21'}
    COUNT = 0

    # 先获取所有 c1/c2 信息 (避免遍历时修改)
    replacements = []
    for name, module in model.model.named_modules():
        if isinstance(module, C2f) and name in DEEP_MODULES:
            for i, bn in enumerate(module.m):
                if hasattr(bn, 'cv1') and hasattr(bn.cv1, 'conv'):
                    # 直接从旧权重获取精确的 in/out 通道
                    old_cv1_w = bn.cv1.conv.weight
                    out_ch = old_cv1_w.shape[0]  # 输出通道
                    in_ch = old_cv1_w.shape[1]   # 输入通道
                    # c2 从 cv2 获取
                    if hasattr(bn.cv2, 'conv'):
                        c2 = bn.cv2.conv.out_channels
                    elif isinstance(bn.cv2, nn.Sequential) and isinstance(bn.cv2[0], nn.Conv2d):
                        c2 = bn.cv2[0].out_channels
                    else:
                        c2 = out_ch * 2  # 默认 c2 = 2*c_
                    shortcut = bn.add if hasattr(bn, 'add') else (in_ch == c2)
                    replacements.append((name, i, in_ch, out_ch, c2, shortcut, old_cv1_w, bn.cv1.bn, bn.cv2))

    # 执行替换
    for name, i, in_ch, out_ch, c2, shortcut, old_w, old_bn_state, old_cv2 in replacements:
        K_actual = min(K, 4)

        # 构建新 Bottleneck: cv1=DynamicConv, cv2=标准Conv
        class _DynamicBN(nn.Module):
            def __init__(self):
                super().__init__()
                self.cv1 = DynamicConv2d(in_ch, out_ch, 3, K=K_actual, temperature=30.0)
                self.cv2 = nn.Sequential(
                    nn.Conv2d(out_ch, c2, 3, 1, 1, bias=False),
                    nn.BatchNorm2d(c2),
                    nn.SiLU()
                )
                self.add = shortcut
            def forward(self, x):
                return x + self.cv2(self.cv1(x)) if self.add else self.cv2(self.cv1(x))

        new_bn = _DynamicBN()

        # 权重迁移
        with torch.no_grad():
            for k in range(K_actual):
                new_bn.cv1.convs[k].weight.data.copy_(old_w)
            new_bn.cv1.bn.load_state_dict(old_bn_state.state_dict())
            # cv2 迁移 (兼容 Conv 和 Sequential)
            if hasattr(old_cv2, 'conv'):
                new_bn.cv2[0].weight.data.copy_(old_cv2.conv.weight.data)
                new_bn.cv2[1].load_state_dict(old_cv2.bn.state_dict())
            else:
                new_bn.cv2.load_state_dict(old_cv2.state_dict())

        # 替换
        for n2, m2 in model.model.named_modules():
            if n2 == name and isinstance(m2, C2f):
                m2.m[i] = new_bn
                COUNT += 1
                break

        if verbose:
            print(f"  {name}.m[{i}]: {in_ch}x{out_ch}→{c2}, K={K_actual}")

    if verbose:
        p = sum(p.numel() for p in model.model.parameters()) / 1e6
        print(f"  Replaced: {COUNT}, Params: {p:.2f}M")
    return model


def set_temperature(model, T):
    """退火: 降低所有 DynamicConv2d 的温度"""
    for m in model.modules():
        if isinstance(m, DynamicConv2d):
            m.set_temperature(T)


if __name__ == '__main__':
    from ultralytics import YOLO
    print("=" * 60)
    print("DynamicConv v4 Integration Test (C2f + Temperature)")
    print("=" * 60)

    model = YOLO('yolov8n.pt')
    orig = sum(p.numel() for p in model.model.parameters()) / 1e6
    print(f"Original: {orig:.2f}M")

    apply_dynamic_conv(model, K=4)
    set_temperature(model, 30.0)

    # Verify
    dummy = torch.randn(1, 3, 640, 640)
    model.model.eval()
    with torch.no_grad():
        out = model.model(dummy)
    print(f"Forward OK: {type(out).__name__}")
    print("Done!")
