package com.supermarket.inventory.controller;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.supermarket.inventory.entity.Inventory;
import com.supermarket.inventory.entity.StockTransfer;
import com.supermarket.inventory.mapper.InventoryMapper;
import com.supermarket.inventory.mapper.StockTransferMapper;
import com.supermarket.inventory.service.InventoryService;
import com.supermarket.inventory.dto.ReplenishRequest;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.List;

import org.springframework.transaction.annotation.Transactional;

import java.util.concurrent.CompletableFuture;

@RestController
@RequestMapping("/inventory")
public class InventoryController {

    @Autowired
    private InventoryMapper inventoryMapper;

    @Autowired
    private StockTransferMapper transferMapper;

    @Autowired
    private InventoryService inventoryService;

    /**
     * 扣减库存接口
     * 给订单服务调用，下单时自动扣减对应门店的商品库存
     *
     * @param productId 商品ID
     * @param storeId   门店ID
     * @param count     扣减数量
     * @return "ok" 成功, "库存不足" 失败
     */
    @PostMapping("/deduct")
    public String deduct(@RequestParam Long productId,
                         @RequestParam Long storeId,
                         @RequestParam Integer count) {
        // 使用 Mapper 的原子更新方法
        int rows = inventoryMapper.deductStock(productId, storeId, count);
        if (rows > 0) {
            return "ok";
        }
        return "库存不足";
    }

    /**
     * 库存查询接口
     * 前端根据返回的 stock 和 warningStock 判断是否显示“缺货预警”
     *
     * @param storeId 门店ID
     * @return 库存列表
     */
    @GetMapping("/list")
    public List<Inventory> list(@RequestParam Long storeId) {
        return inventoryMapper.selectList(new QueryWrapper<Inventory>()
                .eq("store_id", storeId));
    }
    @GetMapping("/listAll")
    public List<Inventory> listAll() {
        return inventoryMapper.selectList(new QueryWrapper<>());
    }

    /**
     * 门店库存调拨接口
     * 实现 "门店A -> 门店B" 的库存转移
     * 逻辑：A店扣减 -> B店增加 -> 记录流水
     * 注意：这里采用业务逻辑控制一致性（简化版），未引入分布式事务
     *
     * @param productId 商品ID
     * @param fromStore 调出门店
     * @param toStore   调入门店
     * @param count     调拨数量
     * @return "ok" 成功
     */
    // 记录旧库存数量，用于虚拟批次逻辑
    private static final String BATCH_KEY_PREFIX = "batch_stock:";

    @PostMapping("/transfer")
    @Transactional(rollbackFor = Exception.class)
    public String transfer(@RequestParam Long productId,
                           @RequestParam Long fromStore,
                           @RequestParam Long toStore,
                           @RequestParam Integer count) {

        // 【新增步骤】0. 先获取源库存信息（为了后面复制生产日期等详情）
        Inventory fromInv = inventoryMapper.selectOne(new QueryWrapper<Inventory>()
                .eq("product_id", productId)
                .eq("store_id", fromStore));

        if (fromInv == null || fromInv.getStock() < count) {
            return "库存不足";
        }

        // 1. 从调出门店（A店）扣减库存
        String deductResult = deduct(productId, fromStore, count);
        if (!"ok".equals(deductResult)) {
            return deductResult;
        }

        // 2. 增加调入门店（B店）库存
        Inventory toInv = inventoryMapper.selectOne(new QueryWrapper<Inventory>()
                .eq("product_id", productId)
                .eq("store_id", toStore));

        if (toInv == null) {
            // 如果B店没有该商品库存记录，则新建
            toInv = new Inventory();
            toInv.setProductId(productId);
            toInv.setStoreId(toStore);
            toInv.setStock(count);
            toInv.setWarningStock(10); // 默认预警阈值

            // 【核心修复】复制源商品的元数据（生产日期、保质期、名称）
            // 只有加上这三行，调拨过去的商品日期才会和原来的一致！
            toInv.setProductName(fromInv.getProductName());
            toInv.setProductionDate(fromInv.getProductionDate());
            toInv.setShelfLifeMonths(fromInv.getShelfLifeMonths());

            inventoryMapper.insert(toInv);
        } else {
            // 如果已有记录，直接累加
            int oldStock = toInv.getStock();
            toInv.setStock(oldStock + count);

            // 【高级逻辑】处理生产日期不一致的情况 (模拟FIFO显示)
            if (fromInv.getProductionDate() != null) {
                // 如果调入的是新货（日期晚于现有库存），且当前库存还有货
                if (toInv.getProductionDate() != null && fromInv.getProductionDate().isAfter(toInv.getProductionDate())) {
                    // 此时不更新日期，保持旧日期（让旧货先卖）。
                    // 但我们需要记录一个“虚拟批次”标记（这里简化处理，仅做注释说明逻辑）
                    // 实际逻辑：当旧货（oldStock）卖完时，系统应自动更新日期。
                    // 由于没有批次表，我们利用一个暂存字段或备注来记录（这里假设Inventory表有扩展字段或逻辑支持，
                    // 若无，则只能维持“显示较旧日期”的安全策略，直到再次人工盘点或调拨更新）。
                    
                    // 当前策略：保持显示旧日期（符合“就低不就高”原则）。
                    // 当未来某次库存扣减导致 quantity <= count (即旧货卖完了) 时，
                    // 理论上应该触发日期更新。但由于HTTP无状态且无批次表，
                    // 无法自动精确做到“卖完瞬间变日期”。
                    
                    // 妥协方案：不做任何日期变更，维持 toInv 原有的旧日期。
                } 
                // 如果调入的是旧货（日期早于现有库存）
                else if (toInv.getProductionDate() == null || fromInv.getProductionDate().isBefore(toInv.getProductionDate())) {
                    // 必须更新为更早的日期（安全第一）
                    toInv.setProductionDate(fromInv.getProductionDate());
                }
            }
            
            inventoryMapper.updateById(toInv);
        }

        // 3. 记录调拨流水
        StockTransfer transfer = new StockTransfer();
        transfer.setProductId(productId);
        transfer.setFromStore(fromStore);
        transfer.setToStore(toStore);
        transfer.setQuantity(count);
        transfer.setCreateTime(LocalDateTime.now());
        transferMapper.insert(transfer);

        // 【关键修复】同步执行商品可见性修复
        // 去掉异步，确保必须执行成功，否则回滚事务
        try {
            inventoryService.ensureProductVisibility(toStore, productId, fromInv.getProductName());
        } catch (Exception e) {
            // 打印堆栈，并且抛出运行时异常以触发事务回滚
            e.printStackTrace();
            throw new RuntimeException("自动修复商品可见性失败: " + e.getMessage());
        }

        return "ok";
    }

    @PostMapping("/replenish")
    public String replenish(@RequestParam Long productId,
                            @RequestParam Long storeId,
                            @RequestParam Integer count) {
        return inventoryService.replenish(productId, storeId, count);
    }

    @PostMapping("/replenish/new")
    public String replenishNew(@RequestBody ReplenishRequest req) {
        return inventoryService.replenishFull(req);
    }

    @DeleteMapping("/delete")
    public String delete(@RequestParam Long storeId, @RequestParam Long productId) {
        return inventoryService.deleteInventory(storeId, productId);
    }
}
