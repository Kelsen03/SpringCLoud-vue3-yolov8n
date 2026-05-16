<template>
  <div class="order-page">
    <!-- ========= 阶段0：未开班 ========= -->
    <div v-if="!isShiftOpen" class="shift-box">
      <div class="shift-card">
        <div class="shift-icon"></div>
        <h2>收银员交班系统</h2>
        <p>开始收银前请先开班，输入找零备用金</p>
        <div class="shift-input">
          <span class="prefix">¥</span>
          <input v-model="openingCash" type="number" step="0.01" min="0" placeholder="备用金金额" @keyup.enter="doOpenShift" />
        </div>
        <el-button type="primary" size="large" @click="doOpenShift" :loading="shiftLoading" class="shift-btn">
          开班上岗
        </el-button>
        <p class="hint">备用金 = 收银机里预先放好的零钱，用于给顾客找零</p>
      </div>
    </div>

    <!-- ========= 阶段1：欢迎界面（已开班，未开始收银） ========= -->
    <div v-else-if="!isStarted" class="welcome-box">
      <div class="welcome-card">
        <div class="shift-bar">
          <el-tag type="success" size="large"> 当班中</el-tag>
          <span>备用金 ¥{{ shiftOpeningCash }}</span>
          <el-button type="warning" size="small" plain @click="showCloseDialog = true">交班</el-button>
        </div>
        <div class="welcome-icon"></div>
        <h2>欢迎使用智能收银系统</h2>
        <p>请输入会员ID开始收银，散客请直接回车</p>
        <div class="input-area">
          <el-input v-model="userId" placeholder="会员ID (可选)" size="large" class="welcome-input" @keyup.enter="startCheckout">
            <template #prefix><el-icon><User /></el-icon></template>
          </el-input>
          <el-button type="primary" size="large" class="start-btn" @click="startCheckout">
            开始收银 <el-icon class="el-icon--right"><ArrowRight /></el-icon>
          </el-button>
        </div>
      </div>
    </div>

    <!-- ========= 阶段3：结算成功 ========= -->
    <div v-else-if="isFinished" class="result-box">
      <el-result icon="success" title="下单成功" sub-title="请核对订单信息">
        <template #extra>
          <div class="receipt-card">
            <div class="receipt-header"><h3>连锁超市购物小票</h3><p>No. {{ orderInfo.id }}</p></div>
            <div class="receipt-info">
              <div class="info-row" v-if="orderInfo.storeName"><span>门店：</span><span>{{ orderInfo.storeName }}</span></div>
              <div class="info-row"><span>会员ID：</span><span>{{ orderInfo.userId || '散客' }}</span></div>
              <div class="info-row" v-if="orderInfo.userId">
                <span>本次积分：</span><span style="color:#e6a23c;font-weight:bold">+{{ orderInfo.points }}</span>
              </div>
            </div>
            <el-divider border-style="dashed" />
            <ul class="receipt-items">
              <li v-for="item in orderInfo.items" :key="item.id">
                <div class="item-name">{{ item.name }}</div>
                <div class="item-calc">
                  <span>{{ item.quantity }} x ¥{{ (item.usePromotion ? (item.promotionPrice||item.price) : item.price).toFixed(2) }}</span>
                  <span class="item-total">¥{{ ((item.usePromotion ? (item.promotionPrice||item.price) : item.price) * item.quantity).toFixed(2) }}</span>
                </div>
              </li>
            </ul>
            <el-divider border-style="dashed" />
            <div class="receipt-total"><span>实付金额</span><span class="total-price">¥{{ orderInfo.totalAmount.toFixed(2) }}</span></div>
          </div>
          <div class="action-buttons">
            <el-button type="primary" size="large" @click="reset">开始下一单</el-button>
          </div>
        </template>
      </el-result>
    </div>

    <!-- ========= 阶段2：收银台主界面 ========= -->
    <div v-else class="pos-container">
      <div class="pos-header">
        <div class="member-info">
          <el-avatar :size="40" style="background:#409EFF;font-size:16px;flex-shrink:0">{{ userId ? '会员' : '散客' }}</el-avatar>
          <span class="user-id">{{ userId ? 'ID:' + userId : '普通顾客' }}</span>
          <span class="points" v-if="memberPoints !== null">积分 {{ memberPoints }}</span>
        </div>
        <div class="header-actions">
          <el-tag type="success">¥{{ shiftOpeningCash }}</el-tag>
          <el-button @click="showCloseDialog = true" type="warning" plain>交班</el-button>
          <el-button @click="exitCheckout" type="danger" plain>退出</el-button>
        </div>
      </div>

      <div class="pos-layout">
        <!-- 左侧：摄像头 + 商品选择 -->
        <div class="pos-left">
          <!-- AI 摄像头 -->
          <div class="ai-section">
            <video ref="videoRef" autoplay playsinline class="ai-video"></video>
            <el-button type="success" @click="captureAndRecognize" :loading="isRecognizing" size="large" style="font-size:20px;padding:14px 48px;margin-top:8px">拍照识别</el-button>
          </div>

          <el-card shadow="never" class="product-search-card">
            <!-- 条形码输入 -->
            <div class="barcode-box">
              <el-input v-model="barcodeInput" placeholder="条形码（扫码枪自动填写，或手动输入按回车）" size="large" @keyup.enter="onBarcodeEnter" @change="onBarcodeEnter" clearable>
                <template #prefix>📷</template>
              </el-input>
            </div>
            <!-- 搜索区 -->
            <div class="search-box">
              <el-select v-model="currentProductId" filterable placeholder="扫码或搜索商品..." size="large" style="flex:1" popper-class="product-popper">
                <el-option v-for="item in productList" :key="item.id" :label="item.name" :value="item.id" :disabled="!item.price||item.price<=0">
                  <div class="product-option">
                    <span class="opt-name">{{ item.name }}</span>
                    <span v-if="item.price>0" class="opt-price">¥{{ item.price }}</span>
                    <el-tag v-else type="danger">未定价</el-tag>
                  </div>
                </el-option>
              </el-select>
              <el-input-number v-model="currentQty" :min="1" size="large" style="width:100px" @keyup.enter="addToCart" />
              <el-button type="primary" size="large" @click="addToCart" :disabled="!currentProductId" style="font-size:16px;padding:12px 28px"><el-icon><ShoppingCart /></el-icon> 加入</el-button>
            </div>

            <!-- 热门商品（按品类取首条，统一高度） -->
            <div class="quick-products">
              <div class="section-title">热门商品</div>
              <div class="product-strip">
                <div v-for="item in hotProducts" :key="item.id" class="hot-card" @click="quickAdd(item)">
                  <div class="hot-name">{{ item.name }}</div>
                  <el-tag type="info">{{ item.category }}</el-tag>
                  <div class="hot-price">¥{{ item.price.toFixed(2) }}</div>
                </div>
              </div>
            </div>
          </el-card>
        </div>

        <!-- 右侧：购物车 -->
        <div class="pos-right">
          <div class="cart-panel">
            <div class="cart-header"><span>购物车</span><el-tag type="info" round>{{ cart.length }} 件</el-tag></div>
            <div class="cart-list">
              <el-empty v-if="cart.length===0" description="暂无商品" :image-size="80"></el-empty>
              <div v-else class="cart-item" v-for="(item, index) in cart" :key="index">
                <div class="item-main">
                  <div class="item-title">{{ item.name }}</div>
                  <el-tag v-if="item.usePromotion" type="danger" effect="plain">促销</el-tag>
                </div>
                <div class="item-actions">
                  <div class="price-calc">
                    <div class="unit-price">
                      <el-radio-group v-if="item.promotionPrice && item.promotionPrice<item.price" v-model="item.usePromotion" size="small">
                        <el-radio-button :label="false">原¥{{ item.price }}</el-radio-button>
                        <el-radio-button :label="true">促¥{{ item.promotionPrice }}</el-radio-button>
                      </el-radio-group>
                      <span v-else>¥{{ item.price }}</span>
                    </div>
                    <div class="qty">x {{ item.quantity }}</div>
                  </div>
                  <div class="subtotal">¥{{ ((item.usePromotion ? (item.promotionPrice||item.price) : item.price) * item.quantity).toFixed(2) }}</div>
                  <el-button type="danger" icon="Delete" circle size="small" @click="removeFromCart(index)" plain></el-button>
                </div>
              </div>
            </div>
            <div class="cart-footer">
              <div class="points-row" v-if="memberPoints!==null && canUsePoints">
                <el-checkbox v-model="usePoints" border class="points-check">
                  <span class="check-label">积分抵扣</span><span class="check-desc">-¥5.00 (消耗1000积分)</span>
                </el-checkbox>
              </div>
              <div class="total-row">
                <span class="label">应付金额</span>
                <span class="amount">¥{{ (usePoints ? totalAmount-5 : totalAmount).toFixed(2) }}</span>
              </div>
              <el-button type="success" class="checkout-btn" @click="submitOrder" :disabled="cart.length===0">立即结算</el-button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ========= 交班对账弹窗 ========= -->
    <el-dialog v-model="showCloseDialog" title="交班对账" width="450px" :close-on-click-modal="false">
      <div class="close-content" v-if="closeResult">
        <el-result icon="success" title="交班完成" sub-title="请核对以下对账信息" />
        <table class="close-table">
          <tr><td>开班备用金</td><td>¥{{ closeResult.openingCash }}</td></tr>
          <tr><td>系统现金收入</td><td>¥{{ closeResult.systemCash }}</td></tr>
          <tr><td>系统在线支付</td><td>¥{{ closeResult.systemOnline }}</td></tr>
          <tr><td>总订单数</td><td>{{ closeResult.totalOrders }} 笔</td></tr>
          <tr class="highlight"><td>理论应有现金</td><td>¥{{ closeResult.theoryCash }}</td></tr>
          <tr class="highlight"><td>实际清点现金</td><td>¥{{ closeResult.closingCash }}</td></tr>
          <tr :class="Math.abs(closeResult.diff)>0.01 ? 'diff-red':'diff-ok'">
            <td>差异</td><td>¥{{ closeResult.diff }}</td>
          </tr>
        </table>
        <el-button type="primary" @click="finishShift" style="width:100%;margin-top:20px">确认退出登录</el-button>
      </div>
      <div v-else>
        <p style="text-align:center;color:#606266;margin-bottom:20px">请清点收银机中的现金，输入实际金额</p>
        <div class="shift-input"><span class="prefix">¥</span>
          <input v-model="closingCash" type="number" step="0.01" min="0" placeholder="实际现金" @keyup.enter="doCloseShift" />
        </div>
        <el-button type="primary" @click="doCloseShift" :loading="shiftLoading" style="width:100%;margin-top:15px">确认交班</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { createOrder, getMemberPoints, openShift, closeShift, getCurrentShift } from '@/api/order'
