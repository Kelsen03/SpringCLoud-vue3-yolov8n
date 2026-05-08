package com.supermarket.product.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.supermarket.product.entity.Product;
import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface ProductMapper extends BaseMapper<Product> {
}
