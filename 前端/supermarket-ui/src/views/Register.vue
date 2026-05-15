<template>
  <div class="login-page">
    <!-- 轮播图背景 -->
    <div class="carousel-background">
      <div 
        v-for="(img, index) in bgImages" 
        :key="index"
        class="bg-image"
        :class="{ active: currentBgIndex === index }"
        :style="{ backgroundImage: `url(${img})` }"
      ></div>
    </div>

    <!-- 全屏浅色毛玻璃遮罩 -->
    <div class="glass-overlay"></div>

    <div class="content-layer">
      <div class="system-brand">
      <div class="logo-circle">🛒</div>
      <span class="system-name">连锁超市微服务管理系统</span>
    </div>

    <div class="main-content">
      <div class="login-container">
        <div class="card-header">
          <h2 class="login-title">创建收银员账号</h2>
        </div>
        
        <el-form class="login-form" :model="form" :rules="rules" ref="registerFormRef">
          <el-form-item prop="name">
            <div class="apple-input-group" :class="{ 'has-value': form.name }">
              <label class="apple-floating-label">姓名全拼 (如: lkq)</label>
              <el-input v-model="form.name" @input="generateUsername" />
            </div>
          </el-form-item>

          <el-form-item prop="storeId">
            <div class="apple-input-group" :class="{ 'has-value': form.storeId }">
              <label class="apple-floating-label">所在门店</label>
              <el-select v-model="form.storeId" placeholder=" " @change="generateUsername" style="width: 100%">
                <el-option label="1号店 (总店)" value="1" />
                <el-option label="2号店 (分店)" value="2" />
                <el-option label="3号店 (分店)" value="3" />
              </el-select>
            </div>
          </el-form-item>
          
          <el-form-item prop="password">
            <div class="apple-input-group" :class="{ 'has-value': form.password }">
              <label class="apple-floating-label">密码</label>
              <el-input v-model="form.password" type="password" show-password />
            </div>
          </el-form-item>

          <el-form-item prop="confirmPassword">
            <div class="apple-input-group" :class="{ 'has-value': form.confirmPassword }">
              <label class="apple-floating-label">确认密码</label>
              <el-input v-model="form.confirmPassword" type="password" show-password />
            </div>
          </el-form-item>

          <div class="link-container">
            <el-link type="primary" :underline="false" @click="router.push('/')">已有账号？返回登录 ↗</el-link>
          </div>

          <div class="account-preview" v-if="form.username">
            <div class="apple-alert">
              <div class="alert-title">您的登录账号为: <strong>{{ form.username }}</strong></div>
              <div class="alert-desc">请牢记此账号用于登录</div>
            </div>
          </div>
          
          <div class="info-paragraph">
            <div class="info-icon-wrapper">
              <el-icon><UserFilled /></el-icon>
            </div>
            <p>本超市管理系统基于 Spring Cloud 微服务与 Vue3 构建，集成了多门店库存隔离、智能扫码收银及 YOLOv8 图像视觉识别等核心模块，旨在为您提供高效、安全的零售管理体验。</p>
          </div>

          <el-form-item class="submit-item">
            <el-button class="apple-button" type="primary" :loading="loading" @click="handleRegister">
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
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { UserFilled, Platform, Search, Goods } from '@element-plus/icons-vue'
import request from '@/utils/request'

const router = useRouter()
const registerFormRef = ref(null)
const loading = ref(false)

// 轮播图逻辑
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

const form = reactive({
  name: '',
  storeId: '',
  password: '',
  confirmPassword: '',
  username: '' // 自动生成的账号
})

const validatePass2 = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请再次输入密码'))
  } else if (value !== form.password) {
    callback(new Error('两次输入密码不一致!'))
  } else {
    callback()
  }
}

