package com.supermarket.product.service;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.supermarket.product.entity.Product;
import com.supermarket.product.mapper.ProductMapper;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class ProductService extends ServiceImpl<ProductMapper, Product> {

    public List<Product> findForStore(Long storeId) {
        return baseMapper.selectList(
            new QueryWrapper<Product>()
                .eq("is_local", 0)
                .or()
                .isNull("is_local") // 【修复逻辑】：如果 is_local 是空，也默认当作全局商品，大家都能看！
                .or()
                .eq("store_id", storeId)
        );
    }
    
    public List<Product> findAll() {
        return list();
    }
}
