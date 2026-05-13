package com.supermarket.analysis.schedule;

import com.supermarket.analysis.mapper.AnalysisMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

@Component
public class ScheduledTaskService {

    @Autowired
    private AnalysisMapper analysisMapper;

    @Scheduled(cron = "0 0 2 * * ?")
    public void aggregateDailyStats() {
        System.out.println("[定时任务] 开始执行每日数据聚合...");
        try {
            analysisMapper.storeRank();
            analysisMapper.productRank();
            analysisMapper.replenishSuggest();
            System.out.println("[定时任务] 每日数据聚合完成");
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
