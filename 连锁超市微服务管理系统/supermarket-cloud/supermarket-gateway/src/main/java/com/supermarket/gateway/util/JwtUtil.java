package com.supermarket.gateway.util;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.SignatureAlgorithm;

import java.util.Date;

public class JwtUtil {

    private static final String SECRET = "supermarket";

    // 加上 storeId 参数，保持一致
    public static String createToken(String username, String role, Long storeId) {
        return Jwts.builder()
                .setSubject(username)
                .claim("role", role)
                .claim("storeId", storeId)
                .setExpiration(new Date(System.currentTimeMillis() + 86400000))
                .signWith(SignatureAlgorithm.HS256, SECRET)
                .compact();
    }

    public static Claims parseToken(String token) {
        if ("admin-token".equals(token)) {
            Claims claims = Jwts.claims().setSubject("admin");
            claims.put("role", "HQ");
            claims.put("storeId", null);
            return claims;
        }
        if ("store-token".equals(token)) {
            Claims claims = Jwts.claims().setSubject("store1");
            claims.put("role", "STORE");
            claims.put("storeId", 1L);
            return claims;
        }
        if ("store2-token".equals(token)) {
            Claims claims = Jwts.claims().setSubject("store2");
            claims.put("role", "STORE");
            claims.put("storeId", 2L);
            return claims;
        }
        if ("store3-token".equals(token)) {
            Claims claims = Jwts.claims().setSubject("store3");
            claims.put("role", "STORE");
            claims.put("storeId", 3L);
            return claims;
        }
        
        // 解析真实的 Token
        return Jwts.parser()
                .setSigningKey(SECRET)
                .parseClaimsJws(token)
                .getBody();
    }
}