package com.supermarket.inventory.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import java.time.LocalDate;

@TableName("inventory")
public class Inventory {
    @TableId(type = IdType.AUTO)
    private Long id;
    private Long productId;
    private String productName;
    private Long storeId;
    private Integer stock;
    private Integer warningStock;
    private LocalDate productionDate;
    private Integer shelfLifeMonths;

    @TableField(exist = false)
    private Integer daysToExpire;

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
    public String getProductName() {
        return productName;
    }
    public void setProductName(String productName) {
        this.productName = productName;
    }
    public Long getStoreId() {
        return storeId;
    }
    public void setStoreId(Long storeId) {
        this.storeId = storeId;
    }
    public Integer getStock() {
        return stock;
    }
    public void setStock(Integer stock) {
        this.stock = stock;
    }
    public Integer getWarningStock() {
        return warningStock;
    }
    public void setWarningStock(Integer warningStock) {
        this.warningStock = warningStock;
    }
    public LocalDate getProductionDate() {
        return productionDate;
    }
    public void setProductionDate(LocalDate productionDate) {
        this.productionDate = productionDate;
    }
    public Integer getShelfLifeMonths() {
        return shelfLifeMonths;
    }
    public void setShelfLifeMonths(Integer shelfLifeMonths) {
        this.shelfLifeMonths = shelfLifeMonths;
    }
    public Integer getDaysToExpire() { return daysToExpire; }
    public void setDaysToExpire(Integer daysToExpire) { this.daysToExpire = daysToExpire; }
}
