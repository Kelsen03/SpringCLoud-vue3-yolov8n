package com.supermarket.order.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.supermarket.order.entity.Order;
import org.apache.ibatis.annotations.*;

import java.util.Date;
import java.util.Map;

@Mapper
public interface OrderMapper extends BaseMapper<Order> {

    /** 统计某收银员从开班到现在的营业数据 */
    @Select("SELECT " +
            "COALESCE(SUM(o.total_price), 0) AS cash, " +
            "COUNT(*) AS count " +
            "FROM `order` o " +
            "WHERE o.create_by = #{username} AND o.create_time >= #{since}")
    Map<String, Object> getShiftStats(@Param("username") String username, @Param("since") Date since);

    /** 查门店名称（跨库查 supermarket_auth.store） */
    @Select("SELECT name FROM supermarket_auth.store WHERE id = #{storeId}")
    String getStoreName(@Param("storeId") Long storeId);
}
