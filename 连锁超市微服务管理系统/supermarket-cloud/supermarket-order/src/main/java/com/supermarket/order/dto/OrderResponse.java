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
    private String orderNo;
    private Integer points;
    private Integer totalPoints;

    private List<OrderItem> items;

    private Date createTime;
    private BigDecimal totalPrice;
    private Long memberId;
    private String createBy;

    public OrderResponse(Long orderId, Integer points, Integer totalPoints) {
        this.orderId = orderId;
        this.points = points;
        this.totalPoints = totalPoints;
    }
}

