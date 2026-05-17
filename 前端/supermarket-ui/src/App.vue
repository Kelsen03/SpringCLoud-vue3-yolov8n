<script setup> 
import { useRouter, useRoute } from 'vue-router' 
import { ref, computed } from 'vue'
import { Monitor, Shop, DataAnalysis, Box, Money, SwitchButton, Goods, Van, ShoppingCart, Tools, Ticket, Service, Wallet, User, Setting, Document, Calendar } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const router = useRouter() 
const route = useRoute()
const role = ref(localStorage.getItem('role'))

// 监听路由变化，实时更新 role（解决登录后菜单不刷新的问题）
router.afterEach(() => {
  role.value = localStorage.getItem('role')
})

const comingSoon = () => {
  ElMessage.info('该功能模块正在开发中...')
}

const go = (path) => { 
  router.push(path) 
} 

const logout = () => { 
  localStorage.clear() 
  role.value = null
  router.push('/') 
} 

// 判断当前路径是否激活
const isActive = (path) => {
  return route.path === path
}
</script> 

<template> 
  <div class="app-layout"> 
    <!-- 顶部导航栏 (Glassmorphism + Gradient) -->
    <!-- 仅在已登录且非登录/注册页显示导航栏 -->
    <div v-if="role && route.path !== '/' && route.path !== '/register'" class="top-nav"> 
      <div class="brand-container">
        <div class="logo-circle">🛒</div>
        <div class="title-wrapper">
          <span class="main-title">连锁超市微服务管理系统</span>
          <span class="sub-title">Microservice Retail System</span>
        </div>
      </div>

      <div class="user-info">
        <!-- 仅为收银员角色在顶部显示收银台菜单 -->
        <el-button 
          v-if="role === 'CASHIER'"
          class="top-menu-btn"
          type="primary"
          plain
          round
          @click="go('/pos')"
        >
          <el-icon style="margin-right: 4px;"><Money /></el-icon>
          收银台
        </el-button>

        <el-tag 
          class="role-tag"
          effect="dark" 
          :type="role === 'HQ' ? 'success' : (role === 'STORE' ? 'warning' : 'info')"
          size="large"
          round
        >
          {{ role === 'HQ' ? '总部 (HQ)' : (role === 'STORE' ? '门店 (STORE)' : (role === 'CASHIER' ? '收银员 (CASHIER)' : '未登录')) }}
        </el-tag>
        
        <el-button 
          v-if="role" 
          class="logout-btn"
          type="danger" 
          circle 
          plain 
          @click="logout" 
          title="退出登录"
        >
          <el-icon><SwitchButton /></el-icon>
        </el-button> 
      </div>
    </div> 

    <div class="main-container"> 
      <!-- 左侧侧边栏 (Modern Sidebar) --> 
      <!-- 仅在已登录、非登录/注册页、且角色不是收银员时显示侧边栏 -->
      <div v-if="role && route.path !== '/' && route.path !== '/register' && role !== 'CASHIER'" class="sidebar glass-sidebar"> 
        <div class="menu-list">
          <!-- 总部菜单 --> 
          <template v-if="role === 'HQ'"> 
            <div class="menu-group-title">核心管理</div>
            
            <div class="menu-item" :class="{ active: isActive('/product') }" @click="go('/product')">
              <el-icon><Goods /></el-icon>
              <span>商品与定价</span>
            </div>

            <div class="menu-item" :class="{ active: isActive('/inventory') }" @click="go('/inventory')">
              <el-icon><Box /></el-icon>
              <span>全局库存</span>
            </div>
            
            <div class="menu-item" :class="{ active: isActive('/transfer') }" @click="go('/transfer')">
              <el-icon><Van /></el-icon>
              <span>库存调拨</span>
            </div>
            
            <div class="menu-group-title">财务与决策</div>

            <div class="menu-item" :class="{ active: isActive('/order') }" @click="go('/order')">
              <el-icon><Wallet /></el-icon>
              <span>财务与所有订单</span>
            </div>
            
            <div class="menu-item" :class="{ active: isActive('/analysis') }" @click="go('/analysis')">
              <el-icon><DataAnalysis /></el-icon>
              <span>数据分析</span>
            </div>
          </template> 

          <!-- 门店菜单 --> 
          <template v-else-if="role === 'STORE'"> 
            <div class="menu-group-title">日常运营</div>
            
            <div class="menu-item" :class="{ active: isActive('/order') }" @click="go('/order')">
              <el-icon><Money /></el-icon>
              <span>订单管理</span>
            </div>
            
            <div class="menu-item" :class="{ active: isActive('/inventory') }" @click="go('/inventory')">
              <el-icon><Box /></el-icon>
              <span>本店库存</span>
            </div>

            <div class="menu-item" :class="{ active: isActive('/transfer') }" @click="go('/transfer')">
              <el-icon><Van /></el-icon>
              <span>店间借货</span>
            </div>
            
            <div class="menu-item" :class="{ active: isActive('/product') }" @click="go('/product')">
              <el-icon><Shop /></el-icon>
              <span>本地商品</span>
            </div>
          </template> 
        </div>

        <!-- 底部系统信息 -->
        <div class="sidebar-footer">
          <div class="version-info">Supermarket OS v1.0</div>
          <div class="support-link" @click="comingSoon">获取技术支持</div>
        </div>
      </div> 

      <!-- 页面展示 (Content Area) --> 
      <div class="content-area" :class="{ 'login-mode': route.path === '/' || route.path === '/register', 'pos-mode': route.path === '/pos' }">
        <div class="content-wrapper" :class="{ 'login-mode': route.path === '/' || route.path === '/register', 'pos-mode': route.path === '/pos' }">
          <router-view v-slot="{ Component }">
            <transition name="fade" mode="out-in">
              <component :is="Component" />
            </transition>
          </router-view>
        </div>
      </div> 
    </div> 
  </div> 
