package com.supermarket.order.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.math.BigDecimal;

@Data
@TableName("order_item")
public class OrderItem {
    @TableId(type = IdType.AUTO)
    private Long id;
    private Long orderId;
    private Long productId;
    
    // 加上这个注解，表示数据库表中不存在这个字段
    @TableField(exist = false)
    private String productName;
    
    // 加上这个注解，表示数据库表中不存在这个字段
    @TableField(exist = false)
    private String category;
    
    private BigDecimal price;
    private Integer quantity;
}
