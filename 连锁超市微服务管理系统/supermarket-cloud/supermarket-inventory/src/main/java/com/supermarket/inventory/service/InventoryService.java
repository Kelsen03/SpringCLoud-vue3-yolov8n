package com.supermarket.inventory.service;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.supermarket.inventory.entity.Inventory;
import com.supermarket.inventory.mapper.InventoryMapper;
import com.supermarket.inventory.dto.ReplenishRequest;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.List;
import java.util.Map;
import org.springframework.jdbc.core.JdbcTemplate;

@Service
public class InventoryService {
    @Autowired
    private InventoryMapper inventoryMapper;
    @Autowired
    private JdbcTemplate jdbcTemplate;

    public String replenish(Long productId, Long storeId, Integer count) {
        if (count == null || count <= 0) return "补货数量必须大于0";
        Inventory inv = inventoryMapper.selectOne(new QueryWrapper<Inventory>()
                .eq("store_id", storeId)
                .eq("product_id", productId));
        if (inv == null) {
            Inventory newInv = new Inventory();
            newInv.setProductId(productId);
            newInv.setStoreId(storeId);
            newInv.setStock(count);
            newInv.setWarningStock(10);
            newInv.setShelfLifeMonths(12);
            inventoryMapper.insert(newInv);
        } else {
            inv.setStock(inv.getStock() + count);
            inventoryMapper.updateById(inv);
        }
        return "ok";
    }

    public String replenishFull(ReplenishRequest req) {
        if (req.getCount() == null || req.getCount() <= 0) return "补货数量必须大于0";
        Integer months = req.getShelfLifeMonths();
        if (months == null) {
            String cat = req.getCategory();
            if (cat != null) {
                if (cat.contains("饮料") || cat.contains("饮用水") || cat.contains("乳制品")) {
                    months = 12;
                } else if (cat.contains("方便面") || cat.contains("熟食") || cat.contains("生鲜")) {
                    months = 12;
                } else if (cat.contains("纸品") || cat.contains("个护")) {
                    months = 24;
                } else {
                    months = 12;
                }
            } else {
                months = 12;
            }
        }
        LocalDate pdate = null;
        if (req.getProductionDate() != null && !req.getProductionDate().isEmpty()) {
            pdate = LocalDate.parse(req.getProductionDate(), DateTimeFormatter.ISO_DATE);
        }
        Inventory inv = inventoryMapper.selectOne(new QueryWrapper<Inventory>()
                .eq("store_id", req.getStoreId())
                .eq("product_id", req.getProductId()));
        Integer exists = jdbcTemplate.queryForObject(
                "SELECT COUNT(*) FROM supermarket_product.product WHERE id = ?",
                Integer.class, req.getProductId());
        if (exists != null && exists == 0) {
            jdbcTemplate.update(
                    "INSERT INTO supermarket_product.product (id, name, category, price, promo_price, is_local, store_id) VALUES (?,?,?,?,?,?,?)",
                    req.getProductId(),
                    req.getProductName(),
                    req.getCategory(),
                    req.getPrice() != null ? req.getPrice() : BigDecimal.ZERO, // 修复：防止价格为NULL导致前端不显示
                    null,
                    1,
                    req.getStoreId()
            );
        } else {
            // 【新增逻辑】如果商品已存在，尝试修复可能缺失的价格或更新名称
            // 仅当价格为NULL时才更新价格，防止覆盖已有的定价
            jdbcTemplate.update(
                    "UPDATE supermarket_product.product SET price = IFNULL(price, ?), name = ? WHERE id = ?",
                    req.getPrice() != null ? req.getPrice() : BigDecimal.ZERO,
                    req.getProductName(),
                    req.getProductId()
            );
        }
        if (inv == null) {
            inv = new Inventory();
            inv.setProductId(req.getProductId());
            inv.setProductName(req.getProductName());
            inv.setStoreId(req.getStoreId());
            inv.setStock(req.getCount());
            inv.setWarningStock(10);
            inv.setProductionDate(pdate);
            inv.setShelfLifeMonths(months);
            inventoryMapper.insert(inv);
        } else {
            inv.setStock(inv.getStock() + req.getCount());
            if (req.getProductName() != null && !req.getProductName().isEmpty()) {
                inv.setProductName(req.getProductName());
            }
            if (pdate != null) inv.setProductionDate(pdate);
            inv.setShelfLifeMonths(months);
            inventoryMapper.updateById(inv);
        }

        // 记录补货流水
        jdbcTemplate.update(
            "INSERT INTO replenish_record (product_id, product_name, category, store_id, count, production_date, shelf_life_months) VALUES (?,?,?,?,?,?,?)",
            req.getProductId(), req.getProductName(), req.getCategory(), req.getStoreId(), req.getCount(), pdate, months
        );

        return "ok";
    }

    public List<Map<String, Object>> getReplenishHistory(Long storeId) {
        if (storeId != null && storeId > 0) {
            return jdbcTemplate.queryForList("SELECT * FROM replenish_record WHERE store_id = ? ORDER BY create_time DESC LIMIT 100", storeId);
        }
        return jdbcTemplate.queryForList("SELECT * FROM replenish_record ORDER BY create_time DESC LIMIT 100");
    }

    public String clearInventory(Long storeId, Long productId) {
        Inventory inv = inventoryMapper.selectOne(new QueryWrapper<Inventory>()
                .eq("store_id", storeId).eq("product_id", productId));
        if (inv == null) return "库存不存在";
        inv.setStock(0);
        inventoryMapper.updateById(inv);
        return "ok";
    }

    public String deleteInventory(Long storeId, Long productId) {
        int rows = inventoryMapper.deleteByStoreAndProduct(storeId, productId);
        return rows > 0 ? "ok" : "库存不存在";
    }

    /**
     * 确保目标门店能看到该商品
     * 如果是私有商品调拨，且目标门店没有该商品档案，则自动复制一份
     */
    public void ensureProductVisibility(Long toStoreId, Long productId, String productName) {
        try {
            // 1. 检查商品是否对目标门店可见
            // 可见条件：(is_local = 0) OR (is_local = 1 AND store_id = toStoreId)
            Integer visible = jdbcTemplate.queryForObject(
                "SELECT COUNT(*) FROM supermarket_product.product WHERE id = ? AND (is_local = 0 OR (is_local = 1 AND store_id = ?))",
                Integer.class, productId, toStoreId);

            if (visible != null && visible > 0) {
                return; // 已经可见，无需处理
            }

            // 2. 如果不可见，说明这是一个“其他门店的私有商品”被调拨过来了
            System.out.println("Auto-fix: Product " + productId + " is not visible to store " + toStoreId + ". Upgrading to global.");

            // 解决方案：将该商品升级为“全局商品” (is_local=0)，这样所有门店都能卖。
            // 同时更新商品名称，确保列表显示正常
            int rows = jdbcTemplate.update(
                "UPDATE supermarket_product.product SET is_local = 0, store_id = NULL, name = IFNULL(name, ?) WHERE id = ?",
                productName, productId
            );
            
            if (rows > 0) {
                System.out.println("Auto-fix success: Product " + productId + " is now global.");
            } else {
                System.err.println("Auto-fix failed: Product " + productId + " update affected 0 rows.");
            }
        } catch (Exception e) {
            // 记录错误但暂时不阻断流程，避免回滚库存
            e.printStackTrace();
            System.err.println("Failed to ensure product visibility: " + e.getMessage());
        }
    }
}
