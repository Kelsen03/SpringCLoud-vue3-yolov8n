package com.supermarket.product.controller;

import com.supermarket.product.entity.Product;
import com.supermarket.product.service.ProductService;
import com.supermarket.product.util.JwtUtil;
import io.jsonwebtoken.Claims;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import org.springframework.web.client.RestTemplate;
import org.springframework.http.ResponseEntity;
import java.util.Map;
import java.util.HashMap;
import java.util.ArrayList;

@RestController
@RequestMapping("/product")
public class ProductController {

    @Autowired
    private ProductService productService;

    // AI 智能收银商品识别接口
    @PostMapping("/ai-recognize")
    public List<Map<String, Object>> aiRecognize(@RequestBody Map<String, String> requestData,
                                                 @RequestHeader(value = "Authorization", required = false) String token) {
        String base64Image = requestData.get("image");
        List<Map<String, Object>> resultList = new ArrayList<>();

        if (base64Image == null || base64Image.isEmpty()) {
            return resultList;
        }

        try {
            // 1. 调用 Python AI 微服务进行 YOLOv5 图像识别
            RestTemplate restTemplate = new RestTemplate();
            String pythonAiUrl = "http://localhost:5000/api/detect"; // Python 服务地址
            
            Map<String, String> aiRequest = new HashMap<>();
            aiRequest.put("image", base64Image);
            
            // 获取识别结果 (Mock数据格式: [{"name": "可口可乐", "quantity": 2}, ...])
            ResponseEntity<List> response = restTemplate.postForEntity(pythonAiUrl, aiRequest, List.class);
            List<Map<String, Object>> detectedItems = response.getBody();

            if (detectedItems != null) {
                for (Map<String, Object> item : detectedItems) {
                    String productName = (String) item.get("name");
                    Integer quantity = (Integer) item.get("quantity");

                    // 2. 去数据库查询该商品的真实信息（价格等）
                    QueryWrapper<Product> queryWrapper = new QueryWrapper<>();
                    queryWrapper.like("name", productName).last("LIMIT 1");
                    Product product = productService.getOne(queryWrapper);

                    if (product != null) {
                        Map<String, Object> resultMap = new HashMap<>();
                        resultMap.put("id", product.getId());
                        resultMap.put("productName", product.getName());
                        resultMap.put("price", product.getPrice());
                        resultMap.put("quantity", quantity);
                        resultList.add(resultMap);
                    }
                }
            }
        } catch (Exception e) {
            e.printStackTrace();
            // 如果 Python 服务没开，为了演示不报错，我们给个保底的假数据：
            Map<String, Object> fallback = new HashMap<>();
            fallback.put("id", 999);
            fallback.put("productName", "测试商品(AI未启动)");
            fallback.put("price", 5.00);
            fallback.put("quantity", 1);
            resultList.add(fallback);
        }

        return resultList;
    }

    // 1️⃣ 新增商品（总部 / 门店共用）
    // 逻辑：
    // - 总部（HQ）：可以添加全局商品（isLocal=0），所有门店可见
    // - 门店（STORE）：只能添加本地自营商品（isLocal=1），仅自己可见
    @PostMapping("/add")
    public String add(@RequestBody Product product,
                      @RequestHeader("Authorization") String token) {

        // 解析 Token 获取角色
        Claims claims = JwtUtil.parseToken(token);
        String role = (String) claims.get("role");

        // 门店只能加本地商品
        if ("STORE".equals(role)) {
            product.setIsLocal(1);
            // 动态获取 storeId (安全解析)
            Object storeIdObj = claims.get("storeId");
            Long storeId = 1L;
            if (storeIdObj != null) {
                if (storeIdObj instanceof Number) {
                    storeId = ((Number) storeIdObj).longValue();
                } else if (storeIdObj instanceof String) {
                    storeId = Long.valueOf((String) storeIdObj);
                }
            }
            product.setStoreId(storeId); 
        } else {
            // 总部添加的是全局商品
            product.setIsLocal(0);
            product.setStoreId(null);
        }

        productService.save(product);
        return "ok";
    }

    // 2️⃣ 修改商品（总部专属）
    // 逻辑：只有总部有权限修改商品信息（如统一调价）
    @PutMapping("/update")
    public String update(@RequestBody Product product,
                         @RequestHeader("Authorization") String token) {

        Claims claims = JwtUtil.parseToken(token);
        // 权限校验：非HQ直接拒绝
        if (!"HQ".equals(claims.get("role"))) {
            return "no permission";
        }

        productService.updateById(product);
        return "ok";
    }

    // 3️⃣ 商品列表查询
    // 逻辑：
    // - 总部：查看所有商品（便于管理）
    // - 门店：查看 "总部商品" + "自己的本地商品"
    @GetMapping("/list")
    public List<Product> list(@RequestHeader(value = "Authorization", required = false) String token,
                              @RequestParam(value = "storeId", required = false) String storeIdStr) {

        Claims claims = null;
        if (token != null && !token.isEmpty()) {
            try {
                claims = JwtUtil.parseToken(token);
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
        
        String role = claims != null ? (String) claims.get("role") : "STORE";

        if ("HQ".equals(role)) {
            return productService.findAll();
        } else {
            // 优先使用前端传来的 storeId，如果没有再从 Token 拿
            Long finalStoreId = null;
            if (storeIdStr != null && !storeIdStr.isEmpty()) {
                try {
                    finalStoreId = Long.valueOf(storeIdStr);
                } catch (NumberFormatException e) {
                    e.printStackTrace();
                }
            }
            
            if (finalStoreId == null && claims != null) {
                Object storeIdObj = claims.get("storeId");
                if (storeIdObj != null) {
                    if (storeIdObj instanceof Number) {
                        finalStoreId = ((Number) storeIdObj).longValue();
                    } else if (storeIdObj instanceof String) {
                        try {
                            finalStoreId = Long.valueOf((String) storeIdObj);
                        } catch (NumberFormatException e) {
                            e.printStackTrace();
                        }
                    }
                }
            }
            
            // 如果都拿不到，默认给个 1
            if (finalStoreId == null) {
                finalStoreId = 1L;
            }
            
            return productService.findForStore(finalStoreId);
        }
    }
}
