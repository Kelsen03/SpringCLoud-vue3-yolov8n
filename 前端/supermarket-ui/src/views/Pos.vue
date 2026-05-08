<template>
  <div class="order-page">
    <!-- 阶段一：欢迎界面 -->
    <div v-if="!isStarted" class="welcome-box">
      <div class="welcome-card glass-effect">
        <div class="welcome-icon">👋</div>
        <h2>欢迎使用智能收银系统</h2>
        <p>请输入会员ID开始收银，散客请直接回车</p>
        
        <div class="input-area">
          <el-input 
            v-model="userId" 
            placeholder="会员ID (可选)" 
            size="large" 
            class="welcome-input"
            @keyup.enter="startCheckout"
          >
            <template #prefix>
              <el-icon><User /></el-icon>
            </template>
          </el-input>
          
          <el-button type="primary" size="large" class="start-btn" @click="startCheckout">
            开始收银
            <el-icon class="el-icon--right"><ArrowRight /></el-icon>
          </el-button>
        </div>
      </div>
    </div>

    <!-- 阶段三：结算成功 -->
    <div v-else-if="isFinished" class="result-box">
      <el-result icon="success" title="下单成功" sub-title="请核对订单信息">
        <template #extra>
          <div class="receipt-card">
            <div class="receipt-header">
              <h3>连锁超市购物小票</h3>
              <p>No. {{ orderInfo.id }}</p>
            </div>
            <div class="receipt-info">
              <div class="info-row">
                <span>会员ID：</span>
                <span>{{ orderInfo.userId || '散客' }}</span>
              </div>
              <div class="info-row" v-if="orderInfo.userId">
                <span>本次积分：</span>
                <span style="color: #e6a23c; font-weight: bold;">+{{ orderInfo.points }}</span>
              </div>
              <div class="info-row" v-if="orderInfo.userId">
                <span>当前积分：</span>
                <span>{{ orderInfo.totalPoints }}</span>
              </div>
            </div>
            <el-divider border-style="dashed" />
            <ul class="receipt-items">
              <li v-for="item in orderInfo.items" :key="item.id">
                <div class="item-name">{{ item.name }}</div>
                <div class="item-calc">
                  <span>{{ item.quantity }} x ￥{{ (item.usePromotion ? (item.promotionPrice || item.price) : item.price).toFixed(2) }}</span>
                  <span class="item-total">￥{{ ((item.usePromotion ? (item.promotionPrice || item.price) : item.price) * item.quantity).toFixed(2) }}</span>
                </div>
              </li>
            </ul>
            <el-divider border-style="dashed" />
            <div class="receipt-total">
              <span>实付金额</span>
              <span class="total-price">￥{{ orderInfo.totalAmount.toFixed(2) }}</span>
            </div>
          </div>
          
          <div class="action-buttons">
            <el-button type="primary" size="large" @click="reset">开始下一单</el-button>
            <el-button size="large" @click="printOrder" plain>打印小票</el-button>
          </div>
        </template>
      </el-result>
    </div>

    <!-- 阶段二：收银台主界面 -->
    <div v-else class="pos-container">
      <!-- 顶部状态栏 -->
      <div class="pos-header">
        <div class="member-info">
          <el-avatar :size="40" style="background: #409EFF">
            {{ userId ? '会员' : '散客' }}
          </el-avatar>
          <div class="info-text">
            <div class="user-id">{{ userId ? 'ID: ' + userId : '普通顾客' }}</div>
            <div class="points" v-if="memberPoints !== null">积分: {{ memberPoints }}</div>
          </div>
        </div>
        <el-button @click="exitCheckout" type="danger" plain size="small">退出收银</el-button>
      </div>

      <div class="pos-layout">
        <!-- 左侧：商品选择区 -->
        <div class="pos-left">
          <el-card shadow="never" class="product-search-card">
            <!-- 🤖 AI 智能识别区 -->
            <div style="text-align: center; margin-bottom: 20px; background: #f8f9fa; padding: 15px; border-radius: 8px;">
              <h3>AI 智能收银台 (YOLOv5)</h3>
              <video ref="videoRef" autoplay playsinline width="640" height="480" style="border: 2px solid #409EFF; border-radius: 8px; background: #000; max-width: 100%;"></video>
              <div style="margin-top: 15px;">
                <el-button type="success" size="large" @click="captureAndRecognize" :loading="isRecognizing" style="width: 200px; font-size: 16px;">
                  📸 拍照并 AI 识别
                </el-button>
              </div>
            </div>

            <div class="search-box">
              <el-select 
                v-model="currentProductId" 
                filterable 
                placeholder="🔍 扫描或搜索商品..." 
                size="large"
                style="width: 100%"
                popper-class="product-popper"
              >
                <el-option 
                  v-for="item in productList" 
                  :key="item.id" 
                  :label="item.name" 
                  :value="item.id" 
                  :disabled="!item.price || item.price <= 0"
                >
                  <div class="product-option">
                    <span class="opt-name">{{ item.name }}</span>
                    <span v-if="item.price > 0" class="opt-price">￥{{ item.price }}</span>
                    <el-tag v-else type="danger" size="small">未定价</el-tag>
                  </div>
                </el-option>
              </el-select>
              
              <div class="input-group">
                <el-input-number v-model="currentQty" :min="1" size="large" style="width: 120px" @keyup.enter="addToCart" />
                <el-button type="primary" size="large" @click="addToCart" :disabled="!currentProductId">
                  <el-icon><ShoppingCart /></el-icon> 加入
                </el-button>
              </div>
            </div>
            
            <!-- 快捷商品展示区 (可选) -->
            <div class="quick-products">
              <div class="section-title">热门商品</div>
              <div class="product-grid">
                <div 
                  v-for="item in productList.slice(0, 6)" 
                  :key="item.id" 
                  class="product-card"
                  @click="currentProductId = item.id"
                >
                  <div class="p-name">{{ item.name }}</div>
                  <div class="p-price">￥{{ item.price }}</div>
                </div>
              </div>
            </div>
          </el-card>
        </div>

        <!-- 右侧：购物车清单 -->
        <div class="pos-right">
          <div class="cart-panel">
            <div class="cart-header">
              <span>购物车清单</span>
              <el-tag type="info" round>{{ cart.length }} 件商品</el-tag>
            </div>
            
            <div class="cart-list">
              <el-empty v-if="cart.length === 0" description="暂无商品" :image-size="100"></el-empty>
              
              <div v-else class="cart-item" v-for="(item, index) in cart" :key="index">
                <div class="item-main">
                  <div class="item-title">{{ item.name }}</div>
                  <div class="item-tags">
                    <el-tag v-if="item.usePromotion" type="danger" size="small" effect="plain">促销</el-tag>
                  </div>
                </div>
                
                <div class="item-actions">
                  <div class="price-calc">
                    <div class="unit-price">
                      <el-radio-group v-if="item.promotionPrice && item.promotionPrice < item.price" v-model="item.usePromotion" size="small">
                        <el-radio-button :label="false">原￥{{ item.price }}</el-radio-button>
                        <el-radio-button :label="true">促￥{{ item.promotionPrice }}</el-radio-button>
                      </el-radio-group>
                      <span v-else>￥{{ item.price }}</span>
                    </div>
                    <div class="qty">x {{ item.quantity }}</div>
                  </div>
                  <div class="subtotal">￥{{ ((item.usePromotion ? (item.promotionPrice || item.price) : item.price) * item.quantity).toFixed(2) }}</div>
                  <el-button type="danger" icon="Delete" circle size="small" @click="removeFromCart(index)" plain></el-button>
                </div>
              </div>
            </div>

            <!-- 底部结算区 -->
            <div class="cart-footer">
              <div class="points-row" v-if="memberPoints !== null && canUsePoints">
                <el-checkbox v-model="usePoints" border class="points-check">
                  <span class="check-label">积分抵扣</span>
                  <span class="check-desc">-￥5.00 (消耗1000积分)</span>
                </el-checkbox>
              </div>
              
              <div class="total-row">
                <span class="label">应付金额</span>
                <span class="amount">￥{{ (usePoints ? totalAmount - 5 : totalAmount).toFixed(2) }}</span>
              </div>
              
              <el-button type="success" class="checkout-btn" @click="submitOrder" :disabled="cart.length === 0">
                立即结算
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { createOrder, getMemberPoints } from '@/api/order'
import { getProductList, aiRecognizeProduct } from '@/api/product'
import { getInventoryList } from '@/api/inventory'
import request from '@/utils/request'
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { ElMessage } from 'element-plus'
import { User, ArrowRight, ShoppingCart, Delete } from '@element-plus/icons-vue'

