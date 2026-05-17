package com.supermarket.analysis.controller;

import com.supermarket.analysis.mapper.AnalysisMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Map;
import java.util.ArrayList;

@RestController
@RequestMapping("/analysis")
public class AnalysisController {

    @Autowired
    private AnalysisMapper analysisMapper;

    @GetMapping("/storeRank")
    public List<?> storeRank() {
        return analysisMapper.storeRank();
    }

    @GetMapping("/productRank")
    public List<?> productRank() {
        return analysisMapper.productRank();
    }

    /** 补货推荐 v4：双因子+ABC 分类 */
    @GetMapping("/replenish/recommend")
    public List<Map<String, Object>> replenishRecommend() {
        List<Map<String, Object>> list = analysisMapper.replenishRecommend();
        double avg = list.stream()
            .filter(m -> m.get("total_sales") != null)
            .mapToDouble(m -> ((Number) m.get("total_sales")).doubleValue())
            .average().orElse(1.0);
        for (Map<String, Object> m : list) {
            Number sales = (Number) m.get("total_sales");
            double v = sales != null ? sales.doubleValue() : 0;
            String cls; double factor;
            if (v > avg * 1.5) { cls = "A"; factor = 1.5; }
            else if (v >= avg * 0.5) { cls = "B"; factor = 1.0; }
            else { cls = "C"; factor = 0.5; }
            m.put("abc_class", cls);
            m.put("abc_factor", factor);
            Number qty = (Number) m.get("recommend_qty");
            if (qty != null && qty.doubleValue() > 0) {
                m.put("recommend_qty", Math.round(qty.doubleValue() * factor));
            }
        }
        return list;
    }

    @GetMapping("/preference")
    public List<?> getRegionPreference() {
        return analysisMapper.getRegionPreference();
    }

    @GetMapping("/shiftRecord")
    public List<?> shiftRecord() {
        return analysisMapper.shiftRecordAnalysis();
    }
}
