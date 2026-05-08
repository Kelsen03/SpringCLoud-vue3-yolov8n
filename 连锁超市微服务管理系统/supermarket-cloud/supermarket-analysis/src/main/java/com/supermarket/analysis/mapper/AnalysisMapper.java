package com.supermarket.analysis.mapper;

import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Select;
import java.util.List;
import java.util.Map;

@Mapper
public interface AnalysisMapper {

    // 1. 门店销售排行
    @Select("SELECT store_id, SUM(total_price) AS total_sales " +
            "FROM supermarket_order.`order` " +
            "GROUP BY store_id " +
            "ORDER BY total_sales DESC")
    List<Map<String, Object>> storeRank();

    // 2. 商品销量排行
    @Select("SELECT oi.product_id, p.name AS product_name, p.category, SUM(oi.quantity) AS total_quantity " +
            "FROM supermarket_order.order_item oi " +
            "JOIN supermarket_product.product p ON p.id = oi.product_id " +
            "GROUP BY oi.product_id, p.name, p.category " +
            "ORDER BY total_quantity DESC")
    List<Map<String, Object>> productRank();

    // 3. 补货建议 (近7天销量 > 当前库存)
    // Cross-database join: supermarket_inventory.inventory JOIN supermarket_order.order/order_item
    @Select("SELECT i.product_id, i.store_id, i.stock, SUM(oi.quantity) AS week_sales " +
            "FROM supermarket_inventory.inventory i " +
            "JOIN supermarket_order.order_item oi ON i.product_id = oi.product_id " +
            "JOIN supermarket_order.`order` o ON oi.order_id = o.id " +
            "WHERE o.create_time >= DATE_SUB(NOW(), INTERVAL 7 DAY) " +
            "GROUP BY i.product_id, i.store_id, i.stock " +
            "HAVING week_sales > i.stock")
    List<Map<String, Object>> replenishSuggest();

    @Select("SELECT o.store_id, " +
            "CASE " +
            "  WHEN p.category IN ('饮料','饮用水','乳制品') THEN '饮品' " +
            "  WHEN p.category IN ('方便面','熟食','生鲜') THEN '食品' " +
            "  WHEN p.category IN ('纸品','个护') THEN '生活用品' " +
            "  ELSE '其他' " +
            "END AS category, " +
            "SUM(oi.quantity) AS sales " +
            "FROM supermarket_order.order_item oi " +
            "JOIN supermarket_order.`order` o ON oi.order_id = o.id " +
            "JOIN supermarket_product.product p ON oi.product_id = p.id " +
            "GROUP BY o.store_id, category " +
            "ORDER BY o.store_id, sales DESC")
    List<Map<String, Object>> getRegionPreference();
}