// 状态管理
const isStarted = ref(false)
const isFinished = ref(false)
const userId = ref('')
const memberPoints = ref(null) // 新增：存储查询到的会员积分
const productList = ref([])
const orderInfo = ref({})
const storeId = Number(localStorage.getItem('storeId')) || 1

// 购物车相关
const currentProductId = ref('')
const currentQty = ref(1)
const cart = ref([])

// --- AI 摄像头相关变量 ---
const videoRef = ref(null)
const isRecognizing = ref(false)

// 1. 开启本地摄像头
const startCamera = async () => {
  try {
    // 检查浏览器是否支持 mediaDevices
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      ElMessage.warning('您的浏览器不支持访问摄像头，或者当前不是 HTTPS 环境')
      return
    }
    
    // 获取所有媒体设备，查找是否有摄像头
    const devices = await navigator.mediaDevices.enumerateDevices()
    const videoDevices = devices.filter(device => device.kind === 'videoinput')
    
    if (videoDevices.length === 0) {
      ElMessage.error('未检测到任何摄像头设备，请检查硬件连接！')
      return
    }

    // 请求摄像头权限 (放宽限制，允许任何可用的摄像头)
    const stream = await navigator.mediaDevices.getUserMedia({ 
      video: true // 不强制指定后置，直接使用默认的（通常是电脑自带的）
    })
    
    if (videoRef.value) {
      videoRef.value.srcObject = stream
    }
  } catch (error) {
    console.error('摄像头错误:', error)
    if (error.name === 'NotAllowedError' || error.name === 'PermissionDeniedError') {
      ElMessage.error('您拒绝了摄像头权限，请在浏览器地址栏左侧重新授权！')
    } else if (error.name === 'NotFoundError' || error.name === 'DevicesNotFoundError') {
      ElMessage.error('未检测到摄像头设备，请检查硬件！')
    } else if (error.name === 'NotReadableError' || error.name === 'TrackStartError') {
      ElMessage.error('摄像头正被其他程序占用，请关闭其他使用摄像头的软件后重试！')
    } else {
      ElMessage.error('无法访问摄像头：' + error.message)
    }
  }
}

