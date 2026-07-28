<script setup> 
import { useRouter, useRoute } from 'vue-router' 
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { Monitor, Shop, DataAnalysis, Box, Money, SwitchButton, Goods, Van, ShoppingCart, Tools, Ticket, Service, Wallet, User, Setting, Document, Calendar, ArrowRight } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import Lenis from '@studio-freight/lenis'
import gsap from 'gsap'

const router = useRouter() 
const route = useRoute()
const role = ref(localStorage.getItem('role'))
const customCursor = ref(null)
const cursorState = ref('default') // default, hover

// 监听路由变化，实时更新 role
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

const isActive = (path) => {
  return route.path === path
}

// 初始化平滑滚动 (Lenis) 和自定义光标
onMounted(() => {
  // 1. 只有在非移动端才启用 Lenis 平滑滚动，避免移动端冲突
  if (window.innerWidth > 768) {
    // 修复首页无法滚动的问题：如果当前是首页（使用 scroll-snap），则禁用 lenis
    if (route.path !== '/' && route.path !== '/register') {
      const lenis = new Lenis({
        duration: 1.2,
        easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)), 
        direction: 'vertical',
        gestureDirection: 'vertical',
        smooth: true,
        mouseMultiplier: 1,
        smoothTouch: false,
        touchMultiplier: 2,
        infinite: false,
      })

      function raf(time) {
        lenis.raf(time)
        requestAnimationFrame(raf)
      }
      requestAnimationFrame(raf)
    }
  }

  // 2. 自定义光标逻辑
  const cursor = customCursor.value
  if (cursor && window.innerWidth > 768) {
    // 监听鼠标移动
    window.addEventListener('mousemove', (e) => {
      // 使用 GSAP 平滑跟随
      gsap.to(cursor, {
        x: e.clientX,
        y: e.clientY,
        duration: 0.15,
        ease: "power2.out"
      })
    })

    // 监听所有可点击元素的 hover 状态
    const handleMouseOver = (e) => {
      const target = e.target.closest('button, a, .menu-item, input, select, .el-table__row, .hero-btn')
      if (target) {
        cursorState.value = 'hover'
      } else {
        cursorState.value = 'default'
      }
    }
    window.addEventListener('mouseover', handleMouseOver)
  }
})
</script> 

<template> 
  <div class="app-layout" :class="{ 'is-dashboard': role && route.path !== '/' && route.path !== '/register' }"> 
    <!-- 渡边风格的自定义光标 -->
    <div ref="customCursor" class="custom-cursor" :class="cursorState"></div>

    <!-- 极简白色顶部导航栏 -->
    <header v-if="role && route.path !== '/' && route.path !== '/register'" class="minimal-header"> 
      <div class="brand-container" @click="go(role === 'HQ' ? '/product' : '/order')">
        <span class="logo-text">LKQ.</span>
        <span class="sub-title">连锁超市 Retail System</span>
      </div>

      <div class="nav-links" v-if="role !== 'CASHIER'">
        <template v-if="role === 'HQ'">
          <a class="nav-item" :class="{ active: isActive('/product') }" @click="go('/product')">商品 <span class="nav-en">Product</span></a>
          <a class="nav-item" :class="{ active: isActive('/inventory') }" @click="go('/inventory')">库存 <span class="nav-en">Inventory</span></a>
          <a class="nav-item" :class="{ active: isActive('/transfer') }" @click="go('/transfer')">调拨 <span class="nav-en">Transfer</span></a>
          <a class="nav-item" :class="{ active: isActive('/order') }" @click="go('/order')">订单 <span class="nav-en">Orders</span></a>
          <a class="nav-item" :class="{ active: isActive('/analysis') }" @click="go('/analysis')">数据 <span class="nav-en">Analysis</span></a>
        </template>
        <template v-else-if="role === 'STORE'">
          <a class="nav-item" :class="{ active: isActive('/order') }" @click="go('/order')">订单 <span class="nav-en">Orders</span></a>
          <a class="nav-item" :class="{ active: isActive('/inventory') }" @click="go('/inventory')">库存 <span class="nav-en">Local Stock</span></a>
          <a class="nav-item" :class="{ active: isActive('/transfer') }" @click="go('/transfer')">借货 <span class="nav-en">Transfer</span></a>
          <a class="nav-item" :class="{ active: isActive('/product') }" @click="go('/product')">商品 <span class="nav-en">Products</span></a>
        </template>
      </div>

      <div class="user-info">
        <el-button 
          v-if="role === 'CASHIER'"
          class="top-menu-btn"
          type="primary"
          round
          @click="go('/pos')"
        >
          收银台 / POS
        </el-button>

        <span class="role-text">{{ role }}</span>
        
        <button class="logout-text-btn" @click="logout">Logout</button> 
      </div>
    </header> 

    <main class="main-container"> 
      <div class="content-area">
        <router-view v-slot="{ Component }">
          <transition name="page-fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </div> 
    </main> 
  </div> 
