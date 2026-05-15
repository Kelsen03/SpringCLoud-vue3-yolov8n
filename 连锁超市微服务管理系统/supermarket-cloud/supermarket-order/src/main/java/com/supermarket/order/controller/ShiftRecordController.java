package com.supermarket.order.controller;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.supermarket.order.entity.ShiftRecord;
import com.supermarket.order.mapper.OrderMapper;
import com.supermarket.order.mapper.ShiftRecordMapper;
import com.supermarket.order.util.JwtUtil;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;
import java.util.*;

/** 收银员换班管理 */
@RestController
@RequestMapping("/shift")
public class ShiftRecordController {

    @Autowired
    private ShiftRecordMapper shiftMapper;

    @Autowired
    private OrderMapper orderMapper;

    /** 开班：输入找零备用金，创建新班次 */
    @PostMapping("/open")
    public Map<String, Object> openShift(@RequestParam BigDecimal openingCash,
                                         @RequestHeader("Authorization") String token) {
        String username = JwtUtil.username(token);
        Long storeId = JwtUtil.storeId(token);
        if (storeId == null) storeId = 1L;

        // 检查是否有未交班的记录
        QueryWrapper<ShiftRecord> qw = new QueryWrapper<>();
        qw.eq("cashier_username", username).eq("status", "ACTIVE");
        if (shiftMapper.selectCount(qw) > 0) {
            Map<String, Object> err = new HashMap<>();
            err.put("ok", false);
            err.put("msg", "当前有未交班的班次，请先交班");
            return err;
        }

        ShiftRecord sr = new ShiftRecord();
        sr.setStoreId(storeId);
        sr.setCashierUsername(username);
        sr.setShiftStart(new Date());
        sr.setOpeningCash(openingCash);
        sr.setStatus("ACTIVE");
        shiftMapper.insert(sr);

        Map<String, Object> result = new HashMap<>();
        result.put("ok", true);
        result.put("shiftId", sr.getId());
        result.put("msg", "开班成功，备用金 ¥" + openingCash);
        return result;
    }

    /** 交班：输入实际现金，系统自动统计本班收入进行对账 */
    @PostMapping("/close")
    public Map<String, Object> closeShift(@RequestParam BigDecimal closingCash,
                                          @RequestHeader("Authorization") String token) {
        String username = JwtUtil.username(token);

        // 找到当前活跃班次
        QueryWrapper<ShiftRecord> qw = new QueryWrapper<>();
        qw.eq("cashier_username", username).eq("status", "ACTIVE").orderByDesc("id").last("LIMIT 1");
        ShiftRecord sr = shiftMapper.selectOne(qw);
        if (sr == null) {
            Map<String, Object> err = new HashMap<>();
            err.put("ok", false);
            err.put("msg", "未找到已开班的记录");
            return err;
        }

        // 统计本班的订单数据（按收银员和开班时间之后的订单）
        Map<String, Object> stats = orderMapper.getShiftStats(username, sr.getShiftStart());
        BigDecimal systemCash = stats.get("cash") != null ? (BigDecimal) stats.get("cash") : BigDecimal.ZERO;
        Integer orderCount = stats.get("count") != null ? ((Number) stats.get("count")).intValue() : 0;

        sr.setShiftEnd(new Date());
        sr.setClosingCash(closingCash);
        sr.setSystemCash(systemCash);
        sr.setSystemOnline(BigDecimal.ZERO);
        sr.setTotalOrders(orderCount);
        sr.setStatus("CLOSED");

        BigDecimal theoryCash = sr.getOpeningCash().add(systemCash);
        BigDecimal diff = closingCash.subtract(theoryCash);
        sr.setRemark("差异: ¥" + diff.stripTrailingZeros().toPlainString());
        shiftMapper.updateById(sr);

        Map<String, Object> result = new HashMap<>();
        result.put("ok", true);
        result.put("openingCash", sr.getOpeningCash());
        result.put("systemCash", systemCash);
        result.put("totalOrders", orderCount);
        result.put("theoryCash", theoryCash);
        result.put("closingCash", closingCash);
        result.put("diff", diff);
        result.put("msg", "交班完成");
        return result;
    }

    /** 查询当前是否已开班 */
    @GetMapping("/current")
    public Map<String, Object> currentShift(@RequestHeader("Authorization") String token) {
        String username = JwtUtil.username(token);
        QueryWrapper<ShiftRecord> qw = new QueryWrapper<>();
        qw.eq("cashier_username", username).eq("status", "ACTIVE").orderByDesc("id").last("LIMIT 1");
        ShiftRecord sr = shiftMapper.selectOne(qw);

        Map<String, Object> result = new HashMap<>();
        result.put("hasShift", sr != null);
        if (sr != null) {
            result.put("shiftId", sr.getId());
            result.put("openingCash", sr.getOpeningCash());
        }
        return result;
    }
}
