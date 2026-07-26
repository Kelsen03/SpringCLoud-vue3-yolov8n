package com.supermarket.order.util;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.SignatureAlgorithm;

import java.util.Date;

public class JwtUtil {

    private static final String SECRET = "supermarket";

    public static Claims parseToken(String token) {
        try {
            return Jwts.parser()
                    .setSigningKey(SECRET)
                    .parseClaimsJws(token)
                    .getBody();
        } catch (Exception e) {
            return null;
        }
    }

    public static String role(String token) {
        if (token == null) return null;
        Claims claims = parseToken(token);
        if (claims != null) {
            return (String) claims.get("role");
        }
        return null;
    }

    /** 从Token提取用户名 */
    public static String username(String token) {
        if (token == null) return null;
        Claims claims = parseToken(token);
        return claims != null ? claims.getSubject() : null;
    }

    public static Long storeId(String token) {
        if (token == null) return null;
        Claims claims = parseToken(token);
        if (claims != null) {
            Object storeIdObj = claims.get("storeId");
            if (storeIdObj != null) {
                if (storeIdObj instanceof Number) {
                    return ((Number) storeIdObj).longValue();
                } else if (storeIdObj instanceof String) {
                    try {
                        return Long.valueOf((String) storeIdObj);
                    } catch (NumberFormatException e) {
                        return null;
                    }
                }
            }
        }
        return null;
    }
}

