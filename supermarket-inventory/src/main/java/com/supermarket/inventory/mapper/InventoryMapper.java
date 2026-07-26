package com.supermarket.inventory.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.supermarket.inventory.entity.Inventory;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Delete;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;
import org.apache.ibatis.annotations.Update;

import java.util.List;

@Mapper
public interface InventoryMapper extends BaseMapper<Inventory> {

    @Delete("DELETE FROM inventory WHERE store_id = #{storeId} AND product_id = #{productId}")
    int deleteByStoreAndProduct(@Param("storeId") Long storeId, @Param("productId") Long productId);

    @Update("UPDATE inventory SET stock = stock - #{count} WHERE product_id = #{productId} AND store_id = #{storeId} AND stock >= #{count}")
    int deductStock(@Param("productId") Long productId, @Param("storeId") Long storeId, @Param("count") Integer count);

    /** 库存列表：过期→临期→缺货→正常排序 */
    @Select("SELECT *, " +
            "DATEDIFF(DATE_ADD(production_date, INTERVAL COALESCE(shelf_life_months,12) MONTH), NOW()) AS days_to_expire " +
            "FROM inventory " +
            "WHERE store_id = #{storeId} " +
            "ORDER BY " +
            "  (DATEDIFF(DATE_ADD(production_date, INTERVAL COALESCE(shelf_life_months,12) MONTH), NOW()) < 0) DESC, " +
            "  (DATEDIFF(DATE_ADD(production_date, INTERVAL COALESCE(shelf_life_months,12) MONTH), NOW()) BETWEEN 0 AND 30) DESC, " +
            "  (stock <= warning_stock) DESC, " +
            "  stock ASC")
    List<Inventory> listSorted(@Param("storeId") Long storeId);
}
