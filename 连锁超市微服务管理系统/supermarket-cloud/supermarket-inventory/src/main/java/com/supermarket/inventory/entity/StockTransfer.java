package com.supermarket.inventory.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import java.time.LocalDateTime;

@TableName("stock_transfer")
public class StockTransfer {
    @TableId(type = IdType.AUTO)
    private Long id;
    private Long productId;
    private Long fromStore;
    private Long toStore;
    private Integer quantity;
    private LocalDateTime createTime;

    public Long getId() {
        return id;
    }
    public void setId(Long id) {
        this.id = id;
    }
    public Long getProductId() {
        return productId;
    }
    public void setProductId(Long productId) {
        this.productId = productId;
    }
    public Long getFromStore() {
        return fromStore;
    }
    public void setFromStore(Long fromStore) {
        this.fromStore = fromStore;
    }
    public Long getToStore() {
        return toStore;
    }
    public void setToStore(Long toStore) {
        this.toStore = toStore;
    }
    public Integer getQuantity() {
        return quantity;
    }
    public void setQuantity(Integer quantity) {
        this.quantity = quantity;
    }
    public LocalDateTime getCreateTime() {
        return createTime;
    }
    public void setCreateTime(LocalDateTime createTime) {
        this.createTime = createTime;
    }
}
