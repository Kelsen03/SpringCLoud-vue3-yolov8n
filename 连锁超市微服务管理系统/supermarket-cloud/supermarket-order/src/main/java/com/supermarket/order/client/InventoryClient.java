package com.supermarket.order.client;

import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;

@FeignClient("inventory-service")
public interface InventoryClient {

    @PostMapping("/inventory/deduct")
    String deduct(@RequestParam("productId") Long productId,
                  @RequestParam("storeId") Long storeId,
                  @RequestParam("count") Integer count);
}
