package com.supermarket.analysis.controller;

import com.supermarket.analysis.mapper.AnalysisMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

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

    @GetMapping("/replenish")
    public List<?> replenishSuggest() {
        return analysisMapper.replenishSuggest();
    }

    @GetMapping("/regionPreference")
    public List<?> getRegionPreference() {
        return analysisMapper.getRegionPreference();
    }
}
