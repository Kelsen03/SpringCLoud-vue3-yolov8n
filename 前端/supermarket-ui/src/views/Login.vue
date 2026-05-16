<template>
  <div class="landing-wrapper" @scroll="handleScroll">
    <!-- 顶部导航栏 -->
    <header class="landing-header" :class="{ 'scrolled': isScrolled }">
      <div class="logo-area">
        <span class="logo-icon">🛒</span>
        <span class="logo-text">Supermarket OS</span>
      </div>
      <div class="action-area">
        <button class="header-login-btn" @click="showLogin = true">登录系统</button>
      </div>
    </header>

    <!-- 第一屏：首屏轮播与核心标语 -->
    <section class="section hero-section">
      <!-- 背景轮播 -->
      <div class="carousel-background">
        <div 
          v-for="(img, index) in bgImages" 
          :key="index"
          class="bg-image"
          :class="{ active: currentBgIndex === index }"
          :style="{ backgroundImage: `url(${img})` }"
        ></div>
      </div>
      <!-- 磨砂玻璃遮罩 -->
      <div class="glass-overlay"></div>
      
      <div class="hero-content">
        <h1 class="hero-title">重塑现代零售新体验。</h1>
        <p class="hero-subtitle">基于 Spring Cloud 微服务与 YOLOv8 视觉识别的智能连锁超市管理平台，为您提供前所未有的高效运营方案。</p>
        <button class="hero-btn" @click="showLogin = true">立即开启</button>
      </div>
      
      <!-- 向下滚动提示 -->
      <div class="scroll-indicator">
        <div class="mouse-icon"></div>
        <span>向下滚动探索更多</span>
      </div>
    </section>

    <!-- 第二屏：AI 视觉收银 -->
    <section class="section feature-section light-section">
      <div class="feature-container">
        <div class="feature-text">
          <h2 class="feature-title">智能视觉收银</h2>
          <p class="feature-desc">抛弃繁琐的传统扫码。系统深度融合了先进的 YOLOv8 目标检测算法与 OpenCV 色彩分析技术，在极低硬件资源消耗下，实现毫秒级商品精准识别。让收银流程如丝般顺滑，大幅提升门店结账效率。</p>
        </div>
        <div class="feature-image-wrapper">
          <img class="feature-image" src="https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?auto=format&fit=crop&w=1000&q=80" alt="AI Vision Checkout" />
        </div>
      </div>
    </section>

    <!-- 第三屏：微服务架构 -->
    <section class="section feature-section gray-section">
      <div class="feature-container reverse">
        <div class="feature-text">
          <h2 class="feature-title">云原生微服务架构</h2>
          <p class="feature-desc">系统底层采用 Spring Cloud 架构，实现多门店库存数据的物理隔离与逻辑统一。无论业务规模如何扩张，高可用、高并发的分布式节点都能为您提供坚不可摧的底层技术支撑。</p>
        </div>
        <div class="feature-image-wrapper">
          <img class="feature-image" src="https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=1000&q=80" alt="Microservices Architecture" />
        </div>
      </div>
    </section>

    <!-- 第四屏：数据分析与页脚 -->
    <section class="section footer-section">
      <div class="data-feature">
        <h2 class="feature-title">全方位数据洞察</h2>
        <p class="feature-desc">依托 ECharts 强大的可视化能力，实时呈现多维度财务对账与库存分析报表。海量数据一目了然，助您精准掌控商业脉搏，做出更明智的战略决策。</p>
        <img class="data-image" src="https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&w=1200&q=80" alt="Data Analysis Dashboard" />
      </div>

      <footer class="apple-footer">
        <div class="footer-content">
          <div class="footer-left">Copyright © 2026 Supermarket Inc. 保留所有权利。</div>
          <div class="footer-links">
            <a href="#" class="footer-link">隐私政策</a>
            <span class="divider">|</span>
            <a href="#" class="footer-link">使用条款</a>
            <span class="divider">|</span>
            <a href="#" class="footer-link">法律信息</a>
          </div>
          <div class="footer-right">中国大陆</div>
        </div>
      </footer>
    </section>

    <!-- 登录弹窗 (高级毛玻璃 Modal) -->
    <transition name="fade">
      <div v-if="showLogin" class="login-modal-overlay">
        <div class="login-modal-backdrop" @click="showLogin = false"></div>
        <div class="login-modal-content">
          <button class="close-btn" @click="showLogin = false">✕</button>
          
          <div class="modal-header">
            <h2 class="modal-title">登录系统</h2>
            <p class="modal-subtitle">欢迎回来，请输入您的账号密码继续</p>
          </div>
          
          <form class="login-form" @submit.prevent="login">
            <div class="input-group">
              <input type="text" v-model="username" class="premium-input" placeholder="用户名" required />
            </div>
            <div class="input-group">
              <input type="password" v-model="password" class="premium-input" placeholder="密码" required />
            </div>
            
            <button type="submit" class="submit-btn" :disabled="loading">
              {{ loading ? '登录中...' : '继续' }}
            </button>
            
            <div class="register-link">
              <a href="#" @click.prevent="goToRegister">创建收银员账号 ↗</a>
            </div>
          </form>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import request from '@/utils/request'
