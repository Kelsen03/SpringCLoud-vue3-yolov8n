package com.supermarket.product;

import com.supermarket.product.util.JwtUtil;
import io.jsonwebtoken.Claims;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/product")
public class TestController {

    @GetMapping("/test")
    public String test() {
        return "product service ok";
    }

    @GetMapping("/hq/only")
    public String onlyHQ(@RequestHeader("Authorization") String token) {
        Claims claims = JwtUtil.parseToken(token);
        if (!"HQ".equals(claims.get("role"))) {
            return "no permission";
        }
        return "welcome HQ";
    }
}