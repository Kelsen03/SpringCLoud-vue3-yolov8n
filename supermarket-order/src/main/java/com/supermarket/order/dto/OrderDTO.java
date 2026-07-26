package com.supermarket.order.dto;

import lombok.Data;
import java.util.List;

@Data
public class OrderDTO {
    private Long storeId;
    private Long memberId;
    private Boolean usePoints;
    private List<Item> items;

    @Data
    public static class Item {
        private Long productId;
        private java.math.BigDecimal price;
        private Integer quantity;
    }
}
