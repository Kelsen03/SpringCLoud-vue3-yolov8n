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

    <!-- 第一屏：Hero Section -->
    <section class="section hero-section">
      <div class="hero-bg"></div>
      
      <div class="hero-content fade-up">
        <h1 class="hero-title">零售管理，<br>跃入智能世代。</h1>
        <p class="hero-subtitle">基于 Spring Cloud Alibaba 与 YOLOv8 视觉大模型构建。<br>涵盖多门店分布式库存、AI 智能收银及全链路数据洞察，为您重塑高效运营新体验。</p>
        <button class="hero-btn" @click="showLogin = true">登录控制台</button>
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
        <div class="feature-text reveal">
          <h2 class="feature-title">毫秒级 AI 视觉收银</h2>
          <p class="feature-desc">告别传统低效扫码。系统深度集成 YOLOv8 目标检测算法与 OpenCV 图像处理技术，实现商品精准识别与一键无感结算。内置严密的员工交接班盲盘对账机制，让门店前台运营如丝般顺滑且滴水不漏。</p>
        </div>
        <div class="feature-image-wrapper reveal-delay">
          <img class="feature-image" src="https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?auto=format&fit=crop&w=1000&q=80" alt="AI Vision Checkout" />
        </div>
      </div>
    </section>

    <!-- 第三屏：分布式库存调拨 -->
    <section class="section feature-section gray-section">
      <div class="feature-container reverse">
        <div class="feature-text reveal">
          <h2 class="feature-title">全局库存与智能调拨</h2>
          <p class="feature-desc">依托云原生微服务架构，完美实现多门店物理数据隔离与逻辑统一。支持总部强制补货下发与门店间双向借货审批流，辅以底层原子级库存扣减与 FIFO 效期预警机制，彻底告别库存积压与断货危机。</p>
        </div>
        <div class="feature-image-wrapper reveal-delay">
          <img class="feature-image" src="https://images.unsplash.com/photo-1553413077-190dd305871c?auto=format&fit=crop&w=1000&q=80" alt="Global Inventory" />
        </div>
      </div>
    </section>

    <!-- 第四屏：数据分析与页脚 -->
    <section class="section footer-section light-section">
      <div class="data-feature">
        <div class="feature-text text-center reveal">
          <h2 class="feature-title">全景商业数据罗盘</h2>
          <p class="feature-desc" style="max-width: 800px; margin: 0 auto;">无缝集成 ECharts 可视化引擎，实时聚合各门店营业额、客单价与热销商品排行。多维度穿透分析商业数据，助您精准洞察市场脉搏，驱动科学商业决策。</p>
        </div>
        <img class="data-image reveal-delay" src="https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&w=1200&q=80" alt="Data Analysis Dashboard" />
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

    <!-- 登录与注册弹窗 (3D翻转 Modal) -->
    <transition name="fade">
      <div v-if="showLogin" class="login-modal-overlay">
        <div class="login-modal-backdrop" @click="showLogin = false"></div>
        
        <div class="perspective-container">
          <div class="flipper" :class="{ 'is-flipped': isFlipped }">
            
            <!-- 正面：登录 -->
            <div class="side front">
              <button class="close-btn" @click="showLogin = false">✕</button>
              
              <div class="modal-header">
                <h2 class="modal-title">登录系统</h2>
                <p class="modal-subtitle">欢迎回来，请输入您的账号密码继续</p>
              </div>
              
              <form class="login-form" @submit.prevent="login">
                <div class="apple-input-group" :class="{ 'has-value': username }">
                  <label class="apple-floating-label">用户名</label>
                  <input type="text" v-model="username" class="premium-input" required />
                </div>
                <div class="apple-input-group" :class="{ 'has-value': password }" style="margin-top: 16px;">
                  <label class="apple-floating-label">密码</label>
                  <input type="password" v-model="password" class="premium-input" required />
                </div>
                
                <button type="submit" class="submit-btn" :disabled="loading">
                  {{ loading ? '登录中...' : '继续' }}
                </button>
                
                <div class="register-link">
                  <a href="#" @click.prevent="isFlipped = true">创建收银员账号 ↗</a>
                </div>
              </form>
            </div>

            <!-- 背面：注册 -->
            <div class="side back">
              <button class="close-btn" @click="showLogin = false">✕</button>
              
              <div class="modal-header" style="margin-bottom: 24px;">
                <h2 class="modal-title">创建账号</h2>
                <p class="modal-subtitle">加入我们，开启智能零售体验</p>
              </div>
              
              <el-form class="login-form" :model="regForm" :rules="regRules" ref="regFormRef" @submit.prevent>
                <el-form-item prop="name">
                  <div class="apple-input-group" :class="{ 'has-value': regForm.name }">
                    <label class="apple-floating-label">姓名全拼 (如: lkq)</label>
                    <input type="text" v-model="regForm.name" class="premium-input" @input="generateUsername" required />
                  </div>
                </el-form-item>

                <el-form-item prop="storeId">
                  <div class="apple-input-group has-value">
                    <label class="apple-floating-label" style="top: 16px; font-size: 12px;">所在门店</label>
                    <el-select v-model="regForm.storeId" placeholder=" " @change="generateUsername" style="width: 100%;">
                      <el-option label="1号店 (总店)" value="1" />
                      <el-option label="2号店 (分店)" value="2" />
                      <el-option label="3号店 (分店)" value="3" />
                    </el-select>
                  </div>
                </el-form-item>
                
                <el-form-item prop="password">
                  <div class="apple-input-group" :class="{ 'has-value': regForm.password }">
                    <label class="apple-floating-label">密码</label>
                    <input type="password" v-model="regForm.password" class="premium-input" required />
                  </div>
                </el-form-item>

                <el-form-item prop="confirmPassword">
                  <div class="apple-input-group" :class="{ 'has-value': regForm.confirmPassword }">
                    <label class="apple-floating-label">确认密码</label>
                    <input type="password" v-model="regForm.confirmPassword" class="premium-input" required />
                  </div>
                </el-form-item>

                <div class="account-preview" v-if="regForm.username">
                  <div class="apple-alert">
                    <div class="alert-title">分配账号: <strong>{{ regForm.username }}</strong></div>
                  </div>
                </div>

                <button type="button" class="submit-btn" :disabled="regLoading" @click="handleRegister" style="margin-top: 8px;">
                  {{ regLoading ? '注册中...' : '注册' }}
                </button>

                <div class="register-link">
                  <a href="#" @click.prevent="isFlipped = false">已有账号？返回登录 ↗</a>
                </div>
              </el-form>
            </div>
            
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import request from '@/utils/request'
import { useRouter } from 'vue-router'
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'

