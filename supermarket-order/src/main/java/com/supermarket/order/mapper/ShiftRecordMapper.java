package com.supermarket.order.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.supermarket.order.entity.ShiftRecord;
import org.apache.ibatis.annotations.Mapper;

/** 换班记录 Mapper */
@Mapper
public interface ShiftRecordMapper extends BaseMapper<ShiftRecord> {
}