// 2. 拍照并发送给后端 AI 识别
const captureAndRecognize = async () => {
  if (!videoRef.value) return
  isRecognizing.value = true

  // 截取视频画面画到 canvas 上
  const canvas = document.createElement('canvas')
  canvas.width = videoRef.value.videoWidth
  canvas.height = videoRef.value.videoHeight
  const ctx = canvas.getContext('2d')
  ctx.drawImage(videoRef.value, 0, 0, canvas.width, canvas.height)

  // 转换成 base64
  const base64Image = canvas.toDataURL('image/jpeg', 0.8)

  try {
    const res = await aiRecognizeProduct(base64Image)
    
    // axios 返回的数据在 res.data 中，由于后端返回的是直接的数组，所以这里就是 res.data
    const detectedKeywords = res.data || []
    
    if (detectedKeywords.length > 0) {
      let count = 0;
      
      // 遍历 AI 识别出的关键词，去商品列表中模糊搜索
      detectedKeywords.forEach(keyword => {
        // 在前端的商品库中进行模糊匹配
        const matchedProduct = productList.value.find(p => p.name.includes(keyword))
        
        if (matchedProduct) { 
          // 检查是否已在购物车
          const existingItem = cart.value.find(c => c.id === matchedProduct.id)
          if (existingItem) {
            existingItem.quantity = Number(existingItem.quantity) + 1
          } else {
            cart.value.push({
              id: matchedProduct.id,
              name: matchedProduct.name,
              price: matchedProduct.price,
              promotionPrice: matchedProduct.promotionPrice || matchedProduct.promoPrice,
              usePromotion: false,
              quantity: 1
            })
          }
          count++
        }
      })
      
      if(count > 0){
        ElMessage.success(`🎉 AI 识别到关键字，成功为您匹配并加入了 ${count} 件商品！`)
      } else {
        ElMessage.warning(`AI 识别到了【${detectedKeywords.join(',')}】，但您的商品库里没有卖这些商品`)
      }
    } else {
      ElMessage.warning('未能识别出商品，请调整位置后重试')
    }
  } catch (error) {
    console.error('AI服务请求错误详情:', error)
    if (error.response) {
      // 服务器返回了错误状态码
      ElMessage.error(`AI 服务返回错误: ${error.response.status}`)
    } else if (error.request) {
      // 请求发出去了，但没收到响应 (通常是跨域、端口没开、服务没启)
      ElMessage.error('无法连接到 AI 服务，请检查服务器 5000 端口是否开放，以及 Python 服务是否运行')
    } else {
      ElMessage.error('请求 AI 服务失败: ' + error.message)
    }
  } finally {
    isRecognizing.value = false
  }
}

