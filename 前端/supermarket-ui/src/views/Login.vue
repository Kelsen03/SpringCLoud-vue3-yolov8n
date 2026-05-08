<template>
  <div class="login-page">
    <!-- 动态流光背景 -->
    <div class="ambient-background">
      <div class="blob blob-1"></div>
      <div class="blob blob-2"></div>
      <div class="blob blob-3"></div>
    </div>
    <!-- 全屏毛玻璃遮罩 -->
    <div class="glass-overlay"></div>

    <div class="content-layer">
      <div class="system-brand">
      <div class="logo-circle">🛒</div>
      <span class="system-name">连锁超市微服务管理系统</span>
    </div>

    <div class="main-content">
      <div class="login-container">
        <div class="card-header">
          <h2 class="login-title">智能收银，一触即达。</h2>
        </div>
        
        <el-form class="login-form" @submit.prevent>
          <el-form-item>
            <div class="apple-input-group" :class="{ 'has-value': username }">
              <label class="apple-floating-label">用户名</label>
              <el-input v-model="username" />
            </div>
          </el-form-item>
          
          <el-form-item>
            <div class="apple-input-group" :class="{ 'has-value': password }">
              <label class="apple-floating-label">密码</label>
              <el-input 
                v-model="password" 
                type="password" 
                show-password 
                @keyup.enter="login" 
              />
            </div>
          </el-form-item>

          <div class="link-container">
            <el-link type="primary" :underline="false" @click="router.push('/register')">创建收银员账号 ↗</el-link>
          </div>

          <div class="info-paragraph">
            <div class="info-icon-wrapper">
              <el-icon><UserFilled /></el-icon>
            </div>
            <p>本超市管理系统基于 Spring Cloud 微服务与 Vue3 构建，集成了多门店库存隔离、智能扫码收银及 YOLOv5 图像视觉识别等核心模块，旨在为您提供高效、安全的零售管理体验。</p>
          </div>
          
          <el-form-item class="submit-item">
            <el-button 
              class="apple-button" 
              type="primary" 
              :loading="loading"
              @click="login"
            >
              继续
            </el-button>
          </el-form-item>
        </el-form>
      </div>
    </div>

    <div class="apple-footer">
        <div class="footer-content">
          <div class="footer-left">Copyright © 2026 Supermarket Inc. 保留所有权利。</div>
          <div class="footer-links">
            <el-link :underline="false">隐私政策</el-link>
            <span class="divider">|</span>
            <el-link :underline="false">使用条款</el-link>
            <span class="divider">|</span>
            <el-link :underline="false">法律信息</el-link>
          </div>
          <div class="footer-right">中国大陆</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import request from '@/utils/request'
import { useRouter } from 'vue-router'
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { UserFilled, Platform, Search, Goods } from '@element-plus/icons-vue'

