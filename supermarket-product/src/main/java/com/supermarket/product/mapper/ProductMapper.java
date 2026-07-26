package com.supermarket.product.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.supermarket.product.entity.Product;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Select;

import java.util.List;
import java.util.Map;

@Mapper
public interface ProductMapper extends BaseMapper<Product> {

    @Select("SELECT p.id, p.name, p.category, p.price, p.promo_price, " +
            "COALESCE(ps.total_quantity, 0) AS sales " +
            "FROM product p " +
            "LEFT JOIN supermarket_order.product_sales ps ON p.id = ps.product_id " +
            "ORDER BY sales DESC, p.id ASC LIMIT 10")
    List<Map<String, Object>> findHotProducts();
}
