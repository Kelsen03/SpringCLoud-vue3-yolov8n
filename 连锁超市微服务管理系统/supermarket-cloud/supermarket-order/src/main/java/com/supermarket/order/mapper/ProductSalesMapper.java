package com.supermarket.order.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.supermarket.order.entity.ProductSales;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Update;

@Mapper
public interface ProductSalesMapper extends BaseMapper<ProductSales> {
    @Update("INSERT INTO product_sales (store_id, product_id, total_quantity) VALUES (#{storeId}, #{productId}, #{qty}) " +
            "ON DUPLICATE KEY UPDATE total_quantity = total_quantity + #{qty}")
    int upsertAdd(@Param("storeId") Long storeId, @Param("productId") Long productId, @Param("qty") Integer qty);
}

