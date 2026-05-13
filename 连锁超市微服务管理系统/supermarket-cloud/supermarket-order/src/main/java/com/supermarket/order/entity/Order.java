package com.supermarket.order.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.math.BigDecimal;
import java.util.Date;

@Data
@TableName("`order`")
public class Order {
    @TableId(type = IdType.AUTO)
    private Long id;
    private String orderNo;
    private Long storeId;
    private Long memberId;
    private BigDecimal totalPrice;
    private Integer points;
    private Date createTime;

    private String createBy;

    @TableField(exist = false)
    private String cashierAccount;
}
