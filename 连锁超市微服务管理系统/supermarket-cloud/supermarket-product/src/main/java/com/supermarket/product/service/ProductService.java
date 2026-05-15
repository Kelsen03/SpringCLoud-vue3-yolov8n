package com.supermarket.product.service;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.supermarket.product.entity.Product;
import com.supermarket.product.mapper.ProductMapper;
import org.springframework.cache.annotation.CacheEvict;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class ProductService extends ServiceImpl<ProductMapper, Product> {

    @Cacheable(value = "productStore", key = "#storeId")
    public List<Product> findForStore(Long storeId) {
        return baseMapper.selectList(
            new QueryWrapper<Product>()
                .eq("is_local", 0)
                .or()
                .isNull("is_local")
                .or()
                .eq("store_id", storeId)
        );
    }

    @Cacheable(value = "productAll", key = "'all'")
    public List<Product> findAll() {
        return list();
    }

    @CacheEvict(value = {"productAll", "productStore"}, allEntries = true)
    public void updateAndEvictCache(Product product) {
        updateById(product);
    }

    @CacheEvict(value = {"productAll", "productStore"}, allEntries = true)
    public void evictProductCache() {
    }
}
