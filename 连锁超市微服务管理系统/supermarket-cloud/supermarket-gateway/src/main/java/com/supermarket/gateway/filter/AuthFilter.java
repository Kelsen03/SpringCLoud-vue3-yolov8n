package com.supermarket.gateway.filter;

import com.supermarket.gateway.util.JwtUtil;
import org.springframework.cloud.gateway.filter.GatewayFilterChain;
import org.springframework.cloud.gateway.filter.GlobalFilter;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Component;
import org.springframework.web.server.ServerWebExchange;
import reactor.core.publisher.Mono;

@Component
public class AuthFilter implements GlobalFilter {

    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {

        String path = exchange.getRequest().getURI().getPath();
        
        // 放行登录接口、注册接口和 OPTIONS 请求（CORS 预检）
        if (path.contains("/auth/login") || path.contains("/auth/register") || exchange.getRequest().getMethod().name().equals("OPTIONS")) {
            return chain.filter(exchange);
        }

        String token = exchange.getRequest().getHeaders().getFirst("Authorization");
        if (token == null) {
            exchange.getResponse().setStatusCode(HttpStatus.UNAUTHORIZED);
            return exchange.getResponse().setComplete();
        }

        try {
            JwtUtil.parseToken(token);
        } catch (Throwable e) {
            e.printStackTrace(); // 打印具体的错误到控制台
            exchange.getResponse().setStatusCode(HttpStatus.UNAUTHORIZED);
            // 手动加上跨域头，防止前端报 CORS 错误
            exchange.getResponse().getHeaders().add("Access-Control-Allow-Origin", "*");
            return exchange.getResponse().setComplete();
        }

        return chain.filter(exchange);
    }
}
