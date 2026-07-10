"""
DynamicConv Module - 动态卷积模块

基于王珏《基于YOLOv8n的遥感小目标检测方法》论文实现。
原理: 通过轻量门控网络动态生成K个卷积核的权重,对K个并行卷积输出加权求和。
替换YOLOv8n C2f中Bottleneck的标准卷积,增强特征提取的适应性。

Architecture:
    Input X → GAP → Flatten → Linear(C, C/r) → ReLU → Linear(C/r, K) → Sigmoid → [α1..αK]
    Input X → Conv1 → out1, Conv2 → out2, ... ConvK → outK
    Output Y = Σ αk * Convk(X)
"""

import torch
import torch.nn as nn
import torch.nn.functional as F


class DynamicConv2d(nn.Module):
    """
    动态卷积模块: K个并行卷积核 + 输入自适应门控权重 + 温度退火

    Args:
        in_ch: 输入通道数
        out_ch: 输出通道数
        kernel_size: 卷积核大小 (默认3)
        K: 并行卷积核数量 (默认4)
        r: 门控网络缩减比 (默认4)
        stride: 步长
        padding: 填充
        temperature: 初始温度 (默认30, 高温→软权重, 低温→硬选择)
    """
    def __init__(self, in_ch, out_ch, kernel_size=3, K=4, r=4, stride=1, padding=None, temperature=30.0):
        super().__init__()
        if padding is None:
            padding = kernel_size // 2

        self.K = K
        self.in_ch = in_ch
        self.out_ch = out_ch
        self.temperature = temperature

        # K 个并行卷积核
        self.convs = nn.ModuleList([
            nn.Conv2d(in_ch, out_ch, kernel_size, stride, padding, bias=False)
            for _ in range(K)
        ])

        # 门控网络
        hidden_dim = max(in_ch // r, 8)
        self.gap = nn.AdaptiveAvgPool2d(1)
        self.fc1 = nn.Linear(in_ch, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, K)
        self.sigmoid = nn.Sigmoid()

        # 初始化 fc2 为小随机值, 确保 K 个核有不同初始门控
        nn.init.normal_(self.fc2.weight, mean=0.0, std=0.01)
        nn.init.zeros_(self.fc2.bias)

        self.bn = nn.BatchNorm2d(out_ch)
        self.act = nn.SiLU()

    def forward(self, x):
        # 门控 (带温度)
        gate = self.gap(x).view(x.size(0), -1)         # [B, C]
        gate = F.relu(self.fc1(gate))                   # [B, C/r]
        gate = self.fc2(gate) / self.temperature        # 温度缩放
        gate = self.sigmoid(gate)                       # [B, K]

        # K 个卷积加权求和
        out = 0
        for k in range(self.K):
            conv_out = self.convs[k](x)
            out += gate[:, k].view(-1, 1, 1, 1) * conv_out

        out = self.bn(out)
        out = self.act(out)
        return out

    def set_temperature(self, T):
        """退火: 逐步降低温度, 让门控从软→硬"""
        self.temperature = max(T, 1.0)

    def extra_repr(self):
        return f'in={self.in_ch}, out={self.out_ch}, K={self.K}, T={self.temperature:.1f}'


if __name__ == '__main__':
    # 单元测试
    x = torch.randn(2, 64, 32, 32)
    conv = DynamicConv2d(64, 64, K=4, r=4)
    y = conv(x)
    print(f"Input:  {x.shape}")
    print(f"Output: {y.shape}")
    print(f"Params: {sum(p.numel() for p in conv.parameters()) / 1e3:.1f}K")

    # 验证门控权重
    gate = conv.sigmoid(conv.fc2(F.relu(conv.fc1(conv.gap(x).view(2, -1)))))
    print(f"Gate weights: {gate[0].detach().numpy()}")
    print(f"Gate sum (should be variable, not 1.0): {gate.sum(dim=1).detach().numpy()}")