import { useRouter } from 'vue-router'
import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'

const router = useRouter()

// 状态控制
const username = ref('')
const password = ref('')
const loading = ref(false)
const showLogin = ref(false)
const isScrolled = ref(false)

// 监听容器滚动，控制导航栏背景变化
const handleScroll = (e) => {
  isScrolled.value = e.target.scrollTop > 50
}

// 首屏轮播图逻辑
const bgImages = [
  'https://images.unsplash.com/photo-1542838132-92c53300491e?ixlib=rb-4.0.3&auto=format&fit=crop&w=1920&q=80',
  'https://images.unsplash.com/photo-1604719312566-8912e9227c6a?ixlib=rb-4.0.3&auto=format&fit=crop&w=1920&q=80',
  'https://images.unsplash.com/photo-1583258292688-d0213dc5a3a8?ixlib=rb-4.0.3&auto=format&fit=crop&w=1920&q=80',
  'https://images.unsplash.com/photo-1533900298318-6b8da08a523e?ixlib=rb-4.0.3&auto=format&fit=crop&w=1920&q=80'
]
const currentBgIndex = ref(0)
let bgTimer = null

onMounted(() => {
  bgTimer = setInterval(() => {
    currentBgIndex.value = (currentBgIndex.value + 1) % bgImages.length
  }, 5000)
})

onUnmounted(() => {
  if (bgTimer) clearInterval(bgTimer)
})

