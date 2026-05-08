package com.supermarket.order.controller;

import com.supermarket.order.client.InventoryClient;
import com.supermarket.order.dto.OrderDTO;
import com.supermarket.order.entity.Order;
import com.supermarket.order.entity.OrderItem;
import com.supermarket.order.mapper.OrderItemMapper;
import com.supermarket.order.mapper.OrderMapper;
import com.supermarket.order.mapper.MemberMapper;
import com.supermarket.order.mapper.ProductSalesMapper;
import com.supermarket.order.entity.Member;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.bind.annotation.RequestParam;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.Date;
import java.util.List;
import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.supermarket.order.util.JwtUtil;
import com.supermarket.order.dto.OrderResponse;

@RestController
@RequestMapping("/order")
public class OrderController {

    @Autowired
    private OrderMapper orderMapper;

    @Autowired
    private OrderItemMapper orderItemMapper;

    @Autowired
    private InventoryClient inventoryClient;
    
    @Autowired
    private MemberMapper memberMapper;
    
    @Autowired
    private ProductSalesMapper productSalesMapper;

    /**
     * 创建订单接口（核心）
     * 1. 计算总价
     * 2. 调用库存服务扣减库存
     * 3. 保存订单主表
     * 4. 保存订单明细表
     */
    @PostMapping("/create")
    public OrderResponse create(@RequestBody OrderDTO dto,
                         @RequestHeader(value = "Authorization", required = false) String token,
                         @RequestHeader(value = "username", required = false) String username) {

        BigDecimal total = BigDecimal.ZERO;
        String role = JwtUtil.role(token);
        Long storeIdFromToken = JwtUtil.storeId(token);
        // 修复：STORE 和 CASHIER 都可以直接从 Token 里获取 storeId
        Long storeIdUsed = ("STORE".equals(role) || "CASHIER".equals(role)) ? storeIdFromToken : dto.getStoreId();
        
        // 尝试从 JWT Token 中提取 username 作为收银员账号
        String currentUsername = username;
        if (currentUsername == null || currentUsername.isEmpty()) {
            if (token != null) {
                try {
                    io.jsonwebtoken.Claims claims = JwtUtil.parseToken(token);
                    if (claims != null && claims.getSubject() != null) {
                        currentUsername = claims.getSubject();
                    }
                } catch (Exception e) {
                    // 忽略解析错误
                }
            }
        }
        
        // 如果上面没拿到，再尝试直接用 dto 里的，兜底处理
        if (storeIdUsed == null || storeIdUsed <= 0) {
            storeIdUsed = dto.getStoreId();
        }
        
        // 如果最后还是没拿到，给个默认值 1，防止报错
        if (storeIdUsed == null || storeIdUsed <= 0) {
            storeIdUsed = 1L;
            // throw new IllegalArgumentException("storeId 无效或缺失");
        }

        boolean usePoints = Boolean.TRUE.equals(dto.getUsePoints());
        Long memberId = dto.getMemberId();
        boolean validMember = memberId != null && memberId > 0;
        if (usePoints && validMember) {
            Member member = memberMapper.selectById(memberId);
            if (member != null && member.getPoints() >= 1000) {
                member.setPoints(member.getPoints() - 1000);
                memberMapper.updateById(member);
            } else {
                throw new RuntimeException("积分不足，无法抵扣");
            }
        }

        // 1. 计算总价 & 扣库存
        for (OrderDTO.Item item : dto.getItems()) {
            total = total.add(item.getPrice()
                    .multiply(new BigDecimal(item.getQuantity())));

            // 2. 扣库存 (Feign 调用)
            String result = inventoryClient.deduct(
                item.getProductId(),
                storeIdUsed,
                item.getQuantity()
            );
            
            if (!"ok".equals(result)) {
                throw new RuntimeException("库存不足，商品ID: " + item.getProductId());
            }
            
            // 累计商品销量（按门店）
            productSalesMapper.upsertAdd(storeIdUsed, item.getProductId(), item.getQuantity());
        }

        if (usePoints) {
            total = total.subtract(new BigDecimal("5"));
            if (total.compareTo(BigDecimal.ZERO) < 0) {
                total = BigDecimal.ZERO;
            }
        }

        // 3. 保存订单
        Order order = new Order();
        order.setStoreId(storeIdUsed);
        order.setMemberId(validMember ? memberId : null);
        order.setTotalPrice(total);
        int points = total.multiply(new BigDecimal(10)).setScale(0, RoundingMode.DOWN).intValue();
        order.setPoints(points);
        order.setCreateTime(new Date());
        
        // 【新增】将收银员账号保存到订单中
        if (currentUsername != null && !currentUsername.isEmpty()) {
            order.setCreateBy(currentUsername);
        }
        
        orderMapper.insert(order);

        // 4. 保存明细
        for (OrderDTO.Item item : dto.getItems()) {
            OrderItem orderItem = new OrderItem();
            orderItem.setOrderId(order.getId());
            orderItem.setProductId(item.getProductId());
            orderItem.setPrice(item.getPrice());
            orderItem.setQuantity(item.getQuantity());
            orderItemMapper.insert(orderItem);
        }
        Integer totalPoints = 0;
        if (validMember) {
            Member m = memberMapper.selectById(memberId);
            if (m == null) {
                m = new Member();
                m.setId(memberId);
                m.setPoints(points);
                memberMapper.insert(m);
            } else {
                m.setPoints(m.getPoints() + points);
                memberMapper.updateById(m);
            }
            totalPoints = memberMapper.selectById(memberId).getPoints();
        }
        return new OrderResponse(order.getId(), points, totalPoints);
    }

