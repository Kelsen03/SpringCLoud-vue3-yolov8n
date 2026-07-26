package com.supermarket.order.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.math.BigDecimal;
import java.util.Date;

/** 收银员换班记录 */
@Data
@TableName("shift_record")
public class ShiftRecord {
    @TableId(type = IdType.AUTO)
    private Long id;
    private Long storeId;
    private String cashierUsername;
    private Date shiftStart;
    private Date shiftEnd;
    private BigDecimal openingCash;  // 开班备用金（找零用）
    private BigDecimal closingCash;  // 交班时实际清点的现金
    private BigDecimal systemCash;   // 系统记录现金收款
    private BigDecimal systemOnline; // 系统记录在线支付
    private Integer totalOrders;
    private String status;           // ACTIVE / CLOSED
    private String remark;
}