</template>

<style>
/* 全局重置 - Apple 风格基础设置 */
:root {
  /* Apple 风格的色彩系统 */
  --apple-bg: #f5f5f7;
  --apple-text: #1d1d1f;
  --apple-text-light: #86868b;
  --apple-active: #0071e3;
  --glass-bg: rgba(255, 255, 255, 0.75);
  --glass-border: 1px solid rgba(255, 255, 255, 0.4);
  --glass-shadow: 0 4px 24px rgba(0, 0, 0, 0.04);
  
  --el-font-size-base: 15px;
  --el-font-size-small: 13px;
  --el-font-size-large: 17px;
  --el-font-size-extra-large: 20px;
  --el-border-radius-base: 10px; /* 全局组件圆角更加柔和 */
  --el-color-primary: var(--apple-active); /* 全局主色调改为 Apple Blue */
}

body, html {
  margin: 0;
  padding: 0;
  width: 100%;
  height: 100%;
  font-family: -apple-system, BlinkMacSystemFont, "SF Pro SC", "SF Pro Text", "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  background-color: var(--apple-bg);
  color: var(--apple-text);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

#app {
  width: 100%;
  height: 100%;
}

/* 布局容器 */
.app-layout {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
  overflow: hidden;
  background-color: var(--apple-bg);
}

/* 顶部导航栏 - 毛玻璃极简风 */
.top-nav {
  height: 60px;
  background: var(--glass-bg);
  backdrop-filter: saturate(180%) blur(20px);
  -webkit-backdrop-filter: saturate(180%) blur(20px);
  border-bottom: 1px solid rgba(0,0,0,0.05);
  color: var(--apple-text);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 30px;
  z-index: 100;
  position: relative;
}

