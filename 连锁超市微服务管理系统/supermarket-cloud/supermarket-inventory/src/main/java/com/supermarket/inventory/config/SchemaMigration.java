package com.supermarket.inventory.config;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Component;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import javax.annotation.PostConstruct;

@Component
public class SchemaMigration {
    @Autowired
    private JdbcTemplate jdbcTemplate;
    private static final Logger log = LoggerFactory.getLogger(SchemaMigration.class);

    @PostConstruct
    public void migrate() {
        try {
            Integer prodCol = jdbcTemplate.queryForObject(
                    "SELECT COUNT(*) FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'inventory' AND COLUMN_NAME = 'production_date'",
                    Integer.class);
            if (prodCol != null && prodCol == 0) {
                jdbcTemplate.execute("ALTER TABLE inventory ADD COLUMN production_date DATE");
            }
            Integer shelfCol = jdbcTemplate.queryForObject(
                    "SELECT COUNT(*) FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'inventory' AND COLUMN_NAME = 'shelf_life_months'",
                    Integer.class);
            if (shelfCol != null && shelfCol == 0) {
                jdbcTemplate.execute("ALTER TABLE inventory ADD COLUMN shelf_life_months INT");
            }
            
            // Add status column to stock_transfer table
            Integer statusCol = jdbcTemplate.queryForObject(
                    "SELECT COUNT(*) FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'stock_transfer' AND COLUMN_NAME = 'status'",
                    Integer.class);
            if (statusCol != null && statusCol == 0) {
                jdbcTemplate.execute("ALTER TABLE stock_transfer ADD COLUMN status VARCHAR(20) DEFAULT 'COMPLETED'");
            }
            
            jdbcTemplate.execute("UPDATE inventory SET production_date = '2025-06-10' WHERE production_date IS NULL");
            jdbcTemplate.execute("UPDATE inventory SET shelf_life_months = 24 WHERE shelf_life_months IS NULL AND (product_name LIKE '%抽纸%' OR product_name LIKE '%纸%' OR product_name LIKE '%牙膏%' OR product_name LIKE '%牙刷%' OR product_name LIKE '%个护%')");
            jdbcTemplate.execute("UPDATE inventory SET shelf_life_months = 12 WHERE shelf_life_months IS NULL");
            jdbcTemplate.execute("UPDATE inventory i JOIN supermarket_product.product p ON p.id = i.product_id SET i.product_name = p.name WHERE i.product_name IS NULL");
            Integer mismatches = jdbcTemplate.queryForObject("SELECT COUNT(*) FROM inventory i LEFT JOIN supermarket_product.product p ON p.id = i.product_id WHERE p.id IS NULL", Integer.class);
            if (mismatches != null && mismatches > 0) {
                log.warn("Inventory has {} product_id without matching product record", mismatches);
            }
        } catch (Exception ignore) {
        }
    }
}
