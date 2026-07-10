"""
ATGA (Adaptive Texture-Gated Attention) — 自适应纹理门控注意力

创新点: 针对收银台商品识别中透明瓶身(脉动/农夫山泉/雪碧)RGB特征不可靠的问题,
引入可学习边缘检测器作为纹理分支, 通过通道级门控网络动态融合 RGB 和纹理特征。

与现有方案的区别:
  CBAM:    固定通道+空间注意力, 不区分特征来源
  DynamicConv: 输入自适应卷积核, 针对尺度变化, 参数量大
  ATGA:    输入自适应特征融合(RGB↔纹理), 针对透明/反光商品, 参数量小

结构:
  Input X
    ├→ RGB分支: Conv(X) → X_rgb
    ├→ 纹理分支: LearnableEdge(X) → Conv → X_edge
    └→ 门控: GAP(X) → FC → Sigmoid → α (per-channel)
  Output: α·X_rgb + (1-α)·X_edge
"""

import torch
import torch.nn as nn
import torch.nn.functional as F


class LearnableEdgeDetector(nn.Module):
    """
    可学习边缘检测器 — 替代手工 Canny

    学习 4 个方向 (0°/45°/90°/135°) 的可微分 sobel-like 核,
    模型自适应学习最优边缘提取方向, 输出单通道边缘图。

    比手工 Canny 优势:
    - 端到端可微分训练
    - 自动学习最适合透明瓶身的边缘方向
    - 不受固定阈值限制
    """
    def __init__(self, channels):
        super().__init__()
        # 4 个可学习方向核: 水平/垂直/对角/反斜对
        self.direction_weights = nn.Parameter(torch.ones(4) / 4)
        # 可学习阈值 (替代 Canny 50/150)
        self.edge_scale = nn.Parameter(torch.tensor(1.0))

        # 初始化 sobel-like 核
        sobel_x = torch.tensor([[-1,0,1],[-2,0,2],[-1,0,1]], dtype=torch.float32) / 4.0
        sobel_y = torch.tensor([[-1,-2,-1],[0,0,0],[1,2,1]], dtype=torch.float32) / 4.0
        sobel_d1 = torch.tensor([[-2,-1,0],[-1,0,1],[0,1,2]], dtype=torch.float32) / 4.0
        sobel_d2 = torch.tensor([[0,1,2],[-1,0,1],[-2,-1,0]], dtype=torch.float32) / 4.0

        self.register_buffer('k0', sobel_x.view(1,1,3,3))
        self.register_buffer('k1', sobel_y.view(1,1,3,3))
        self.register_buffer('k2', sobel_d1.view(1,1,3,3))
        self.register_buffer('k3', sobel_d2.view(1,1,3,3))

        # 可学习边缘增强卷积
        self.enhance = nn.Sequential(
            nn.Conv2d(4, 1, 1, bias=False),
            nn.Sigmoid()
        )

    def forward(self, x):
        B, C, H, W = x.shape
        # 对每个通道独立做边缘检测
        x_flat = x.view(B * C, 1, H, W)

        g0 = F.conv2d(x_flat, self.k0, padding=1)
        g1 = F.conv2d(x_flat, self.k1, padding=1)
        g2 = F.conv2d(x_flat, self.k2, padding=1)
        g3 = F.conv2d(x_flat, self.k3, padding=1)

        # 4方向加权融合 → 方向权重可学习
        w = F.softmax(self.direction_weights, dim=0)
        edge = w[0]*g0 + w[1]*g1 + w[2]*g2 + w[3]*g3

        # 堆叠 4 方向, 用 1×1 Conv 学习最优融合
        stacked = torch.cat([g0, g1, g2, g3], dim=1)  # (B*C, 4, H, W)
        edge_map = self.enhance(stacked).view(B, C, H, W)  # (B, C, H, W)

        return edge_map.abs() * self.edge_scale


class ATGA(nn.Module):
    """
    自适应纹理门控注意力

    Args:
        channels: 输入通道数
        reduction: 门控网络缩减比 (默认8)
    """
    def __init__(self, channels, reduction=8):
        super().__init__()
        hidden = max(channels // reduction, 4)

        # RGB 分支: 标准 3×3 Conv
        self.rgb_conv = nn.Sequential(
            nn.Conv2d(channels, channels, 3, 1, 1, groups=channels, bias=False),
            nn.Conv2d(channels, channels, 1, bias=False),
            nn.BatchNorm2d(channels),
            nn.SiLU()
        )

        # 纹理分支: LearnableEdge → Conv
        self.edge_detector = LearnableEdgeDetector(channels)
        self.edge_conv = nn.Sequential(
            nn.Conv2d(channels, channels, 3, 1, 1, groups=channels, bias=False),
            nn.Conv2d(channels, channels, 1, bias=False),
            nn.BatchNorm2d(channels),
            nn.SiLU()
        )

        # 门控网络: 输入 → 逐通道 α
        self.gap = nn.AdaptiveAvgPool2d(1)
        self.fc = nn.Sequential(
            nn.Linear(channels, hidden),
            nn.ReLU(),
            nn.Linear(hidden, channels),
            nn.Sigmoid()      # α ∈ [0,1]
        )

        # 残差连接
        self.residual = nn.Conv2d(channels, channels, 1) if True else nn.Identity()
        self.act = nn.SiLU()

    def forward(self, x):
        identity = x

        # RGB 分支
        x_rgb = self.rgb_conv(x)

        # 纹理分支
        edge = self.edge_detector(x)
        x_edge = self.edge_conv(x * edge)  # 用边缘图加权输入

        # 门控: 逐通道 α
        alpha = self.gap(x).view(x.size(0), -1)
        alpha = self.fc(alpha).view(x.size(0), -1, 1, 1)  # (B, C, 1, 1)

        # 自适应融合
        out = alpha * x_rgb + (1 - alpha) * x_edge

        # 残差
        out = out + identity
        out = self.act(out)
        return out


if __name__ == '__main__':
    # 测试
    x = torch.randn(2, 64, 80, 80)
    atga = ATGA(64, reduction=8)
    y = atga(x)

    print(f"Input:      {x.shape}")
    print(f"Output:     {y.shape}")
    print(f"Params:     {sum(p.numel() for p in atga.parameters())/1e3:.1f}K")
    print(f"Parameters: {dict(atga.named_parameters()).keys()}")

    # 验证门控分布
    with torch.no_grad():
        edge_map = atga.edge_detector(x)
        alpha = atga.fc(atga.gap(x).view(2, -1)).view(2, -1)
        print(f"\nEdge map:   mean={edge_map.mean():.3f}, std={edge_map.std():.3f}")
        print(f"Alpha gate: mean={alpha.mean():.3f}, std={alpha.std():.3f}")
        print(f"  (α→1=信任RGB, α→0=信任纹理)")