// 初始化加载商品库（模拟扫码枪数据库）
onMounted(async () => {
  // startCamera() // 将启动摄像头移到进入收银台之后
  try {
    const res = await getProductList()
    // 关键修复：确保即使返回的是对象，也能正确提取商品数组
    let products = res.data || []
    if (!Array.isArray(products) && res.data.list) {
      products = res.data.list
    }
    
    productList.value = products
  } catch (e) {
    console.error('加载商品库失败', e)
    ElMessage.error('加载商品数据失败，请检查网络或刷新页面')
  }
})

// 进入收银模式
const startCheckout = async () => {
  if (userId.value) {
    try {
      // 不再发送0元订单，而是直接获取积分（或者直接假设用户有积分，为了不报错我们做个兼容）
      // 如果后端还没有 getMemberPoints 接口，这里会走到 catch 块，至少不会生成假订单
      const res = await getMemberPoints(Number(userId.value))
      memberPoints.value = res.data !== undefined ? res.data : 0
    } catch (e) {
      console.error('获取积分失败或接口未实现', e)
      // 如果接口没实现，给个默认值不影响收银流程
      memberPoints.value = 0 
    }
  } else {
    memberPoints.value = null
  }
  isStarted.value = true
  
  // 延迟一小段时间，确保 videoRef 元素已经渲染出来
  setTimeout(() => {
    startCamera()
  }, 500)
}

// 退出收银模式
const exitCheckout = () => {
  isStarted.value = false
  if (videoRef.value && videoRef.value.srcObject) {
    videoRef.value.srcObject.getTracks().forEach(track => track.stop())
    videoRef.value.srcObject = null
  }
}

// 添加到购物车
const addToCart = () => {
  if (!currentProductId.value) {
    ElMessage.warning('请选择商品')
    return
  }
  if (currentQty.value <= 0) {
    ElMessage.warning('数量必须大于0')
    return
  }

  // 查找商品信息
  const product = productList.value.find(p => p.id === currentProductId.value)
  if (!product) return

  // 检查是否已在购物车
  const existingItem = cart.value.find(item => item.id === product.id)
  if (existingItem) {
    existingItem.quantity = Number(existingItem.quantity) + Number(currentQty.value)
  } else {
    cart.value.push({
      id: product.id,
      name: product.name,
      price: product.price, 
      promotionPrice: product.promotionPrice || product.promoPrice, // 兼容字段
      usePromotion: false, // 默认不使用促销价（使用原价）
      quantity: Number(currentQty.value)
    })
  }
  
  // 重置输入
  currentProductId.value = ''
  currentQty.value = 1
}

