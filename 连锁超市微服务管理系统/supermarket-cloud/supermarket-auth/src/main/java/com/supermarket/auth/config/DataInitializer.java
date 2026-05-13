package com.supermarket.auth.config;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.supermarket.auth.entity.User;
import com.supermarket.auth.mapper.UserMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.CommandLineRunner;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.stereotype.Component;

@Component
public class DataInitializer implements CommandLineRunner {

    @Autowired
    private UserMapper userMapper;

    @Autowired
    private BCryptPasswordEncoder passwordEncoder;

    @Override
    public void run(String... args) {
        String encodedPassword = passwordEncoder.encode("123456");

        initUser("admin", encodedPassword, "HQ", "超级管理员", 0L);
        initUser("store1", encodedPassword, "STORE", "一号门店店长", 1L);
        initUser("store2", encodedPassword, "STORE", "二号门店店长", 2L);
        initUser("store3", encodedPassword, "STORE", "三号门店店长", 3L);
    }

    private void initUser(String username, String encodedPassword, String role, String realName, Long storeId) {
        QueryWrapper<User> wrapper = new QueryWrapper<>();
        wrapper.eq("username", username);
        if (userMapper.selectCount(wrapper) == 0) {
            User user = new User();
            user.setUsername(username);
            user.setPassword(encodedPassword);
            user.setRole(role);
            user.setRealName(realName);
            user.setStoreId(storeId);
            userMapper.insert(user);
        }
    }
}