import { getProductList, getHotProducts, getProductByBarcode, aiRecognizeProduct } from '@/api/product'
import request from '@/utils/request'
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { User, ArrowRight, ShoppingCart } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// ===== 换班状态 =====
const isShiftOpen = ref(false)
const shiftOpeningCash = ref('0')
const showCloseDialog = ref(false)
const shiftLoading = ref(false)
const openingCash = ref('500')
const closingCash = ref('')
const closeResult = ref(null)

// ===== 收银状态 =====
const isStarted = ref(false)
const isFinished = ref(false)
const userId = ref('')
const memberPoints = ref(null)
const productList = ref([])
const orderInfo = ref({})
const storeId = Number(localStorage.getItem('storeId')) || 1
const currentProductId = ref('')
const currentQty = ref(1)
const cart = ref([])
const videoRef = ref(null)
const isRecognizing = ref(false)

// ===== 热门商品（API 按销量取 TOP10） =====
const hotProducts = ref([])

const fetchHotProducts = async () => {
  try {
    const res = await getHotProducts()
    hotProducts.value = (res.data || []).map(p => ({
      id: p.id, name: p.name, category: p.category,
      price: p.price, promotionPrice: p.promotionPrice || p.promo_price
    }))
    if (hotProducts.value.length === 0) {
      // 无销量时降级为首批有价格的商品
      hotProducts.value = productList.value.filter(p => p.price > 0).slice(0, 10)
    }
  } catch (_) {
    hotProducts.value = productList.value.filter(p => p.price > 0).slice(0, 10)
  }
}