const router = useRouter()

// ================== 状态控制 ==================
const username = ref('')
const password = ref('')
const loading = ref(false)
const showLogin = ref(false)
const isScrolled = ref(false)
const isFlipped = ref(false) // 控制 3D 翻转

// 监听容器滚动，控制导航栏背景变化
const handleScroll = (e) => {
  isScrolled.value = e.target.scrollTop > 50
}

// ================== 登录逻辑 ==================
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

// ================== 注册逻辑 ==================
const regFormRef = ref(null)
const regLoading = ref(false)

const regForm = reactive({
  name: '',
  storeId: '',
  password: '',
  confirmPassword: '',
  username: '' 
})

const validatePass2 = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请再次输入密码'))
  } else if (value !== regForm.password) {
    callback(new Error('两次输入密码不一致!'))
  } else {
    callback()
  }
}

const regRules = reactive({
  name: [
    { required: true, message: '请输入姓名全拼或首字母缩写', trigger: 'blur' },
    { pattern: /^[a-zA-Z]+$/, message: '只能输入英文字母', trigger: 'blur' }
  ],
  storeId: [
    { required: true, message: '请选择所在门店', trigger: 'change' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能小于6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, validator: validatePass2, trigger: 'blur' }
  ]
})

const generateUsername = () => {
  if (regForm.name && regForm.storeId) {
    const today = new Date()
    const year = today.getFullYear()
    const month = String(today.getMonth() + 1).padStart(2, '0')
    const day = String(today.getDate()).padStart(2, '0')
    const dateStr = `${year}${month}${day}`
    
    const storeCode = String(regForm.storeId).padStart(2, '0')
    regForm.username = `${regForm.name.toLowerCase()}${storeCode}${dateStr}`
  } else {
    regForm.username = ''
  }
}

