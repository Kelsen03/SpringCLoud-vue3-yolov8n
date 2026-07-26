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

    @Autowired
    private com.supermarket.auth.mapper.StoreMapper storeMapper;

    @Override
    public void run(String... args) {
        String encodedPassword = passwordEncoder.encode("123456");

        initStore(1L, "旗舰店（一号门店）");
        initStore(2L, "社区店（二号门店）");
        initStore(3L, "生鲜店（三号门店）");

        initUser("admin", encodedPassword, "HQ", "超级管理员", 0);
        initUser("store1", encodedPassword, "STORE", "一号门店店长", 1);
        initUser("store2", encodedPassword, "STORE", "二号门店店长", 2);
        initUser("store3", encodedPassword, "STORE", "三号门店店长", 3);
    }

    private void initUser(String username, String encodedPassword, String role, String realName, Integer storeId) {
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

    private void initStore(Long id, String name) {
        com.supermarket.auth.entity.Store store = storeMapper.selectById(id);
        if (store == null) {
            store = new com.supermarket.auth.entity.Store();
            store.setId(id);
            store.setName(name);
            storeMapper.insert(store);
        }
    }
}