// ===== 开班 =====
const doOpenShift = async () => {
  const val = parseFloat(openingCash.value)
  if (!val || val < 0) { ElMessage.warning('请输入有效的备用金金额'); return }
  shiftLoading.value = true
  try {
    const res = await openShift(val)
    if (res.data.ok) {
      isShiftOpen.value = true
      shiftOpeningCash.value = val.toFixed(2)
      ElMessage.success(res.data.msg)
    } else {
      ElMessage.error(res.data.msg)
    }
  } catch (e) {
    ElMessage.error('开班失败，请检查服务')
  }
  shiftLoading.value = false
}

// ===== 交班 =====
const doCloseShift = async () => {
  const val = parseFloat(closingCash.value)
  if (!val || val < 0) { ElMessage.warning('请输入实际现金金额'); return }
  shiftLoading.value = true
  try {
    const res = await closeShift(val)
    if (res.data.ok) {
      closeResult.value = res.data
    } else {
      ElMessage.error(res.data.msg)
    }
  } catch (e) {
    ElMessage.error('交班失败')
  }
  shiftLoading.value = false
}

const finishShift = () => {
  showCloseDialog.value = false
  closeResult.value = null
  closingCash.value = ''
  localStorage.removeItem('token')
  localStorage.removeItem('role')
  localStorage.removeItem('storeId')
  localStorage.removeItem('username')
  router.push('/')
}

