package com.supermarket.order.dto;

import com.supermarket.order.entity.OrderItem;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.util.Date;
import java.util.List;

@Data
@AllArgsConstructor
@NoArgsConstructor
public class OrderResponse {
    private Long orderId;
    private Integer points;
    private Integer totalPoints;
    
    // 用于详情接口，包含订单明细
    private List<OrderItem> items;
    
    // 扩展字段，方便前端渲染小票
    private Date createTime;
    private BigDecimal totalPrice;
    private Long memberId;
    private String createBy; // 增加返回收银员账号
    
    public OrderResponse(Long orderId, Integer points, Integer totalPoints) {
        this.orderId = orderId;
        this.points = points;
        this.totalPoints = totalPoints;
    }
}