// 移除商品
const removeFromCart = (index) => {
  cart.value.splice(index, 1)
}

// 计算总价
const totalAmount = computed(() => {
  return cart.value.reduce((sum, item) => sum + (item.usePromotion ? (item.promotionPrice || item.price) : item.price) * item.quantity, 0)
})

// 积分抵扣相关
const usePoints = ref(false)
const canUsePoints = computed(() => {
  // 条件：有会员积分 + 积分>=1000 + 订单金额>5
  // 注意：memberPoints.value 可能是字符串，需要转数字比较
  const points = Number(memberPoints.value || 0)
  return memberPoints.value !== null && points >= 1000 && totalAmount.value > 5
})

// 提交订单
const submitOrder = async () => {
  if (cart.value.length === 0) {
    ElMessage.warning('购物车是空的')
    return
  }

  try {
    const payload = {
      items: cart.value.map(item => ({
        productId: Number(item.id),
        quantity: Number(item.quantity),
        // [安全警告] 前端传递价格仅作为参考，后端必须忽略此字段并从数据库重新查询当前价格！
        // 防止恶意用户通过抓包工具篡改价格
        price: Number(item.usePromotion ? (item.promotionPrice || item.price) : item.price) 
      })),
      cashierAccount: localStorage.getItem('username') // 加入收银员账号字段
    }
    
    // 仅当输入了有效的会员ID时才传递 memberId，并确保转为数字
    if (userId.value && !isNaN(userId.value) && Number(userId.value) > 0) {
      payload.memberId = Number(userId.value)
    }

    // 积分抵扣逻辑
    if (usePoints.value && canUsePoints.value) {
      payload.usePoints = true // 告诉后端使用了积分
      // 注意：这里前端只是标记，具体扣积分和减金额逻辑应由后端处理
      // 但为了前端显示正确，我们这里也做一下临时计算
    }

    const res = await createOrder(payload)
    
    // 记录订单信息
    const total = usePoints.value ? totalAmount.value - 5 : totalAmount.value
    orderInfo.value = {
      id: res.data?.orderId || 'ORD-' + Date.now(), 
      userId: userId.value,
      items: [...cart.value],
      totalAmount: total,
      // 使用后端返回的积分数据
      points: res.data?.points || 0, 
      totalPoints: res.data?.totalPoints || 0
    }
    
    ElMessage.success('下单成功！')
    isFinished.value = true // 进入结果页
  } catch (e) {
    // 错误已由拦截器处理
  }
}

// 重置并开始下一单
const reset = () => {
  cart.value = []
  userId.value = ''
  orderInfo.value = {}
  isStarted.value = false
  isFinished.value = false
}

// 打印小票（模拟）
const printOrder = () => {
  ElMessage.success('正在发送到打印机...')
}

onBeforeUnmount(() => {
  if (videoRef.value && videoRef.value.srcObject) {
    videoRef.value.srcObject.getTracks().forEach(track => track.stop())
  }
})
</script>

<style scoped>
.order-page {
  /* padding: 20px; */
  height: 100%;
}

/* 欢迎页样式 */
.welcome-box {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 80vh;
}

.welcome-card {
  width: 500px;
  padding: 60px;
  text-align: center;
  background: white;
  border-radius: 16px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.05);
}

.welcome-icon {
  font-size: 60px;
  margin-bottom: 20px;
}

.welcome-card h2 {
  color: #303133;
  margin-bottom: 10px;
}

.welcome-card p {
  color: #909399;
  margin-bottom: 40px;
}

.input-area {
  display: flex;
  gap: 10px;
}

/* 收银台主界面 */
.pos-container {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 100px); /* 减去顶部导航和padding */
  gap: 20px;
}

.pos-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
  padding: 15px 20px;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.03);
}

.member-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.info-text .user-id {
  font-weight: bold;
  font-size: 16px;
}

.info-text .points {
  font-size: 12px;
  color: #e6a23c;
}

.pos-layout {
  display: flex;
  gap: 20px;
  flex: 1;
  overflow: hidden;
}