.brand-container {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-circle {
  width: 32px;
  height: 32px;
  background: #1d1d1f;
  color: white;
  border-radius: 8px; /* 类似 iOS App 图标 */
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
}

.title-wrapper {
  display: flex;
  flex-direction: column;
}

.main-title {
  font-size: 17px;
  font-weight: 600;
  letter-spacing: -0.5px;
  color: var(--apple-text);
}

.sub-title {
  font-size: 10px;
  color: var(--apple-text-light);
  letter-spacing: 0.5px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.top-menu-btn {
  border-radius: 20px !important;
  font-weight: 600 !important;
}

.role-tag {
  font-weight: 500 !important;
  border-radius: 20px;
  padding: 0 12px;
}

.logout-btn {
  transition: all 0.3s ease;
  border: none !important;
  background: transparent !important;
  color: var(--apple-text-light) !important;
}

.logout-btn:hover {
  transform: scale(1.1);
  color: #ff3b30 !important;
}

/* 主内容区 */
.main-container {
  display: flex;
  flex: 1;
  overflow: hidden;
}

/* 侧边栏 - 极致纯净 */
.sidebar {
  width: 280px; /* 加宽侧边栏 */
  background: transparent;
  border-right: 1px solid rgba(0,0,0,0.05);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  z-index: 90;
}

.menu-list {
  padding: 20px 20px; /* 增加两边内边距 */
  flex: 1;
  overflow-y: auto;
}

.menu-group-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--apple-text-light);
  padding: 24px 20px 10px 20px; /* 增加上下留白 */
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 16px; /* 加大图标和文字的距离 */
  padding: 16px 20px; /* 加大内边距 */
  border-radius: 14px; /* 加大圆角 */
  cursor: pointer;
  color: var(--apple-text);
  font-weight: 500;
  font-size: 16px; /* 稍微放大字号 */
  margin-bottom: 16px; /* 加大菜单项之间的距离，填补空白 */
  transition: background-color 0.2s ease, color 0.2s ease;
}

.menu-item:hover {
  background-color: rgba(0,0,0,0.04);
}

.menu-item.active {
  background-color: #e8e8ed; /* Apple 侧边栏选中色 */
  color: var(--apple-text);
  font-weight: 600;
}

.menu-item .el-icon {
  font-size: 20px;
  color: var(--apple-active); /* 图标点缀蓝色 */
}

.menu-item.active .el-icon {
  color: var(--apple-text);
}

.sidebar-footer {
  padding: 20px;
  text-align: center;
}

.version-info {
  font-size: 11px;
  color: var(--apple-text-light);
  margin-bottom: 4px;
}

.support-link {
  font-size: 11px;
  color: var(--apple-active);
  cursor: pointer;
}

.support-link:hover {
  text-decoration: underline;
}

/* 内容区域 - 悬浮卡片感 */
.content-area {
  flex: 1;
  padding: 30px;
  overflow-y: auto;
  background-color: transparent;
}

.content-area.login-mode,
.content-area.pos-mode {
  padding: 0;
  overflow: hidden;
}

.content-wrapper {
  max-width: 1400px;
  margin: 0 auto;
  background: var(--glass-bg);
  backdrop-filter: blur(30px);
  -webkit-backdrop-filter: blur(30px);
  border: var(--glass-border);
  padding: 40px;
  border-radius: 20px;
  min-height: calc(100vh - 120px);
  box-shadow: var(--glass-shadow);
}

.content-wrapper.login-mode,
.content-wrapper.pos-mode {
  padding: 0;
  background: transparent;
  box-shadow: none;
  backdrop-filter: none;
  -webkit-backdrop-filter: none;
  border: none;
  max-width: 100%;
  width: 100%;
  height: 100%;
  border-radius: 0;
  min-height: 100vh;
}

/* 全局组件样式覆盖 (使其更 Apple) */
.el-card {
  border-radius: 16px !important;
  border: none !important;
  box-shadow: 0 4px 16px rgba(0,0,0,0.03) !important;
  background: rgba(255,255,255,0.8) !important;
  backdrop-filter: blur(20px) !important;
}

.el-button {
  border-radius: 8px !important;
  font-weight: 500 !important;
}

.el-table {
  border-radius: 12px !important;
  border: none !important;
  width: 100% !important;
}

.el-table__body-wrapper {
  overflow-x: auto !important;
}

.el-table th.el-table__cell {
  background-color: #f5f5f7 !important;
  color: var(--apple-text-light);
  font-weight: 600;
}

/* 路由动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 移动端适配 */
@media screen and (max-width: 768px) {
  .top-nav { padding: 0 15px; }
  .sidebar { display: none; } /* 移动端可以隐藏侧边栏或改底部，为极致简约直接隐藏或抽屉 */
  .content-area { padding: 15px; }
  .content-wrapper { padding: 20px; border-radius: 16px; }
}
</style>