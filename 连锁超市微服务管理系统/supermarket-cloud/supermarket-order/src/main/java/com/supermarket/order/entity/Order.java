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
    private Long storeId;
    private Long memberId;
    private BigDecimal totalPrice;
    private Integer points;
    private Date createTime;
    
    // 【新增】记录收银员账号 (映射到数据库的 create_by 字段)
    private String createBy;
    
    // 前端为了显示收银员，加上这个注解，表示数据库表中不存在这个字段，但在返回时可以用
    @TableField(exist = false)
    private String cashierAccount;
}