const rules = reactive({
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

// 自动生成账号逻辑：姓名首字母缩写 + 所在店的编号 + 入职日期(YYYYMMDD)
const generateUsername = () => {
  if (form.name && form.storeId) {
    const today = new Date()
    const year = today.getFullYear()
    const month = String(today.getMonth() + 1).padStart(2, '0')
    const day = String(today.getDate()).padStart(2, '0')
    const dateStr = `${year}${month}${day}`
    
    // 强制将 storeId 补齐为2位，例如 1 -> 01
    const storeCode = String(form.storeId).padStart(2, '0')
    
    // 强制转为小写拼接
    form.username = `${form.name.toLowerCase()}${storeCode}${dateStr}`
  } else {
    form.username = ''
  }
}

const handleRegister = async () => {
  if (!registerFormRef.value) return
  
  await registerFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        // 调用后端注册接口
        const res = await request.post('/auth/register', {
          username: form.username,
          password: form.password,
          role: 'CASHIER', // 固定为收银员
          storeId: Number(form.storeId), // 这里直接传数字 1, 2, 3 给后端
          realName: form.name
        })
        
        // 假设后端返回成功 (适配后端的 Result 包装格式)
        // 1. axios 默认返回格式：res.data 是后端的响应体
        // 2. 如果后端响应体是 { code: 0, msg: "成功" }，那么它就在 res.data.code
        const responseData = res.data || res
        const isSuccess = responseData.code === 0 || responseData.code === 200
        
        if (isSuccess) { 
           ElMessage.success(`注册成功！请使用账号 ${form.username} 登录。`)
           setTimeout(() => {
             router.push('/')
           }, 1500)
        } else {
           // 这样当后端返回逻辑错误时，才会正确走入失败分支
           ElMessage.error(responseData.message || responseData.msg || '注册失败')
        }
      } catch (e) {
        console.error(e)
        // 实际开发中错误信息由拦截器或这里处理
        ElMessage.error(e.response?.data?.message || e.message || '注册失败，请检查网络或联系管理员')
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style scoped>
.login-page {
  position: relative;
  min-height: 100vh;
  overflow: hidden;
  background-color: #f5f5f7;
  font-family: -apple-system, BlinkMacSystemFont, "SF Pro SC", "SF Pro Text", "Helvetica Neue", Helvetica, Arial, sans-serif;
}

/* 轮播图背景 */
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
  transition: opacity 1.5s ease-in-out, transform 6s linear;
  transform: scale(1.05);
}
.bg-image.active {
  opacity: 1;
  transform: scale(1);
}

/* 全屏浅色毛玻璃遮罩 */
.glass-overlay {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(255, 255, 255, 0.55);
  backdrop-filter: saturate(180%) blur(25px);
  -webkit-backdrop-filter: saturate(180%) blur(25px);
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

/* 左上角系统 Logo (浅色模式适配) */
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
  background: rgba(0, 0, 0, 0.05);
  color: #1d1d1f;
  border: 1px solid rgba(0, 0, 0, 0.1);
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
  color: #1d1d1f;
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
  color: #1d1d1f;
  letter-spacing: -0.5px;
}

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
  color: #1d1d1f !important;
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
  color: #1d1d1f !important;
  -webkit-text-fill-color: #1d1d1f !important;
  line-height: normal !important;
  height: auto !important;
  padding: 0 !important;
}

:deep(.el-select__selected-item span) {
  color: #1d1d1f !important;
  -webkit-text-fill-color: #1d1d1f !important;
}

:deep(.el-select__placeholder.is-transparent) {
  color: transparent !important;
  -webkit-text-fill-color: transparent !important;
}

:deep(.el-input__suffix) {
  align-items: center;
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

/* 注册页面专属的账号提示框 (浅色适配) */
.apple-alert {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 24px;
  text-align: center;
}
.alert-title {
  font-size: 15px;
  color: #1d1d1f;
  margin-bottom: 4px;
}
.alert-desc {
  font-size: 12px;
  color: #86868b;
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
  color: #1d1d1f;
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
  border-top: 1px solid rgba(0, 0, 0, 0.1);
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
  color: #1d1d1f;
}

.divider {
  color: rgba(0, 0, 0, 0.2);
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