</template>

<style>
/* 渡边风格全局重置 - 极致纯净白底黑字 */
:root {
  --w-bg: #ffffff;
  --w-text: #000000;
  --w-text-gray: #888888;
  --w-accent: #000000; /* 纯黑作为点缀色 */
  --w-border: rgba(0, 0, 0, 0.1);
  --w-hover-bg: #f5f5f5;
  
  --el-color-primary: #000000;
  --el-border-radius-base: 0px; /* 极简风格通常去圆角，使用直角或超大圆角，这里采用锐利风格 */
}

/* A4 打印优化 */
@media print {
  @page {
    size: A4;
    margin: 2cm;
  }
  body {
    background: white !important;
    color: black !important;
    -webkit-print-color-adjust: exact;
  }
  .minimal-header, .custom-cursor, .hero-bg, .scroll-indicator {
    display: none !important;
  }
  /* 确保打印时不要背景色，文字全黑 */
  .el-card, .el-table, .el-table th.el-table__cell, .el-table tr {
    background: transparent !important;
    border: none !important;
    color: black !important;
    box-shadow: none !important;
  }
  .el-table td, .el-table th {
    border-bottom: 1px solid #000 !important;
  }
  /* 避免表格在页中间被截断 */
  .el-table {
    page-break-inside: auto;
  }
  tr {
    page-break-inside: avoid;
    page-break-after: auto;
  }
}

body, html {
  margin: 0;
  padding: 0;
  width: 100%;
  min-height: 100%;
  /* 极简无衬线字体，极度干净 */
  font-family: 'Helvetica Neue', Helvetica, Arial, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
  background-color: var(--w-bg);
  color: var(--w-text);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  /* 隐藏默认鼠标，给自定义光标让路 */
  cursor: none;
}

/* 覆盖所有元素的鼠标样式 */
a, button, input, select, textarea, .el-table__row {
  cursor: none !important;
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
  min-height: 100vh;
  background-color: var(--w-bg);
}

/* 自定义光标 */
.custom-cursor {
  position: fixed;
  top: 0;
  left: 0;
  width: 12px;
  height: 12px;
  background-color: rgba(0, 0, 0, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.8);
  border-radius: 50%;
  pointer-events: none;
  z-index: 99999;
  transform: translate(-50%, -50%);
  transition: width 0.3s cubic-bezier(0.16, 1, 0.3, 1), height 0.3s cubic-bezier(0.16, 1, 0.3, 1), background-color 0.3s ease;
  mix-blend-mode: normal; /* 移除 difference 以确保在各种背景下都清晰可见 */
}

.custom-cursor.hover {
  width: 48px;
  height: 48px;
  background-color: rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
}

/* 极简顶部导航栏 */
.minimal-header {
  position: fixed;
  top: 0; left: 0; right: 0;
  height: 80px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-bottom: 1px solid var(--w-border);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 40px;
  z-index: 100;
}

.brand-container {
  display: flex;
  align-items: baseline;
  gap: 8px;
}

.logo-text {
  font-size: 24px;
  font-weight: 800;
  letter-spacing: -1px;
}