// ===== 快捷加购物车 =====
const quickAdd = (item) => {
  const exist = cart.value.find(c => c.id === item.id)
  if (exist) { exist.quantity++ } else {
    cart.value.push({ id: item.id, name: item.name, price: item.price, promotionPrice: item.promotionPrice||item.promoPrice, usePromotion: false, quantity: 1 })
  }
}

// ===== 相机 + AI =====
const startCamera = async () => {
  try {
    if (!navigator.mediaDevices?.getUserMedia) { ElMessage.warning('浏览器不支持摄像头'); return }
    const stream = await navigator.mediaDevices.getUserMedia({ video: true })
    if (videoRef.value) videoRef.value.srcObject = stream
  } catch (e) {
    ElMessage.error('无法访问摄像头: ' + (e.message||'权限被拒'))
  }
}

const captureAndRecognize = async () => {
  if (!videoRef.value) return
  isRecognizing.value = true
  const canvas = document.createElement('canvas')
  canvas.width = videoRef.value.videoWidth; canvas.height = videoRef.value.videoHeight
  canvas.getContext('2d').drawImage(videoRef.value, 0, 0)
  const base64 = canvas.toDataURL('image/jpeg', 0.8)
  try {
    const res = await aiRecognizeProduct(base64)
    const keys = res.data || []
    let hit = 0
    keys.forEach(k => {
      const m = productList.value.find(p => p.name.includes(k))
      if (m) {
        const e = cart.value.find(c => c.id === m.id)
        e ? e.quantity++ : cart.value.push({ id: m.id, name: m.name, price: m.price, promotionPrice: m.promotionPrice||m.promoPrice, usePromotion: false, quantity: 1 })
        hit++
      }
    })
    if (hit > 0) {
      ElMessage.success(`🎉 AI 识别并加入 ${hit} 件商品`)
    } else if (keys.length > 0) {
      ElMessage.warning(`AI 检测到: ${keys.join('、')}，商品库中无匹配\n💡 请将饮料瓶对准摄像头`)
    } else {
      ElMessage.info('未检测到物体，请确保光线充足、瓶子在画面中央')
    }
  } catch (e) {
    ElMessage.error('AI 服务连接失败，请检查 5000 端口')
  }
  isRecognizing.value = false
}

const scanBuffer = ref('')
const barcodeInput = ref('')
let scanTimer = null

/** 条形码输入框回车处理 */
const onBarcodeEnter = async () => {
  const code = barcodeInput.value.trim()
  if (!code || code.length < 8) return
  try {
    const res = await getProductByBarcode(code)
    if (res.data?.id) {
      const p = res.data
      const exist = cart.value.find(c => c.id === p.id)
      exist ? exist.quantity++ : cart.value.push({ id: p.id, name: p.name, price: p.price, promotionPrice: p.promoPrice, usePromotion: false, quantity: 1 })
      ElMessage.success(`条形码: ${p.name} ¥${p.price}`)
      barcodeInput.value = ''
    } else {
      ElMessage.warning(`条形码 ${code} 未匹配到商品`)
    }
  } catch (_) {}
}

