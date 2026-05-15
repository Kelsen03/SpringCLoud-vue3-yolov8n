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

    /** 查门店名称（兜底：无store表时用固定映射） */
    default String getStoreName(Long storeId) {
        if (storeId == null) return "总部";
        switch (storeId.intValue()) {
            case 1: return "旗舰店（一号门店）";
            case 2: return "社区店（二号门店）";
            case 3: return "生鲜店（三号门店）";
            default: return "门店" + storeId;
        }
    }
}
