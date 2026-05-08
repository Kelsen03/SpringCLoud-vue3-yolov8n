import os
import re

path = r'C:\Users\LEGION\Desktop\陆铿全源码\连锁超市微服务管理系统\supermarket-cloud\supermarket-auth\src\main\java\com\supermarket\auth\controller\LoginController.java'

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    'import org.springframework.web.bind.annotation.RequestParam;',
    'import org.springframework.web.bind.annotation.RequestParam;\nimport org.springframework.web.bind.annotation.RequestBody;\nimport org.springframework.web.bind.annotation.PostMapping;\nimport com.supermarket.auth.entity.User;\nimport com.supermarket.auth.mapper.UserMapper;\nimport org.springframework.beans.factory.annotation.Autowired;\nimport com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;'
)

content = content.replace(
    'public class LoginController {',
    'public class LoginController {\n\n    @Autowired\n    private UserMapper userMapper;'
)

content = re.sub(
    r'return Result\.fail\(" 用户名或密码错误\\);\s*\}\s*\}',
 ' // 数据库查询\n QueryWrapper<User> queryWrapper = new QueryWrapper<>();\n queryWrapper.eq(\username\, username);\n queryWrapper.eq(\password\, password);\n User user = userMapper.selectOne(queryWrapper);\n\n if (user != null) {\n return Result.ok()\n .put(\token\, user.getUsername() + \-token\)\n .put(\role\, user.getRole())\n .put(\storeId\, user.getStoreId());\n }\n\n return Result.fail(\用户名或密码错误\);\n }\n\n @PostMapping(\/register\)\n public Result register(@RequestBody User user) {\n if (user.getUsername() == null || user.getPassword() == null) {\n return Result.fail(\用户名或密码不能为空\);\n }\n QueryWrapper<User> queryWrapper = new QueryWrapper<>();\n queryWrapper.eq(\username\, user.getUsername());\n if (userMapper.selectCount(queryWrapper) > 0) {\n return Result.fail(\该账号已被注册\);\n }\n userMapper.insert(user);\n return Result.ok(\注册成功\);\n }\n}',
 content
)

with open(path, 'w', encoding='utf-8') as f:
 f.write(content)
