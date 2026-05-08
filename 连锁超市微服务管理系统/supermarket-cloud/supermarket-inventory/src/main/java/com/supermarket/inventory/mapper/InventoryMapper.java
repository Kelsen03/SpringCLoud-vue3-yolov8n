package com.supermarket.inventory.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.supermarket.inventory.entity.Inventory;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Delete;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Update;

@Mapper
public interface InventoryMapper extends BaseMapper<Inventory> {
    @Delete("DELETE FROM inventory WHERE store_id = #{storeId} AND product_id = #{productId}")
    int deleteByStoreAndProduct(@Param("storeId") Long storeId, @Param("productId") Long productId);

    @Update("UPDATE inventory SET stock = stock - #{count} WHERE product_id = #{productId} AND store_id = #{storeId} AND stock >= #{count}")
    int deductStock(@Param("productId") Long productId, @Param("storeId") Long storeId, @Param("count") Integer count);
}