const handleRegister = async () => {
  if (!regFormRef.value) return
  await regFormRef.value.validate(async (valid) => {
    if (valid) {
      regLoading.value = true
      try {
        const res = await request.post('/auth/register', {
          username: regForm.username,
          password: regForm.password,
          role: 'CASHIER', 
          storeId: Number(regForm.storeId), 
          realName: regForm.name
        })
        const responseData = res.data || res
        const isSuccess = responseData.code === 0 || responseData.code === 200
        
        if (isSuccess) { 
           ElMessage.success(`注册成功！请使用账号 ${regForm.username} 登录。`)
           // 自动填充账号密码，并翻转回登录面
           username.value = regForm.username
           password.value = regForm.password
           setTimeout(() => {
             isFlipped.value = false
           }, 800)
        } else {
           ElMessage.error(responseData.message || responseData.msg || '注册失败')
        }
      } catch (e) {
        console.error(e)
        ElMessage.error(e.response?.data?.message || e.message || '注册失败，请检查网络')
      } finally {
        regLoading.value = false
      }
    }
  })
}
</script>

<style scoped>
/* 全局重置与容器设置 */
.landing-wrapper {
  height: 100vh;
  overflow-y: scroll;
  /* 启用原生的滚动吸附，实现一页一页丝滑滑动 */
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
  transition: background-color 0.4s ease, backdrop-filter 0.4s ease, box-shadow 0.4s ease;
  background: rgba(255, 255, 255, 0); 
}
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
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
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