    /**
     * 获取订单列表
     */
    @GetMapping("/list")
    public List<Order> list(@RequestParam(required = false) Long storeId,
                            @RequestHeader(value = "Authorization", required = false) String token) {
        String role = JwtUtil.role(token);
        Long tokenStoreId = JwtUtil.storeId(token);

        QueryWrapper<Order> queryWrapper = new QueryWrapper<>();
        
        // 门店角色只能看自己的订单
        if ("STORE".equals(role)) {
            queryWrapper.eq("store_id", tokenStoreId);
        } else if (storeId != null) {
            // 总部角色可以看所有订单，也可以按门店筛选
            queryWrapper.eq("store_id", storeId);
        }
        
        // 按创建时间倒序排列
        queryWrapper.orderByDesc("create_time");
        
        return orderMapper.selectList(queryWrapper);
    }

    /**
     * 查询会员积分
     */
    @GetMapping("/member-points")
    public Integer getMemberPoints(@RequestParam Long memberId) {
        if (memberId == null || memberId <= 0) {
            return 0;
        }
        Member member = memberMapper.selectById(memberId);
        return member != null ? member.getPoints() : 0;
    }

    /**
     * 获取订单详情（包含商品明细）
     */
    @GetMapping("/detail")
    public OrderResponse getOrderDetail(@RequestParam Long orderId) {
        Order order = orderMapper.selectById(orderId);
        if (order == null) {
            throw new RuntimeException("订单不存在");
        }

        // 查询该订单的所有商品明细
        QueryWrapper<OrderItem> queryWrapper = new QueryWrapper<>();
        queryWrapper.eq("order_id", orderId);
        List<OrderItem> items = orderItemMapper.selectList(queryWrapper);

        // 构造返回对象
        OrderResponse response = new OrderResponse();
        response.setOrderId(order.getId());
        response.setPoints(order.getPoints());
        response.setItems(items); // 把明细列表装进去
        // 为了前端展示方便，将创建时间和总价也放进去
        response.setCreateTime(order.getCreateTime());
        response.setTotalPrice(order.getTotalPrice());
        response.setMemberId(order.getMemberId());
        response.setCreateBy(order.getCreateBy()); // 加上收银员账号
        
        return response; 
    }
}
