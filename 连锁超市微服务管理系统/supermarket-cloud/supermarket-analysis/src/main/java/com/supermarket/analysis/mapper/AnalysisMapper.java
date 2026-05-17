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

    // 3. 补货建议：缺货+临期优先排序
    @Select("SELECT i.product_id, i.product_name, i.store_id, i.stock, i.warning_stock, " +
            "i.production_date, i.shelf_life_months, " +
            "DATEDIFF(DATE_ADD(i.production_date, INTERVAL i.shelf_life_months MONTH), NOW()) AS days_to_expire, " +
            "COALESCE(s.week_sales, 0) AS week_sales " +
            "FROM supermarket_inventory.inventory i " +
            "LEFT JOIN (SELECT oi.product_id, o.store_id, SUM(oi.quantity) AS week_sales " +
            "  FROM supermarket_order.order_item oi " +
            "  JOIN supermarket_order.`order` o ON oi.order_id = o.id " +
            "  WHERE o.create_time >= DATE_SUB(NOW(), INTERVAL 7 DAY) " +
            "  GROUP BY oi.product_id, o.store_id) s ON i.product_id = s.product_id AND i.store_id = s.store_id " +
            "ORDER BY (i.stock <= i.warning_stock) DESC, " +
            "  (DATEDIFF(DATE_ADD(i.production_date, INTERVAL i.shelf_life_months MONTH), NOW()) < 30) DESC, " +
            "  i.stock ASC")
    List<Map<String, Object>> replenishSuggest();

    /** 补货推荐 v3 — 频率×单次销量 双因子加权
     *  ABC 分类在 Service 层 Java 计算
     */
    @Select("SELECT i.product_id, i.product_name, i.store_id, i.stock, i.warning_stock, " +
            "i.production_date, i.shelf_life_months, " +
            "DATEDIFF(DATE_ADD(i.production_date, INTERVAL i.shelf_life_months MONTH), NOW()) AS days_to_expire, " +
            "COALESCE(ROUND(s.total_sales / 14.0, 1), 0) AS daily_sales, " +
            "COALESCE(s.sales_days, 0) AS sales_days, " +
            "COALESCE(ROUND(s.total_sales / GREATEST(s.order_cnt, 1), 0), 0) AS avg_qty, " +
            "s.total_sales, " +
            "CASE WHEN COALESCE(s.total_sales, 0) > 0 THEN " +
            "  GREATEST(i.warning_stock * 3 - i.stock, " +
            "    ROUND((s.total_sales / 14.0) * 10 * " +
            "      (1 + (s.sales_days / 14.0) + LEAST((s.total_sales / GREATEST(s.order_cnt, 1)) / 10.0, 1.0)) " +
            "    - i.stock)) " +
            "  ELSE GREATEST(0, i.warning_stock * 5 - i.stock) " +
            "END AS recommend_qty " +
            "FROM supermarket_inventory.inventory i " +
            "LEFT JOIN (SELECT oi.product_id, o.store_id, SUM(oi.quantity) AS total_sales, " +
            "  COUNT(DISTINCT DATE(o.create_time)) AS sales_days, COUNT(DISTINCT o.id) AS order_cnt " +
            "FROM supermarket_order.order_item oi " +
            "JOIN supermarket_order.`order` o ON oi.order_id = o.id " +
            "WHERE o.create_time >= DATE_SUB(NOW(), INTERVAL 14 DAY) " +
            "GROUP BY oi.product_id, o.store_id) s ON i.product_id = s.product_id AND i.store_id = s.store_id " +
            "ORDER BY (i.stock <= i.warning_stock) DESC, recommend_qty DESC, i.stock ASC")
    List<Map<String, Object>> replenishRecommend();

    @Select("SELECT o.store_id, " +
            "CASE " +
            "  WHEN p.category = '饮品' THEN '饮品' " +
            "  WHEN p.category = '乳制品' THEN '乳制品' " +
            "  WHEN p.category IN ('零食','方便食品','冷冻食品','谷物早餐','烘焙面点','主食粮谷','罐头食品','干货特产') THEN '食品' " +
            "  WHEN p.category IN ('纸品个护','家居清洁','日杂百货') THEN '日用品' " +
            "  WHEN p.category = '调味品' THEN '调味品' " +
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
