package com.supermarket.auth.controller;

import com.supermarket.auth.common.Result;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RequestBody;
import com.supermarket.auth.entity.User;
import com.supermarket.auth.mapper.UserMapper;
import org.springframework.beans.factory.annotation.Autowired;
import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/auth")
public class LoginController {

    @Autowired
    private UserMapper userMapper;

    @PostMapping(value = "/login")
    public Result login(@RequestParam(required = false) String username, 
                        @RequestParam(required = false) String password) {
        
        if (username == null || password == null) {
            return Result.fail("用户名或密码不能为空");
        }

        // 1. 优先使用硬编码账号（保证老账号绝对能登录）
        if ("admin".equals(username) && "123456".equals(password)) {
            return Result.ok().put("token", "admin-token").put("role", "HQ");
        }
        if ("store1".equals(username) && "123456".equals(password)) {
            return Result.ok().put("token", "store-token").put("role", "STORE");
        }
        if ("store2".equals(username) && "123456".equals(password)) {
            return Result.ok().put("token", "store2-token").put("role", "STORE");
        }
        if ("store3".equals(username) && "123456".equals(password)) {
            return Result.ok().put("token", "store3-token").put("role", "STORE");
        }

        // 2. 如果不是上面的默认账号，再去数据库查询（用于新注册的账号）
        try {
            QueryWrapper<User> queryWrapper = new QueryWrapper<>();
            queryWrapper.eq("username", username).eq("password", password);
            User user = userMapper.selectOne(queryWrapper);

            if (user != null) {
                String role = user.getRole() != null ? user.getRole() : "STORE";
                
                // 生成真正的 JWT，把角色和门店ID都放进去
                String realToken = com.supermarket.auth.util.JwtUtil.createToken(
                    username, role, user.getStoreId() != null ? Long.valueOf(user.getStoreId()) : null
                );
                
                return Result.ok()
                        .put("token", realToken) // 返回真正的 token
                        .put("role", role)
                        .put("storeId", user.getStoreId())
                        .put("realName", user.getRealName());
            }
        } catch (Exception e) {
            // 捕获可能出现的数据库查询异常，防止程序崩溃
            e.printStackTrace();
        }

        return Result.fail("用户名或密码错误");
    }

    @PostMapping("/register")
    public Result register(@RequestBody User user) {
        if (user.getUsername() == null || user.getPassword() == null) {
            return Result.fail("用户名或密码不能为空");
        }
        
        // 检查用户名是否已存在
        QueryWrapper<User> queryWrapper = new QueryWrapper<>();
        queryWrapper.eq("username", user.getUsername());
        if (userMapper.selectCount(queryWrapper) > 0) {
            return Result.fail("用户名已存在");
        }
        
        // 设置默认角色和信息
        if (user.getRole() == null) {
            user.setRole("STORE"); // 默认角色
        }
        
        userMapper.insert(user);
        return Result.ok().put("msg", "注册成功");
    }
}