.pos-left {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.product-search-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.search-box {
  display: flex;
  gap: 15px;
  margin-bottom: 30px;
}

.input-group {
  display: flex;
  gap: 10px;
}

.section-title {
  font-size: 14px;
  color: #909399;
  margin-bottom: 15px;
  font-weight: bold;
}

.product-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 15px;
}

.product-card {
  background: #f5f7fa;
  padding: 15px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid transparent;
}

.product-card:hover {
  background: #ecf5ff;
  border-color: #409eff;
  transform: translateY(-2px);
}

.p-name {
  font-weight: bold;
  margin-bottom: 5px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.p-price {
  color: #f56c6c;
}

.pos-right {
  width: 400px;
  display: flex;
  flex-direction: column;
}

.cart-panel {
  background: white;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  height: 100%;
  box-shadow: 0 4px 16px rgba(0,0,0,0.05);
}

.cart-header {
  padding: 20px;
  border-bottom: 1px solid #ebeef5;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
  font-size: 16px;
}

.cart-list {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
}

.cart-item {
  background: #fcfcfc;
  border: 1px solid #ebeef5;
  border-radius: 6px;
  padding: 12px;
  margin-bottom: 10px;
}

.item-main {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.item-title {
  font-weight: 500;
}

.item-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.price-calc {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 12px;
  color: #909399;
}

.subtotal {
  font-weight: bold;
  color: #f56c6c;
  font-size: 16px;
}

.cart-footer {
  padding: 20px;
  background: #fff;
  border-top: 1px solid #ebeef5;
}

.points-row {
  margin-bottom: 15px;
  padding: 10px;
  background: #fdf6ec;
  border-radius: 4px;
}

.check-label {
  font-weight: bold;
  color: #e6a23c;
}

.check-desc {
  font-size: 12px;
  color: #909399;
  margin-left: 5px;
}

.total-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.total-row .label {
  font-size: 16px;
  color: #606266;
}

.total-row .amount {
  font-size: 28px;
  font-weight: bold;
  color: #f56c6c;
}

.checkout-btn {
  width: 100%;
  height: 50px;
  font-size: 18px;
  font-weight: bold;
  border-radius: 25px;
}

/* 下拉框自定义样式 */
.product-option {
  display: flex;
  justify-content: space-between;
  width: 100%;
}
.opt-price {
  color: #f56c6c;
}

/* 结算成功页 */
.result-box {
  display: flex;
  justify-content: center;
  padding-top: 50px;
}

.receipt-card {
  width: 400px;
  background: #fff;
  padding: 30px;
  border: 1px solid #ebeef5;
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
  margin-bottom: 30px;
}

.receipt-header {
  text-align: center;
  margin-bottom: 20px;
}

.receipt-info {
  font-size: 14px;
  color: #606266;
  margin-bottom: 20px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 5px;
}

.receipt-items {
  list-style: none;
  padding: 0;
  margin: 20px 0;
}

.receipt-items li {
  margin-bottom: 10px;
}

.item-name {
  font-weight: 500;
  margin-bottom: 2px;
}

.item-calc {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  color: #909399;
}

.item-total {
  color: #303133;
}

.receipt-total {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 20px;
  font-size: 18px;
  font-weight: bold;
}

.action-buttons {
  text-align: center;
}

@media (max-width: 768px) {
  /* 欢迎页适配 */
  .welcome-card {
    width: 90%;
    padding: 40px 20px;
  }
  
  .input-area {
    flex-direction: column;
  }
  
  .start-btn {
    width: 100%;
  }

  /* 收银台布局适配 */
  .pos-container {
    height: auto;
    overflow-y: visible;
  }
  
  .pos-layout {
    flex-direction: column;
    overflow: visible;
  }
  
  .pos-left {
    flex: none;
    width: 100%;
  }
  
  .pos-right {
    flex: none;
    width: 100%;
  }
  
  .cart-panel {
    height: 500px; /* 移动端给个固定高度，或者自适应 */
  }
  
  /* 结算结果页适配 */
  .receipt-card {
    width: 100%;
    box-sizing: border-box;
  }
}
</style>