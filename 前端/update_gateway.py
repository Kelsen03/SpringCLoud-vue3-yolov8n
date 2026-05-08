import os
path = r'C:\Users\LEGION\Desktop\陆铿全源码\连锁超市微服务管理系统\supermarket-cloud\supermarket-gateway\src\main\java\com\supermarket\gateway\filter\AuthFilter.java'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()
content = content.replace('if (path.contains(" /auth/login\) || exchange.getRequest().getMethod().name().equals(\OPTIONS\)) {', 'if (path.contains(\/auth/login\) || path.contains(\/auth/register\) || exchange.getRequest().getMethod().name().equals(\OPTIONS\)) {')
with open(path, 'w', encoding='utf-8') as f:
 f.write(content)
