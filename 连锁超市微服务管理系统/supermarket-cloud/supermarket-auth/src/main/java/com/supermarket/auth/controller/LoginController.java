package com.supermarket.auth.controller;

import com.supermarket.auth.common.Result;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RequestBody;
import com.supermarket.auth.entity.User;
import com.supermarket.auth.mapper.UserMapper;
import com.supermarket.auth.util.JwtUtil;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/auth")
public class LoginController {

    @Autowired
    private UserMapper userMapper;

    @Autowired
    private BCryptPasswordEncoder passwordEncoder;

    @PostMapping(value = "/login")
    public Result login(@RequestParam(required = false) String username,
                        @RequestParam(required = false) String password) {

        if (username == null || password == null) {
            return Result.fail("用户名或密码不能为空");
        }

        try {
            QueryWrapper<User> queryWrapper = new QueryWrapper<>();
            queryWrapper.eq("username", username);
            User user = userMapper.selectOne(queryWrapper);

            if (user != null && passwordEncoder.matches(password, user.getPassword())) {
                String role = user.getRole() != null ? user.getRole() : "STORE";

                String realToken = JwtUtil.createToken(
                    username, role, user.getStoreId() != null ? Long.valueOf(user.getStoreId()) : null
                );

                return Result.ok()
                        .put("token", realToken)
                        .put("role", role)
                        .put("storeId", user.getStoreId())
                        .put("realName", user.getRealName());
            }
        } catch (Exception e) {
            e.printStackTrace();
        }

        return Result.fail("用户名或密码错误");
    }

    @PostMapping("/register")
    public Result register(@RequestBody User user) {
        if (user.getUsername() == null || user.getPassword() == null) {
            return Result.fail("用户名或密码不能为空");
        }

        QueryWrapper<User> queryWrapper = new QueryWrapper<>();
        queryWrapper.eq("username", user.getUsername());
        if (userMapper.selectCount(queryWrapper) > 0) {
            return Result.fail("用户名已存在");
        }

        if (user.getRole() == null) {
            user.setRole("STORE");
        }

        user.setPassword(passwordEncoder.encode(user.getPassword()));

        userMapper.insert(user);
        return Result.ok().put("msg", "注册成功");
    }
}
