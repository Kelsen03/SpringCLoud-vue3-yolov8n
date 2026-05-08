package com.supermarket.inventory.dto;

import java.math.BigDecimal;

public class ReplenishRequest {
    private Long productId;
    private String productName;
    private String category;
    private BigDecimal price; // 新增价格字段
    private Long storeId;
    private Integer count;
    private String productionDate; // yyyy-MM-dd
    private Integer shelfLifeMonths;

    public Long getProductId() { return productId; }
    public void setProductId(Long productId) { this.productId = productId; }
    public String getProductName() { return productName; }
    public void setProductName(String productName) { this.productName = productName; }
    public String getCategory() { return category; }
    public void setCategory(String category) { this.category = category; }
    public BigDecimal getPrice() { return price; }
    public void setPrice(BigDecimal price) { this.price = price; }
    public Long getStoreId() { return storeId; }
    public void setStoreId(Long storeId) { this.storeId = storeId; }
    public Integer getCount() { return count; }
    public void setCount(Integer count) { this.count = count; }
    public String getProductionDate() { return productionDate; }
    public void setProductionDate(String productionDate) { this.productionDate = productionDate; }
    public Integer getShelfLifeMonths() { return shelfLifeMonths; }
    public void setShelfLifeMonths(Integer shelfLifeMonths) { this.shelfLifeMonths = shelfLifeMonths; }
}
