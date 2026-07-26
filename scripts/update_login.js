const fs = require('fs');
const path = 'C:/Users/LEGION/Desktop/陆铿全源码/连锁超市微服务管理系统/supermarket-cloud/supermarket-auth/src/main/java/com/supermarket/auth/controller/LoginController.java';
let content = fs.readFileSync(path, 'utf8');

content = content.replace('import org.springframework.web.bind.annotation.RequestParam;',
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.PostMapping;
import com.supermarket.auth.entity.User;
import com.supermarket.auth.mapper.UserMapper;
import org.springframework.beans.factory.annotation.Autowired;
import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;);

content = content.replace('public class LoginController {',
public class LoginController {

    @Autowired
    private UserMapper userMapper;);

content = content.replace(/return Result\.fail\( 用户名或密码错误\);[\s\S]*?}/,
        // 数据库查询
        QueryWrapper<User> queryWrapper = new QueryWrapper<>();
        queryWrapper.eq(username, username);
        queryWrapper.eq(password, password);
        User user = userMapper.selectOne(queryWrapper);

        if (user != null) {
            return Result.ok()
                    .put(token, user.getUsername() + -token)
                    .put(role, user.getRole())
                    .put(storeId, user.getStoreId());
        }

        return Result.fail(用户名或密码错误);
    }

    @PostMapping(/register)
    public Result register(@RequestBody User user) {
        if (user.getUsername() == null || user.getPassword() == null) {
            return Result.fail(用户名或密码不能为空);
        }
        QueryWrapper<User> queryWrapper = new QueryWrapper<>();
        queryWrapper.eq(username, user.getUsername());
        if (userMapper.selectCount(queryWrapper) > 0) {
            return Result.fail(该账号已被注册);
        }
        userMapper.insert(user);
        return Result.ok(注册成功);
    }
});

fs.writeFileSync(path, content, 'utf8');
