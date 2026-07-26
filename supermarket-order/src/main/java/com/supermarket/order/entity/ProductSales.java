package com.supermarket.order.entity;

import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

@Data
@TableName("product_sales")
public class ProductSales {
    private Long storeId;
    private Long productId;
    private Integer totalQuantity;
}
