package com.supermarket.order.entity;

import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

@Data
@TableName("member")
public class Member {
    @TableId
    private Long id;
    private Integer points;
}