.sub-title {
  font-size: 12px;
  color: var(--w-text-gray);
  text-transform: uppercase;
  letter-spacing: 2px;
}

.nav-links {
  display: flex;
  gap: 32px;
}

.nav-item {
  font-size: 15px;
  font-weight: 600;
  color: var(--w-text-gray);
  letter-spacing: 1px;
  position: relative;
  transition: color 0.3s ease;
  display: flex;
  align-items: baseline;
  gap: 4px;
}

.nav-en {
  font-size: 11px;
  font-weight: 500;
  text-transform: uppercase;
  opacity: 0.6;
}

.nav-item:hover, .nav-item.active {
  color: var(--w-text);
}

.nav-item::after {
  content: '';
  position: absolute;
  bottom: -4px;
  left: 0;
  width: 0;
  height: 1px;
  background-color: var(--w-text);
  transition: width 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.nav-item.active::after {
  width: 100%;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 24px;
}

.role-text {
  font-size: 12px;
  font-weight: 600;
  padding: 4px 12px;
  border: 1px solid var(--w-text);
  border-radius: 20px;
  text-transform: uppercase;
}

.logout-text-btn {
  background: transparent;
  border: none;
  font-size: 14px;
  font-weight: 500;
  color: var(--w-text);
  position: relative;
  padding: 0;
}

.logout-text-btn::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 100%;
  height: 1px;
  background-color: var(--w-text);
  transform: scaleX(0);
  transform-origin: right;
  transition: transform 0.3s ease;
}

.logout-text-btn:hover::after {
  transform: scaleX(1);
  transform-origin: left;
}

/* 主内容区 */
.main-container {
  flex: 1;
  width: 100%;
  padding-top: 80px; /* 留出头部高度 */
}

.content-area {
  max-width: 1600px;
  margin: 0 auto;
  padding: 40px;
  min-height: calc(100vh - 80px);
}

/* 当不需要头部时（如登录页） */
.app-layout:not(.is-dashboard) .main-container {
  padding-top: 0;
}
.app-layout:not(.is-dashboard) .content-area {
  max-width: 100%;
  padding: 0;
}

/* 全局组件样式重写 - 极简化 */
.el-card {
  border-radius: 0 !important;
  border: 1px solid var(--w-border) !important;
  box-shadow: none !important;
  background: transparent !important;
}

.el-button {
  border-radius: 0 !important;
  font-weight: 600 !important;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.el-button--primary {
  background-color: var(--w-text) !important;
  border-color: var(--w-text) !important;
  color: var(--w-bg) !important;
}

.el-button--primary:hover {
  background-color: var(--w-text-gray) !important;
  border-color: var(--w-text-gray) !important;
}

.el-table {
  border-radius: 0 !important;
  border: none !important;
  background-color: transparent !important;
}

.el-table th.el-table__cell {
  background-color: transparent !important;
  color: var(--w-text);
  font-weight: 600;
  border-bottom: 2px solid var(--w-text) !important;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.el-table td.el-table__cell {
  border-bottom: 1px solid var(--w-border) !important;
  background-color: transparent !important;
}

.el-table--striped .el-table__body tr.el-table__row--striped td.el-table__cell {
  background-color: #fafafa !important;
}

.el-tag {
  border-radius: 0 !important;
  border: 1px solid var(--w-border) !important;
}

/* 页面切换动画 */
.page-fade-enter-active,
.page-fade-leave-active {
  transition: opacity 0.6s cubic-bezier(0.16, 1, 0.3, 1), transform 0.6s cubic-bezier(0.16, 1, 0.3, 1);
}
.page-fade-enter-from {
  opacity: 0;
  transform: translateY(20px);
}
.page-fade-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}

@media screen and (max-width: 768px) {
  .minimal-header { padding: 0 20px; }
  .nav-links { display: none; } /* 移动端隐藏横向菜单 */
  .content-area { padding: 20px; }
  .custom-cursor { display: none; } /* 移动端不需要自定义光标 */
  body, html { cursor: auto; }
  a, button, input, select, textarea, .el-table__row { cursor: auto !important; }
}
</style>