.hero-bg {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: radial-gradient(circle at 50% -20%, #e5e5ea 0%, #f5f5f7 80%);
  z-index: 1;
}

.hero-content {
  position: relative;
  z-index: 3;
  max-width: 800px;
  padding: 0 20px;
}

/* 渐显上浮动画 */
.fade-up {
  animation: fadeUpAnim 1.2s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

@keyframes fadeUpAnim {
  0% { opacity: 0; transform: translateY(40px); }
  100% { opacity: 1; transform: translateY(0); }
}

.hero-title {
  font-size: 72px;
  font-weight: 700;
  color: #1d1d1f;
  letter-spacing: -2px;
  margin-bottom: 24px;
  line-height: 1.1;
  background: linear-gradient(135deg, #1d1d1f 0%, #434345 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
.hero-subtitle {
  font-size: 22px;
  color: #86868b;
  line-height: 1.6;
  margin-bottom: 48px;
  font-weight: 400;
}
.hero-btn {
  background: #0a84ff;
  color: white;
  border: none;
  padding: 18px 56px;
  border-radius: 30px;
  font-size: 18px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
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
  letter-spacing: -1px;
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
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.08);
  transition: transform 0.6s cubic-bezier(0.16, 1, 0.3, 1);
}
.feature-image:hover {
  transform: translateY(-15px) scale(1.02);
}

/* 简单的滚动视差效果类 */
.reveal {
  animation: fadeUpAnim 1.2s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}
.reveal-delay {
  animation: fadeUpAnim 1.2s cubic-bezier(0.16, 1, 0.3, 1) 0.2s forwards;
  opacity: 0;
}

/* ================== 第四屏：数据与页脚 ================== */
.footer-section {
  justify-content: space-between;
}
.data-feature {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 100px 40px 0;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}
.text-center {
  text-align: center;
}
.data-image {
  width: 100%;
  max-width: 900px;
  margin-top: 60px;
  border-radius: 16px 16px 0 0;
  box-shadow: 0 -10px 40px rgba(0, 0, 0, 0.06);
  transition: transform 0.6s ease;
}
.data-image:hover {
  transform: translateY(-10px);
}

/* 底部区域 */
.apple-footer {
  background-color: #f5f5f7;
  padding: 30px 0;
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

/* ================== 高级登录与注册弹窗 Modal + 3D翻转 ================== */
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

/* 3D 透视容器 */
.perspective-container {
  perspective: 1500px;
  width: 100%;
  max-width: 420px;
  height: 620px; /* 固定高度以容纳两面的表单 */
  z-index: 1001;
  position: relative;
}

/* 翻转体 */
.flipper {
  width: 100%;
  height: 100%;
  position: relative;
  transition: transform 0.8s cubic-bezier(0.2, 0.8, 0.2, 1);
  transform-style: preserve-3d;
}
.flipper.is-flipped {
  transform: rotateY(180deg);
}

/* 每一面的通用样式 */
.side {
  position: absolute;
  top: 0; left: 0;
  width: 100%; height: 100%;
  backface-visibility: hidden;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: saturate(180%) blur(40px);
  -webkit-backdrop-filter: saturate(180%) blur(40px);
  border-radius: 24px;
  padding: 40px;
  box-shadow: 0 24px 48px rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.5);
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.front {
  transform: rotateY(0deg);
}

.back {
  transform: rotateY(180deg);
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
  z-index: 20;
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

/* 高级输入框 - 带有悬浮标签动画 */
.apple-input-group {
  position: relative;
  width: 100%;
  height: 56px;
  background-color: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 12px;
  transition: border-color 0.2s ease, box-shadow 0.2s ease, background-color 0.2s ease;
  box-sizing: border-box;
}

.apple-input-group:focus-within {
  border-color: #0a84ff;
  background-color: rgba(255, 255, 255, 0.9);
  box-shadow: 0 0 0 4px rgba(10, 132, 255, 0.2);
}

.apple-floating-label {
  position: absolute;
  left: 16px;
  top: 50%;
  transform: translateY(-50%);
  color: #98989d;
  font-size: 17px;
  pointer-events: none;
  transition: all 0.2s cubic-bezier(0.25, 0.8, 0.25, 1);
  z-index: 10;
}

.apple-input-group:focus-within .apple-floating-label,
.apple-input-group.has-value .apple-floating-label {
  top: 16px;
  font-size: 12px;
  color: #86868b;
}

.premium-input {
  width: 100%;
  height: 100%;
  background-color: transparent;
  border: none;
  padding: 18px 16px 0 16px; 
  font-size: 17px;
  color: #1d1d1f;
  box-sizing: border-box;
  outline: none;
}

/* Vue Element 表单重写，以适应在背面展示 */
:deep(.el-form-item) {
  margin-bottom: 16px;
}
:deep(.el-form-item__error) {
  padding-top: 4px;
}

:deep(.el-select) {
  width: 100%;
  height: 100%;
}
:deep(.el-select__wrapper) {
  background: transparent !important;
  box-shadow: none !important;
  border: none !important;
  padding: 18px 16px 0 16px !important;
  min-height: 100% !important;
  height: 100% !important;
  box-sizing: border-box !important;
}
:deep(.el-select__placeholder),
:deep(.el-select__selected-item) {
  font-size: 17px !important;
  color: #1d1d1f !important;
}

/* 注册成功预览 */
.apple-alert {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 12px;
  padding: 12px;
  margin-bottom: 16px;
  text-align: center;
}
.alert-title {
  font-size: 14px;
  color: #1d1d1f;
}

/* 提交按钮 */
.submit-btn {
  width: 100%;
  height: 52px;
  margin-top: 24px;
  background: #0a84ff;
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 17px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
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
.fade-enter-active .perspective-container {
  transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}
.fade-leave-active .perspective-container {
  transition: transform 0.3s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
.fade-enter-from .perspective-container {
  transform: translateY(20px) scale(0.95);
}
.fade-leave-to .perspective-container {
  transform: translateY(20px) scale(0.95);
}

/* 移动端适配 */
@media (max-width: 768px) {
  .hero-title { font-size: 48px; }
  .feature-container { flex-direction: column !important; text-align: center; gap: 40px; justify-content: center; }
  .feature-title { font-size: 32px; }
  .landing-header { padding: 0 20px; }
  .footer-content { flex-direction: column; gap: 12px; text-align: center; }
}
</style>