// 登录逻辑 (保持原有业务逻辑不变)
const login = async () => {
  if (!username.value || !password.value) {
    ElMessage.warning('请输入用户名和密码')
    return
  }

  loading.value = true
  try {
    const params = new URLSearchParams()
    params.append('username', username.value)
    params.append('password', password.value)
    
    const res = await request.post('/auth/login', params)
    
    if (res.data && res.data.token) {
      localStorage.setItem('token', res.data.token)
      localStorage.setItem('role', res.data.role)
      // 处理 storeId
      if (res.data.storeId) {
        localStorage.setItem('storeId', res.data.storeId)
      } else {
        if (username.value.includes('2')) {
          localStorage.setItem('storeId', '2')
        } else if (username.value.includes('3')) {
          localStorage.setItem('storeId', '3')
        } else {
          localStorage.setItem('storeId', '1')
        }
      }
      localStorage.setItem('username', username.value)
      
      ElMessage.success('登录成功')
      
      // 路由跳转
      if (res.data.role === 'HQ') {
        router.push('/product')
      } else if (res.data.role === 'STORE') {
        router.push('/order')
      } else if (res.data.role === 'CASHIER') {
        router.push('/pos')
      } else {
        router.push('/product')
      }
    } else {
      ElMessage.error(res.data?.msg || '登录失败：用户名或密码错误')
    }
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

// 跳转注册页
const goToRegister = () => {
  router.push('/register')
}
</script>

<style scoped>
/* 全局重置与容器设置 */
.landing-wrapper {
  height: 100vh;
  overflow-y: scroll;
  /* 启用原生的滚动吸附 (Scroll Snapping)，实现一页一页滑动的效果 */
  scroll-snap-type: y mandatory;
  scroll-behavior: smooth;
  font-family: -apple-system, BlinkMacSystemFont, "SF Pro SC", "SF Pro Text", "Helvetica Neue", Helvetica, Arial, sans-serif;
  background-color: #f5f5f7;
}

/* 每一屏的基础样式 */
.section {
  height: 100vh;
  width: 100%;
  scroll-snap-align: start;
  position: relative;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* ================== 顶部导航栏 ================== */
.landing-header {
  position: fixed;
  top: 0; left: 0; right: 0;
  height: 64px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 40px;
  z-index: 100;
  transition: background-color 0.3s ease, backdrop-filter 0.3s ease, box-shadow 0.3s ease;
  background: rgba(255, 255, 255, 0); /* 顶部透明 */
}
/* 滚动后的导航栏形态 (高级毛玻璃) */
.landing-header.scrolled {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: saturate(180%) blur(20px);
  -webkit-backdrop-filter: saturate(180%) blur(20px);
  box-shadow: 0 1px 0 rgba(0, 0, 0, 0.05);
}

.logo-area {
  display: flex;
  align-items: center;
  gap: 8px;
}
.logo-icon { font-size: 24px; }
.logo-text {
  font-size: 18px;
  font-weight: 600;
  color: #1d1d1f;
  letter-spacing: 0.5px;
}

.header-login-btn {
  background: #1d1d1f;
  color: #ffffff;
  border: none;
  padding: 8px 24px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}
.header-login-btn:hover {
  background: #000000;
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

/* ================== 第一屏：Hero Section ================== */
.hero-section {
  justify-content: center;
  align-items: center;
  text-align: center;
}

/* 首屏轮播背景 */
.carousel-background {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  z-index: 1;
  background-color: #f5f5f7;
}
.bg-image {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background-size: cover;
  background-position: center;
  opacity: 0;
  transition: opacity 1.5s ease-in-out, transform 8s linear;
  transform: scale(1.05);
}
.bg-image.active {
  opacity: 1;
  transform: scale(1);
}

/* 首屏浅色毛玻璃遮罩 */
.glass-overlay {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(255, 255, 255, 0.65);
  backdrop-filter: saturate(180%) blur(30px);
  -webkit-backdrop-filter: saturate(180%) blur(30px);
  z-index: 2;
}

.hero-content {
  position: relative;
  z-index: 3;
  max-width: 800px;
  padding: 0 20px;
}
.hero-title {
  font-size: 64px;
  font-weight: 700;
  color: #1d1d1f;
  letter-spacing: -1.5px;
  margin-bottom: 24px;
  line-height: 1.1;
}
.hero-subtitle {
  font-size: 22px;
  color: #424245;
  line-height: 1.5;
  margin-bottom: 48px;
  font-weight: 400;
}
.hero-btn {
  background: #0a84ff;
  color: white;
  border: none;
  padding: 16px 48px;
  border-radius: 30px;
  font-size: 18px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}
.hero-btn:hover {
  background: #007aff;
  transform: scale(1.05);
  box-shadow: 0 8px 24px rgba(10, 132, 255, 0.3);
}

/* 向下滚动提示 */
.scroll-indicator {
  position: absolute;
  bottom: 40px;
  z-index: 3;
  display: flex;
  flex-direction: column;
  align-items: center;
  color: #86868b;
  font-size: 12px;
  animation: bounce 2s infinite;
}
.mouse-icon {
  width: 24px;
  height: 36px;
  border: 2px solid #86868b;
  border-radius: 12px;
  margin-bottom: 8px;
  position: relative;
}
.mouse-icon::before {
  content: '';
  position: absolute;
  top: 6px;
  left: 50%;
  transform: translateX(-50%);
  width: 4px;
  height: 6px;
  background: #86868b;
  border-radius: 2px;
}
@keyframes bounce {
  0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
  40% { transform: translateY(-10px); }
  60% { transform: translateY(-5px); }
}

/* ================== 特性介绍屏 (第二、三屏) ================== */
.light-section { background-color: #ffffff; }
.gray-section { background-color: #f5f5f7; }

.feature-container {
  max-width: 1200px;
  margin: 0 auto;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 40px;
  gap: 80px;
}
.feature-container.reverse {
  flex-direction: row-reverse;
}

.feature-text {
  flex: 1;
}
.feature-title {
  font-size: 48px;
  font-weight: 700;
  color: #1d1d1f;
  margin-bottom: 24px;
  letter-spacing: -0.5px;
}
.feature-desc {
  font-size: 20px;
  color: #86868b;
  line-height: 1.6;
}

.feature-image-wrapper {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
}
.feature-image {
  max-width: 100%;
  border-radius: 24px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.08);
  transition: transform 0.5s ease;
}
.feature-image:hover {
  transform: translateY(-10px);
}

/* ================== 第四屏：数据与页脚 ================== */
.footer-section {
  background-color: #ffffff;
  justify-content: space-between;
}
.data-feature {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 100px 40px 0;
  max-width: 1000px;
  margin: 0 auto;
}
.data-image {
  width: 100%;
  max-width: 800px;
  margin-top: 60px;
  border-radius: 16px 16px 0 0;
  box-shadow: 0 -10px 40px rgba(0, 0, 0, 0.05);
}

/* 底部区域 */
.apple-footer {
  background-color: #f5f5f7;
  padding: 30px 0;
  border-top: 1px solid rgba(0, 0, 0, 0.05);
  width: 100%;
}
.footer-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 40px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: #86868b;
}
.footer-links {
  display: flex;
  align-items: center;
  gap: 12px;
}
.footer-link {
  color: #86868b;
  text-decoration: none;
  transition: color 0.2s;
}
.footer-link:hover {
  color: #1d1d1f;
}
.divider {
  color: rgba(0, 0, 0, 0.2);
}

/* ================== 高级登录弹窗 Modal ================== */
.login-modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
}
.login-modal-backdrop {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(15px);
  -webkit-backdrop-filter: blur(15px);
}
.login-modal-content {
  position: relative;
  width: 100%;
  max-width: 400px;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: saturate(180%) blur(40px);
  -webkit-backdrop-filter: saturate(180%) blur(40px);
  border-radius: 24px;
  padding: 48px 40px;
  box-shadow: 0 24px 48px rgba(0, 0, 0, 0.2);
  z-index: 1001;
  border: 1px solid rgba(255, 255, 255, 0.5);
}

.close-btn {
  position: absolute;
  top: 20px; right: 20px;
  background: rgba(0, 0, 0, 0.05);
  border: none;
  width: 32px; height: 32px;
  border-radius: 50%;
  font-size: 14px;
  color: #86868b;
  cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: all 0.2s ease;
}
.close-btn:hover {
  background: rgba(0, 0, 0, 0.1);
  color: #1d1d1f;
}

.modal-header {
  text-align: center;
  margin-bottom: 40px;
}
.modal-title {
  font-size: 28px;
  font-weight: 600;
  color: #1d1d1f;
  margin: 0 0 8px 0;
  letter-spacing: -0.5px;
}
.modal-subtitle {
  font-size: 14px;
  color: #86868b;
  margin: 0;
}

/* 高级输入框 */
.input-group {
  margin-bottom: 16px;
}
.premium-input {
  width: 100%;
  height: 56px;
  background-color: rgba(0, 0, 0, 0.04);
  border-radius: 12px;
  border: 2px solid transparent;
  padding: 0 16px;
  font-size: 16px;
  color: #1d1d1f;
  box-sizing: border-box;
  outline: none;
  transition: all 0.3s ease;
}
.premium-input::placeholder {
  color: #98989d;
}
.premium-input:focus {
  border-color: #0a84ff;
  background-color: #ffffff;
  box-shadow: 0 0 0 4px rgba(10, 132, 255, 0.15);
}

/* 提交按钮 */
.submit-btn {
  width: 100%;
  height: 52px;
  margin-top: 16px;
  background: #0a84ff;
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 17px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}
.submit-btn:hover {
  background: #007aff;
  box-shadow: 0 4px 12px rgba(10, 132, 255, 0.3);
}
.submit-btn:disabled {
  background: #86868b;
  cursor: not-allowed;
  box-shadow: none;
}

.register-link {
  text-align: center;
  margin-top: 24px;
}
.register-link a {
  color: #0a84ff;
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
}
.register-link a:hover {
  text-decoration: underline;
}

/* Vue 弹窗动画 */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-active .login-modal-content {
  transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}
.fade-leave-active .login-modal-content {
  transition: transform 0.3s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
.fade-enter-from .login-modal-content {
  transform: translateY(20px) scale(0.95);
}
.fade-leave-to .login-modal-content {
  transform: translateY(20px) scale(0.95);
}

/* 移动端适配 */
@media (max-width: 768px) {
  .hero-title { font-size: 40px; }
  .feature-container { flex-direction: column !important; text-align: center; gap: 40px; justify-content: center; }
  .feature-title { font-size: 32px; }
  .landing-header { padding: 0 20px; }
  .footer-content { flex-direction: column; gap: 12px; text-align: center; }
}
</style>
