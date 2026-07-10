"""
CBAM (Convolutional Block Attention Module) for YOLOv8n

通道注意力: 关注"什么特征重要" → 区分相似包装
空间注意力: 关注"哪里重要" → 聚焦标签/logo区域

参数量增加 <2%, 专门适合零售商品细粒度识别
"""
import torch
import torch.nn as nn
import torch.nn.functional as F


class ChannelAttention(nn.Module):
    """通道注意力: GAP+GMP → 共享MLP → 通道权重"""
    def __init__(self, channels, reduction=16):
        super().__init__()
        self.gap = nn.AdaptiveAvgPool2d(1)
        self.gmp = nn.AdaptiveMaxPool2d(1)
        self.mlp = nn.Sequential(
            nn.Conv2d(channels, channels // reduction, 1, bias=False),
            nn.ReLU(),
            nn.Conv2d(channels // reduction, channels, 1, bias=False),
        )
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        avg = self.mlp(self.gap(x))
        max = self.mlp(self.gmp(x))
        return self.sigmoid(avg + max)


class SpatialAttention(nn.Module):
    """空间注意力: 通道池化 → 7x7Conv → 空间权重"""
    def __init__(self, kernel_size=7):
        super().__init__()
        self.conv = nn.Conv2d(2, 1, kernel_size, padding=kernel_size//2, bias=False)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        avg = torch.mean(x, dim=1, keepdim=True)
        max, _ = torch.max(x, dim=1, keepdim=True)
        return self.sigmoid(self.conv(torch.cat([avg, max], dim=1)))


class CBAM(nn.Module):
    """CBAM: 通道注意力 + 空间注意力"""
    def __init__(self, channels, reduction=16, spatial_kernel=7):
        super().__init__()
        self.ca = ChannelAttention(channels, reduction)
        self.sa = SpatialAttention(spatial_kernel)

    def forward(self, x):
        x = x * self.ca(x)       # 通道加权
        x = x * self.sa(x)       # 空间加权
        return x


if __name__ == '__main__':
    x = torch.randn(2, 64, 80, 80)
    cbam = CBAM(64, reduction=16)
    y = cbam(x)
    print(f"Input:  {x.shape}")
    print(f"Output: {y.shape}")
    print(f"Params: {sum(p.numel() for p in cbam.parameters())/1e3:.1f}K")