/** 扫码枪输入处理：快速输入13位数字+回车 → 条形码查商品 */
const handleBarcodeScan = (e) => {
  if (!isShiftOpen.value || !isStarted.value) return
  // 仅拦截数字键
  if (e.key >= '0' && e.key <= '9') {
    scanBuffer.value += e.key
    clearTimeout(scanTimer)
    scanTimer = setTimeout(() => { scanBuffer.value = '' }, 3000)
  } else if (e.key === 'Enter' && scanBuffer.value.length >= 8) {
    e.preventDefault()
    const code = scanBuffer.value
    scanBuffer.value = ''
    clearTimeout(scanTimer)
    getProductByBarcode(code).then(res => {
      if (res.data?.id) {
        const p = res.data
        const exist = cart.value.find(c => c.id === p.id)
        exist ? exist.quantity++ : cart.value.push({ id: p.id, name: p.name, price: p.price, promotionPrice: p.promoPrice, usePromotion: false, quantity: 1 })
        ElMessage.success(`扫码: ${p.name} ¥${p.price}`)
      } else {
        ElMessage.warning(`条形码 ${code} 未找到商品`)
      }
    }).catch(() => {})
  }
}

onMounted(async () => {
  window.addEventListener('keydown', handleBarcodeScan)

  try {
    const r = await getCurrentShift()
    if (r.data?.hasShift) {
      isShiftOpen.value = true
      shiftOpeningCash.value = String(r.data.openingCash||0)
    }
  } catch (_) {}

  try {
    const res = await getProductList()
    productList.value = Array.isArray(res.data) ? res.data : (res.data?.list||[])
  } catch (e) {
    ElMessage.error('加载商品失败')
  }

  fetchHotProducts()
})

const startCheckout = async () => {
  if (userId.value) {
    try {
      const r = await getMemberPoints(Number(userId.value))
      memberPoints.value = r.data ?? 0
    } catch (_) { memberPoints.value = 0 }
  } else { memberPoints.value = null }
  isStarted.value = true
  setTimeout(() => startCamera(), 500)
}

const exitCheckout = () => {
  isStarted.value = false
  if (videoRef.value?.srcObject) {
    videoRef.value.srcObject.getTracks().forEach(t => t.stop())
    videoRef.value.srcObject = null
  }
}

const addToCart = () => {
  if (!currentProductId.value) { ElMessage.warning('请选择商品'); return }
  const p = productList.value.find(x => x.id === currentProductId.value)
  if (!p) return
  const e = cart.value.find(x => x.id === p.id)
  e ? e.quantity += Number(currentQty.value) : cart.value.push({ id: p.id, name: p.name, price: p.price, promotionPrice: p.promotionPrice||p.promoPrice, usePromotion: false, quantity: Number(currentQty.value) })
  currentProductId.value = ''; currentQty.value = 1
}

const removeFromCart = (i) => cart.value.splice(i, 1)
const totalAmount = computed(() => cart.value.reduce((s, x) => s + (x.usePromotion ? (x.promotionPrice||x.price) : x.price) * x.quantity, 0))
const usePoints = ref(false)
const canUsePoints = computed(() => memberPoints.value !== null && Number(memberPoints.value||0) >= 1000 && totalAmount.value > 5)

const submitOrder = async () => {
  if (cart.value.length === 0) { ElMessage.warning('购物车是空的'); return }
  try {
    const payload = {
      items: cart.value.map(x => ({ productId: Number(x.id), quantity: Number(x.quantity), price: Number(x.usePromotion ? (x.promotionPrice||x.price) : x.price) })),
      cashierAccount: localStorage.getItem('username')
    }
    if (userId.value && Number(userId.value) > 0) payload.memberId = Number(userId.value)
    if (usePoints.value && canUsePoints.value) payload.usePoints = true
    const res = await createOrder(payload)
    const t = usePoints.value ? totalAmount.value - 5 : totalAmount.value
    orderInfo.value = { id: res.data?.orderId||'ORD-'+Date.now(), userId: userId.value, items: [...cart.value], totalAmount: t, points: res.data?.points||0, totalPoints: res.data?.totalPoints||0, storeName: res.data?.storeName||'' }
    isFinished.value = true
  } catch (_) {}
}

const reset = () => { cart.value = []; userId.value = ''; orderInfo.value = {}; isStarted.value = false; isFinished.value = false }