const router = useRouter()
const username = ref('')
const password = ref('')
const loading = ref(false)

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
      // 如果后端返回了 storeId，则存储它
      if (res.data.storeId) {
        localStorage.setItem('storeId', res.data.storeId)
      } else {
        // [临时补丁] 如果后端没返回 storeId，根据用户名猜测
        if (username.value.includes('2')) {
          localStorage.setItem('storeId', '2')
        } else if (username.value.includes('3')) {
          localStorage.setItem('storeId', '3')
        } else {
          localStorage.setItem('storeId', '1')
        }
      }
      // 保存当前登录的用户名(作为收银员账号)
      localStorage.setItem('username', username.value)
      
      ElMessage.success('登录成功')
      if (res.data.role === 'HQ') {
        router.push('/product')
      } else if (res.data.role === 'STORE') {
        router.push('/order')
      } else if (res.data.role === 'CASHIER') {
        router.push('/pos')
      } else {
        router.push('/product') // 默认fallback
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
</script>

<style scoped>
.login-page {
  position: relative;
  min-height: 100vh;
  overflow: hidden;
  background-color: #000000;
  font-family: -apple-system, BlinkMacSystemFont, "SF Pro SC", "SF Pro Text", "Helvetica Neue", Helvetica, Arial, sans-serif;
}

/* 深色动态流光背景 */
.ambient-background {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  overflow: hidden;
  z-index: 1;
}

.blob {
  position: absolute;
  filter: blur(100px);
  opacity: 0.8;
  animation: darkFloat 15s infinite ease-in-out alternate;
  border-radius: 50%;
}

.blob-1 { top: -20%; left: -10%; width: 60vw; height: 60vw; background: #001540; animation-delay: 0s; }
.blob-2 { bottom: -20%; right: -10%; width: 70vw; height: 70vw; background: #1a0033; animation-delay: -5s; }
.blob-3 { top: 30%; left: 20%; width: 50vw; height: 50vw; background: #002244; animation-delay: -10s; }

@keyframes darkFloat {
  0% { transform: translate(0, 0) scale(1) rotate(0deg); }
  33% { transform: translate(5%, 10%) scale(1.1) rotate(10deg); }
  66% { transform: translate(-5%, -5%) scale(0.9) rotate(-5deg); }
  100% { transform: translate(2%, -10%) scale(1.05) rotate(5deg); }
}

/* 全屏深色毛玻璃遮罩 */
.glass-overlay {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(10, 10, 15, 0.7);
  backdrop-filter: saturate(180%) blur(80px);
  -webkit-backdrop-filter: saturate(180%) blur(80px);
  z-index: 2;
}

/* 内容层 */
.content-layer {
  position: relative;
  z-index: 3;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

/* 左上角系统 Logo (深色模式适配) */
.system-brand {
  position: absolute;
  top: 30px;
  left: 40px;
  display: flex;
  align-items: center;
  gap: 12px;
  z-index: 10;
}

.logo-circle {
  width: 32px;
  height: 32px;
  background: rgba(255, 255, 255, 0.1);
  color: #ffffff;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  backdrop-filter: blur(10px);
}

.system-name {
  font-size: 16px;
  font-weight: 600;
  color: #f5f5f7;
  letter-spacing: 0.5px;
}

/* 主内容区 */
.main-content {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
}

.login-container {
  width: 100%;
  max-width: 420px;
  box-sizing: border-box;
}

.card-header {
  text-align: center;
  margin-bottom: 32px;
}

.login-title {
  margin: 0;
  font-size: 28px;
  font-weight: 600;
  color: #f5f5f7;
  letter-spacing: -0.5px;
}

.apple-input-group {
  position: relative;
  width: 100%;
  height: 56px;
  background-color: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 12px;
  transition: border-color 0.2s ease, box-shadow 0.2s ease, background-color 0.2s ease;
  box-sizing: border-box;
}

.apple-input-group:focus-within {
  border-color: #0a84ff;
  background-color: rgba(255, 255, 255, 0.1);
  box-shadow: 0 0 0 4px rgba(10, 132, 255, 0.3);
}

.apple-floating-label {
  position: absolute;
  left: 16px;
  top: 50%;
  transform: translateY(-50%);
  color: #98989d;
  font-size: 17px;
  pointer-events: none;
  transition: all 0.2s ease;
  z-index: 10;
}

.apple-input-group:focus-within .apple-floating-label,
.apple-input-group.has-value .apple-floating-label {
  top: 16px;
  font-size: 12px;
  color: #86868b;
}

:deep(.el-form-item) {
  margin-bottom: 16px;
}

:deep(.el-input) {
  height: 100%;
}

:deep(.el-input__wrapper) {
  background: transparent !important;
  box-shadow: none !important;
  border: none !important;
  padding: 0 16px !important;
  height: 100%;
}

:deep(.el-input__inner) {
  height: 100% !important;
  padding-top: 18px !important;
  font-size: 17px !important;
  color: #f5f5f7 !important;
}

:deep(.el-input__suffix) {
  align-items: center;
}

/* 适配 Select 组件 - 新思路 */
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

:deep(.el-select .el-input__wrapper) {
  background: transparent !important;
  box-shadow: none !important;
  border: none !important;
  padding: 18px 16px 0 16px !important;
  height: 100% !important;
  box-sizing: border-box !important;
}

:deep(.el-select__placeholder),
:deep(.el-select__selected-item),
:deep(.el-select .el-input__inner) {
  font-size: 17px !important;
  color: #f5f5f7 !important;
  -webkit-text-fill-color: #f5f5f7 !important;
  line-height: normal !important;
  height: auto !important;
  padding: 0 !important;
}

:deep(.el-select__selected-item span) {
  color: #f5f5f7 !important;
  -webkit-text-fill-color: #f5f5f7 !important;
}

:deep(.el-select__placeholder.is-transparent) {
  color: transparent !important;
  -webkit-text-fill-color: transparent !important;
}

.link-container {
  text-align: left;
  margin-top: -8px;
  margin-bottom: 24px;
  padding-left: 8px;
}

.link-container .el-link {
  font-size: 14px;
  color: #0a84ff;
}

.info-paragraph {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 32px;
  text-align: left;
}

.info-icon-wrapper {
  color: #0a84ff;
  font-size: 24px;
  margin-top: 2px;
}

.info-paragraph p {
  margin: 0;
  font-size: 12px;
  color: #86868b;
  line-height: 1.5;
}

.inline-link {
  font-size: 12px;
  color: #0a84ff;
  vertical-align: baseline;
}

.submit-item {
  margin-bottom: 0;
  text-align: center;
}

.apple-button {
  width: 100%;
  height: 52px;
  border-radius: 12px;
  background-color: #0a84ff;
  border: none;
  color: white;
  font-size: 17px;
  font-weight: 500;
  transition: all 0.2s ease;
}

.apple-button:hover {
  background-color: #007aff;
  box-shadow: 0 4px 12px rgba(10, 132, 255, 0.4);
}

.apple-button:active {
  transform: scale(0.98);
}

/* 底部区域 */
.apple-footer {
  background-color: transparent;
  padding: 20px 0;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  margin-top: auto;
}

.footer-content {
  max-width: 1000px;
  margin: 0 auto;
  padding: 0 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: #86868b;
}

.footer-links {
  display: flex;
  align-items: center;
  gap: 8px;
}

.footer-links .el-link {
  font-size: 12px;
  color: #86868b;
}

.footer-links .el-link:hover {
  color: #f5f5f7;
}

.divider {
  color: rgba(255, 255, 255, 0.2);
}

@media (max-width: 768px) {
  .system-brand {
    position: static;
    justify-content: center;
    padding: 20px 0 0 0;
  }
  .main-content {
    padding-top: 20px;
  }
  .footer-content {
    flex-direction: column;
    gap: 12px;
    text-align: center;
  }
}
</style>