onBeforeUnmount(() => {
  window.removeEventListener('keydown', handleBarcodeScan)
  if (videoRef.value?.srcObject) videoRef.value.srcObject.getTracks().forEach(t => t.stop())
})
</script>

<style scoped>
.order-page { height:100% }

/* 开班页 */
.shift-box { display:flex;justify-content:center;align-items:center;height:80vh }
.shift-card { text-align:center;background:#fff;padding:50px 60px;border-radius:16px;box-shadow:0 8px 30px rgba(0,0,0,.06);max-width:450px;width:100% }
.shift-icon { font-size:56px;margin-bottom:16px }
.shift-card h2 { color:#303133;margin-bottom:8px }
.shift-card p { color:#909399;margin-bottom:24px }
.shift-input { display:flex;align-items:center;background:#f5f7fa;border:1px solid #dcdfe6;border-radius:8px;padding:12px 16px;margin-bottom:16px }
.shift-input .prefix { font-size:22px;color:#67c23a;font-weight:bold;margin-right:8px }
.shift-input input { flex:1;border:none;outline:none;background:transparent;font-size:28px;color:#303133;width:100% }
.shift-btn { width:100%;height:48px;font-size:17px;font-weight:600;border-radius:8px }
.hint { font-size:12px;color:#c0c4cc;margin-top:12px }

/* 欢迎页班次条 */
.shift-bar { display:flex;align-items:center;gap:12px;background:#f0f9eb;padding:10px 16px;border-radius:8px;margin-bottom:24px }

/* 收银台 */
.pos-container { display:flex;flex-direction:column;height:calc(100vh - 60px);gap:8px;padding:0 }
.pos-layout { display:flex;gap:10px;flex:1;overflow:hidden; }
.pos-left { flex:1;display:flex;flex-direction:column;min-width:0 }
.product-search-card { height:100%;display:flex;flex-direction:column }
:deep(.product-search-card .el-card__body) { padding:6px 8px }
/* AI 摄像头区域 */
.ai-section { text-align:center;padding:2px 0;margin-bottom:6px }
.ai-video { width:100%;max-width:560px;border:3px solid #333;border-radius:8px;background:#1a1a1a;display:block;margin:0 auto }
.pos-header { display:flex;align-items:center;background:#fff;padding:10px 0;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,.04);gap:10px;width:100% }
.pos-header .user-id { font-size:20px;white-space:nowrap }
.pos-header .points { font-size:14px }
.pos-header .el-tag { font-size:14px;padding:5px 10px;flex-shrink:0 }
.pos-header .el-button { font-size:14px;padding:6px 12px;flex-shrink:0 }
.member-info { display:flex;align-items:center;gap:12px;flex:1;min-width:0 }
.header-actions { display:flex;align-items:center;gap:6px;width:460px;flex-shrink:0;justify-content:flex-end }
.header-actions { display:flex;align-items:center;gap:5px;flex-shrink:0;white-space:nowrap }
.pos-header .el-button { font-size:16px;padding:8px 16px }
.pos-header .el-button + .el-button { margin-left:0 }
.barcode-box { margin-bottom:6px }
.search-box { display:flex;gap:6px;margin-bottom:6px }
.quick-products { flex:1;overflow-y:auto }
.product-strip { display:grid;grid-template-columns:repeat(5, 1fr);gap:8px }
.hot-card { background:#fff;border:1px solid #ebeef5;border-radius:8px;padding:12px 8px;cursor:pointer;text-align:center }
.hot-card:hover { border-color:#67c23a;box-shadow:0 2px 6px rgba(103,194,58,.1) }
.hot-name { font-weight:600;font-size:17px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;margin-bottom:4px;color:#303133 }
.hot-price { color:#f56c6c;font-weight:bold;font-size:18px }
.barcode-box { margin-bottom:8px }
.barcode-box :deep(.el-input__inner) { font-size:16px !important }
.search-box :deep(.el-input__inner) { font-size:15px !important }
.section-title { font-size:18px;font-weight:bold;color:#303133;margin-bottom:10px }
.hot-price { color:#f56c6c;font-weight:bold;font-size:18px }

.pos-right { width:460px;display:flex;flex-direction:column;flex-shrink:0 }
.cart-panel { background:#fff;border-radius:8px;display:flex;flex-direction:column;height:100%;box-shadow:0 4px 12px rgba(0,0,0,.05) }
.cart-header { padding:14px 18px;border-bottom:1px solid #ebeef5;display:flex;justify-content:space-between;align-items:center;font-weight:bold;font-size:16px }
.cart-list { flex:1;overflow-y:auto;padding:10px }
.cart-item { background:#fcfcfc;border:1px solid #ebeef5;border-radius:6px;padding:12px;margin-bottom:8px }
.item-main { display:flex;justify-content:space-between;margin-bottom:6px }
.item-title { font-weight:500 }
.item-actions { display:flex;justify-content:space-between;align-items:center }
.price-calc { display:flex;align-items:center;gap:8px;font-size:12px;color:#909399 }
.subtotal { font-weight:bold;color:#f56c6c;font-size:15px }
.cart-footer { padding:16px 20px;background:#fff;border-top:1px solid #ebeef5 }
.points-row { margin-bottom:12px;padding:8px;background:#fdf6ec;border-radius:4px }
.check-label { font-weight:bold;color:#e6a23c }
.check-desc { font-size:12px;color:#909399;margin-left:5px }
.total-row { display:flex;justify-content:space-between;align-items:center;margin-bottom:16px }
.total-row .label { font-size:16px;color:#606266 }
.total-row .amount { font-size:28px;font-weight:bold;color:#f56c6c }
.checkout-btn { width:100%;height:56px;font-size:20px;font-weight:bold;border-radius:25px;letter-spacing:2px }

/* 交班对账 */
.close-table { width:100%;border-collapse:collapse;margin-top:12px }
.close-table td { padding:8px 12px;border-bottom:1px solid #ebeef5 }
.close-table td:first-child { color:#909399 }
.close-table td:last-child { text-align:right;font-weight:bold }
.close-table .highlight td { font-size:18px;color:#303133 }
.diff-red td { color:#f56c6c }
.diff-ok td { color:#67c23a }

/* 复用样式 */
.product-option { display:flex;justify-content:space-between;width:100% }
.opt-name { font-size:15px }
.opt-price { color:#f56c6c;font-size:15px }
.user-id { font-size:16px;font-weight:600 }
.result-box { display:flex;justify-content:center;padding-top:40px }
.receipt-card { width:400px;background:#fff;padding:24px;border:1px solid #ebeef5;box-shadow:0 4px 12px rgba(0,0,0,.05);margin-bottom:20px }
.receipt-header { text-align:center;margin-bottom:16px }
.receipt-header h3 { margin:0 0 4px }
.receipt-info { font-size:15px;color:#606266;margin-bottom:16px }
.info-row { display:flex;justify-content:space-between;margin-bottom:4px }
.receipt-items { list-style:none;padding:0;margin:16px 0 }
.receipt-items li { margin-bottom:8px }
.item-name { font-weight:500;margin-bottom:2px }
.item-calc { display:flex;justify-content:space-between;font-size:15px;color:#909399 }
.item-total { color:#303133 }
.receipt-total { display:flex;justify-content:space-between;align-items:center;margin-top:16px;font-size:18px;font-weight:bold }
.total-price { color:#f56c6c;font-size:22px }
.action-buttons { text-align:center }

/* 欢迎页 */
.welcome-box { display:flex;justify-content:center;align-items:center;height:80vh }
.welcome-card { width:500px;padding:50px;text-align:center;background:#fff;border-radius:16px;box-shadow:0 10px 30px rgba(0,0,0,.05) }
.welcome-icon { font-size:56px;margin-bottom:16px }
.welcome-card h2 { color:#303133;margin-bottom:8px }
.welcome-card p { color:#909399;margin-bottom:32px }
.input-area { display:flex;gap:10px }
.start-btn { flex-shrink:0 }

@media (max-width:768px) {
  .pos-layout { flex-direction:column;overflow:visible }
  .pos-right { width:100% }
  .cart-panel { height:400px }
  .welcome-card { width:90%;padding:30px 20px }
  .input-area { flex-direction:column }
  .start-btn { width:100% }
  .product-strip { grid-template-columns:repeat(auto-fill, minmax(100px,1fr)) }
  .shift-card { padding:30px 24px }
}
</style>
