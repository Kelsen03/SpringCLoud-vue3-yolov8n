<template>
  <div class="hw-pos-page">
    <!-- ========= 阶段0：未开班 ========= -->
    <div v-if="!isShiftOpen" class="hw-center-box fade-up">
      <div class="hw-card">
        <h2 class="hw-title">SHIFT START / 开班上岗</h2>
        <p class="hw-subtitle">Input Opening Cash / 输入找零备用金</p>
        <div class="hw-huge-input">
          <span>¥</span>
          <input v-model="openingCash" type="number" step="0.01" min="0" placeholder="0.00" @keyup.enter="doOpenShift" />
        </div>
        <button class="hw-btn hw-btn-dark" @click="doOpenShift" :disabled="shiftLoading">
          <span class="btn-text">CONFIRM / 确认开班</span>
        </button>
      </div>
    </div>

    <!-- ========= 阶段1：欢迎界面（已开班，未开始收银） ========= -->
    <div v-else-if="!isStarted" class="hw-center-box fade-up">
      <div class="hw-card">
        <div class="hw-status-bar">
          <span class="status-dot pulsing"></span>
          <span>STATUS: ONLINE / 当班中 | 备用金 ¥{{ shiftOpeningCash }}</span>
          <button class="hw-text-btn" @click="showCloseDialog = true">CLOSE SHIFT / 交班 ↗</button>
        </div>
        <h2 class="hw-title">CASHIER SYSTEM / 智能收银</h2>
        <p class="hw-subtitle">Input Member ID or press Enter / 输入会员ID或直接回车</p>
        <div class="hw-huge-input">
          <input v-model="userId" placeholder="MEMBER ID / 会员号 (可选)" @keyup.enter="startCheckout" />
        </div>
        <button class="hw-btn hw-btn-dark" @click="startCheckout">
          <span class="btn-text">START / 开始收银 ↗</span>
        </button>
      </div>
    </div>

    <!-- ========= 阶段3：结算成功 ========= -->
    <div v-else-if="isFinished" class="hw-center-box fade-up">
      <div class="hw-receipt-card">
        <h2 class="hw-title">COMPLETED / 结算完成</h2>
        <p class="hw-subtitle">ORDER SUCCESS / 订单提交成功</p>
        
        <div class="receipt-paper">
          <div class="receipt-head">LKQ.RETAIL RECEIPT / 购物小票</div>
          <div class="receipt-no">NO. {{ orderInfo.id }}</div>
          <div class="receipt-row" v-if="orderInfo.storeName"><span>STORE / 门店</span><span>{{ orderInfo.storeName }}</span></div>
          <div class="receipt-row"><span>MEMBER / 会员</span><span>{{ orderInfo.userId || 'GUEST / 散客' }}</span></div>
          <div class="receipt-row" v-if="orderInfo.userId"><span>POINTS / 获得积分</span><span>+{{ orderInfo.points }}</span></div>
          
          <div class="receipt-divider"></div>
          
          <div class="receipt-item" v-for="item in orderInfo.items" :key="item.id">
            <div class="r-name">{{ item.name }}</div>
            <div class="r-calc">
              <span>{{ item.quantity }} x ¥{{ (item.usePromotion ? (item.promotionPrice||item.price) : item.price).toFixed(2) }}</span>
              <span>¥{{ ((item.usePromotion ? (item.promotionPrice||item.price) : item.price) * item.quantity).toFixed(2) }}</span>
            </div>
          </div>
          
          <div class="receipt-divider"></div>
          <div class="receipt-total">
            <span>TOTAL / 实付</span>
            <span>¥{{ orderInfo.totalAmount.toFixed(2) }}</span>
          </div>
        </div>

        <button class="hw-btn hw-btn-dark" @click="reset" style="margin-top: 30px;">
          <span class="btn-text">NEXT ORDER / 下一单 ↗</span>
        </button>
      </div>
    </div>

    <!-- ========= 阶段2：收银台主界面 ========= -->
    <div v-else class="hw-pos-layout fade-up">
      <!-- 顶部导航 -->
      <header class="hw-header">
        <div class="hw-brand">
          <span class="font-bold">LKQ.RETAIL</span> / POS SYSTEM
        </div>
        <div class="hw-customer">
          <span class="label">CUSTOMER / 顾客:</span> {{ userId ? userId : 'GUEST / 散客' }}
          <span v-if="memberPoints !== null" class="pts">| POINTS / 积分: {{ memberPoints }}</span>
        </div>
        <div class="hw-actions">
          <span class="cash-badge">OPENING CASH / 备用金: ¥{{ shiftOpeningCash }}</span>
          <button class="hw-text-btn" @click="showCloseDialog = true">CLOSE SHIFT / 交班 ↗</button>
          <button class="hw-text-btn danger" @click="exitCheckout">EXIT / 退出 ↗</button>
        </div>
      </header>

      <div class="hw-pos-main">
        <!-- 左侧：工作区 -->
        <div class="hw-workspace">
          <!-- AI 摄像头 -->
          <div class="hw-camera-section">
            <div class="camera-frame">
              <video ref="videoRef" autoplay playsinline class="ai-video"></video>
              <div class="camera-overlay"></div>
            </div>
            <button class="hw-btn hw-btn-outline" @click="captureAndRecognize" :disabled="isRecognizing">
              <span class="btn-text">AI RECOGNITION / 智能拍照识别</span>
            </button>
          </div>

          <!-- 商品检索区 -->
          <div class="hw-search-section">
            <div class="hw-input-line">
              <input v-model="barcodeInput" placeholder="BARCODE / 扫码或输入条形码..." @keyup.enter="onBarcodeEnter" @change="onBarcodeEnter" />
            </div>
            
            <div class="hw-manual-add">
              <el-select v-model="currentProductId" filterable placeholder="SEARCH PRODUCT / 搜索商品..." class="hw-select" popper-class="hw-dark-popper">
                <el-option v-for="item in productList" :key="item.id" :label="(item.barcode||'') + ' ' + item.name" :value="item.id" :disabled="!item.price||item.price<=0">
                  <div class="hw-option">
                    <span>{{ item.name }}</span>
                    <span v-if="item.price>0">¥{{ item.price }}</span>
                    <span v-else class="error">NO PRICE</span>
                  </div>
                </el-option>
              </el-select>
              <el-input-number v-model="currentQty" :min="1" class="hw-number" @keyup.enter="addToCart" />
              <button class="hw-btn hw-btn-dark small" @click="addToCart" :disabled="!currentProductId">ADD</button>
            </div>
          </div>

          <!-- 热门商品卡片 -->
          <div class="hw-hot-products">
            <h3 class="hw-section-title">HOT ITEMS / 热门商品</h3>
            <div class="hw-grid">
              <div v-for="item in hotProducts" :key="item.id" class="hw-item-card hover-3d" @click="quickAdd(item)">
                <div class="cate">{{ item.category }}</div>
                <div class="name">{{ item.name }}</div>
                <div class="price">¥{{ item.price.toFixed(2) }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- 右侧：购物车黑底极简风格 -->
        <div class="hw-cart-panel">
          <div class="cart-head">
            <h2>CART / 购物车</h2>
            <span>{{ cart.length }} ITEMS</span>
          </div>
          
          <div class="cart-body">
            <div v-if="cart.length===0" class="cart-empty">NO ITEMS / 暂无商品</div>
            <div v-else class="cart-item" v-for="(item, index) in cart" :key="index">
              <div class="c-info">
                <div class="c-name">{{ item.name }} <span v-if="item.usePromotion" class="promo-tag">PROMO</span></div>
                <div class="c-calc">
                  <div class="c-price-sel">
                    <el-radio-group v-if="item.promotionPrice && item.promotionPrice<item.price" v-model="item.usePromotion" size="small" class="hw-radio">
                      <el-radio-button :label="false">¥{{ item.price }}</el-radio-button>
                      <el-radio-button :label="true">¥{{ item.promotionPrice }}</el-radio-button>
                    </el-radio-group>
                    <span v-else>¥{{ item.price }}</span>
                  </div>
                  <span class="c-qty">x {{ item.quantity }}</span>
                </div>
              </div>
              <div class="c-right">
                <div class="c-subtotal">¥{{ ((item.usePromotion ? (item.promotionPrice||item.price) : item.price) * item.quantity).toFixed(2) }}</div>
                <button class="c-del" @click="removeFromCart(index)">✕</button>
              </div>
            </div>
          </div>

          <div class="cart-foot">
            <div class="c-points" v-if="memberPoints!==null && canUsePoints">
              <el-checkbox v-model="usePoints" class="hw-checkbox">
                USE POINTS / 使用积分 (-¥5.00 / 1000 PTS)
              </el-checkbox>
            </div>
            <div class="c-total">
              <span>TOTAL / 应付</span>
              <span class="amount">¥{{ (usePoints ? totalAmount-5 : totalAmount).toFixed(2) }}</span>
            </div>
            <button class="hw-btn hw-btn-light block" @click="submitOrder" :disabled="cart.length===0">
              <span class="btn-text">CHECKOUT / 结算 ↗</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- ========= 交班对账弹窗 (极简黑白) ========= -->
    <el-dialog v-model="showCloseDialog" title="CLOSE SHIFT / 交班对账" width="500px" :close-on-click-modal="false" custom-class="hw-dialog">
      <div class="hw-close-content" v-if="closeResult">
        <h2 class="hw-title small">SHIFT COMPLETED</h2>
        <div class="hw-receipt-paper">
          <div class="r-row"><span>备用金 (OPENING)</span><span>¥{{ closeResult.openingCash }}</span></div>
          <div class="r-row"><span>系统现金 (SYS CASH)</span><span>¥{{ closeResult.systemCash }}</span></div>
          <div class="r-row"><span>在线支付 (ONLINE)</span><span>¥{{ closeResult.systemOnline }}</span></div>
          <div class="r-row"><span>总单数 (ORDERS)</span><span>{{ closeResult.totalOrders }}</span></div>
          <div class="hw-divider"></div>
          <div class="r-row bold"><span>应有现金 (THEORY)</span><span>¥{{ closeResult.theoryCash }}</span></div>
          <div class="r-row bold"><span>实点现金 (ACTUAL)</span><span>¥{{ closeResult.closingCash }}</span></div>
          <div class="r-row giant" :class="Math.abs(closeResult.diff)>0.01 ? 'error':'success'">
            <span>差异 (DIFF)</span><span>¥{{ closeResult.diff }}</span>
          </div>
        </div>
        <button class="hw-btn hw-btn-dark block" @click="finishShift" style="margin-top:20px">
          <span class="btn-text">LOGOUT / 确认退出 ↗</span>
        </button>
      </div>
      <div v-else class="hw-close-input">
        <p class="hw-subtitle">ACTUAL CASH / 输入收银机实点现金</p>
        <div class="hw-huge-input">
          <span>¥</span>
          <input v-model="closingCash" type="number" step="0.01" min="0" placeholder="0.00" @keyup.enter="doCloseShift" />
        </div>
        <button class="hw-btn hw-btn-dark block" @click="doCloseShift" :disabled="shiftLoading" style="margin-top:30px">
          <span class="btn-text">CONFIRM / 确认交班 ↗</span>
        </button>
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
/* 渡邊浩樹风格极简黑白 UI */
.hw-pos-page {
  height: 100vh;
  background-color: #f7f7f7;
  color: #111;
  font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
  overflow: hidden;
  box-sizing: border-box;
}

/* 动画 */
.fade-up { animation: fadeUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards; }
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(30px); }
  to { opacity: 1; transform: translateY(0); }
}

/* 居中大卡片（开班、欢迎、结算成功） */
.hw-center-box {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
}
.hw-card, .hw-receipt-card {
  width: 500px;
  background: #fff;
  padding: 60px 50px;
  border-radius: 2px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.05);
  text-align: center;
}
.hw-title {
  font-size: 36px;
  font-weight: 800;
  letter-spacing: -1px;
  margin: 0 0 10px 0;
  text-transform: uppercase;
}
.hw-title.small { font-size: 24px; }
.hw-subtitle {
  font-size: 14px;
  color: #666;
  margin-bottom: 40px;
  letter-spacing: 1px;
}

/* 巨大输入框 */
.hw-huge-input {
  display: flex;
  align-items: center;
  border-bottom: 2px solid #111;
  margin-bottom: 40px;
  padding-bottom: 10px;
}
.hw-huge-input span {
  font-size: 32px;
  font-weight: bold;
  margin-right: 15px;
}
.hw-huge-input input {
  flex: 1;
  border: none;
  background: transparent;
  outline: none;
  font-size: 32px;
  font-weight: bold;
  color: #111;
  width: 100%;
}
.hw-huge-input input::placeholder { color: #ccc; font-weight: normal; font-size: 24px; }

/* 按钮通用 */
.hw-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 16px 32px;
  font-size: 14px;
  font-weight: bold;
  letter-spacing: 2px;
  cursor: pointer;
  border: none;
  transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
  border-radius: 0;
}
.hw-btn.block { width: 100%; }
.hw-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.hw-btn-dark { background: #111; color: #fff; }
.hw-btn-dark:hover:not(:disabled) { background: #333; transform: translateY(-2px); box-shadow: 0 10px 20px rgba(0,0,0,0.2); }
.hw-btn-light { background: #fff; color: #111; border: 1px solid #111; }
.hw-btn-light:hover:not(:disabled) { background: #f0f0f0; transform: translateY(-2px); }
.hw-btn-outline { background: transparent; color: #111; border: 2px solid #111; }
.hw-btn-outline:hover:not(:disabled) { background: #111; color: #fff; }

.hw-text-btn {
  background: transparent;
  border: none;
  font-weight: bold;
  font-size: 12px;
  letter-spacing: 1px;
  cursor: pointer;
  color: #111;
  padding: 5px 10px;
  transition: opacity 0.3s;
}
.hw-text-btn:hover { opacity: 0.6; }
.hw-text-btn.danger { color: #d93025; }

/* 状态条 */
.hw-status-bar {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  background: #f0f0f0;
  padding: 8px 16px;
  border-radius: 30px;
  font-size: 12px;
  font-weight: bold;
  margin-bottom: 30px;
}
.status-dot { width: 8px; height: 8px; background: #34a853; border-radius: 50%; }
.pulsing { animation: pulse 2s infinite; }
@keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(52,168,83,0.4); } 70% { box-shadow: 0 0 0 6px rgba(52,168,83,0); } 100% { box-shadow: 0 0 0 0 rgba(52,168,83,0); } }

/* 购物小票风格 */
.receipt-paper, .hw-receipt-paper {
  background: #fff;
  border: 1px solid #eee;
  padding: 30px;
  text-align: left;
  font-family: 'Courier New', Courier, monospace;
  box-shadow: 0 5px 15px rgba(0,0,0,0.03);
}
.receipt-head { text-align: center; font-size: 18px; font-weight: bold; margin-bottom: 5px; }
.receipt-no { text-align: center; font-size: 12px; color: #666; margin-bottom: 20px; }
.receipt-row, .r-row { display: flex; justify-content: space-between; font-size: 13px; margin-bottom: 8px; }
.r-row.bold { font-weight: bold; font-size: 14px; }
.r-row.giant { font-size: 18px; font-weight: bold; margin-top: 10px; }
.r-row.giant.error { color: #d93025; }
.r-row.giant.success { color: #34a853; }
.receipt-divider, .hw-divider { border-top: 1px dashed #ccc; margin: 15px 0; }
.receipt-item { margin-bottom: 12px; }
.r-name { font-weight: bold; font-size: 14px; margin-bottom: 4px; }
.r-calc { display: flex; justify-content: space-between; font-size: 13px; color: #666; }
.receipt-total { display: flex; justify-content: space-between; font-size: 20px; font-weight: bold; margin-top: 20px; }

/* 主收银界面布局 */
.hw-pos-layout {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 20px;
}
.hw-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px 20px 20px;
  border-bottom: 2px solid #111;
  margin-bottom: 20px;
}
.hw-brand { font-size: 20px; letter-spacing: 1px; }
.font-bold { font-weight: 900; }
.hw-customer { font-size: 14px; font-weight: bold; }
.hw-customer .label { color: #888; }
.hw-customer .pts { color: #d93025; margin-left: 10px; }
.hw-actions { display: flex; align-items: center; gap: 15px; }
.cash-badge { background: #111; color: #fff; padding: 4px 10px; font-size: 12px; font-weight: bold; }

.hw-pos-main {
  display: flex;
  flex: 1;
  gap: 30px;
  overflow: hidden;
}

/* 左侧工作区 */
.hw-workspace { flex: 1; display: flex; flex-direction: column; gap: 20px; min-width: 0; }

.hw-camera-section { display: flex; gap: 20px; align-items: stretch; }
.camera-frame { flex: 1; position: relative; background: #000; border-radius: 2px; overflow: hidden; height: 320px; }
.ai-video { width: 100%; height: 100%; object-fit: cover; opacity: 0.8; }
.camera-overlay { position: absolute; inset: 20px; border: 1px solid rgba(255,255,255,0.3); pointer-events: none; }
.camera-overlay::after { content:''; position: absolute; top: 50%; left: 0; right: 0; height: 1px; background: rgba(52,168,83,0.5); box-shadow: 0 0 10px #34a853; animation: scan 2s linear infinite; }
@keyframes scan { 0% { transform: translateY(-100px); } 50% { transform: translateY(100px); } 100% { transform: translateY(-100px); } }

.hw-search-section { background: #fff; padding: 20px; box-shadow: 0 5px 20px rgba(0,0,0,0.03); }
.hw-input-line { border-bottom: 2px solid #111; margin-bottom: 15px; padding-bottom: 8px; }
.hw-input-line input { width: 100%; border: none; outline: none; font-size: 18px; font-weight: bold; background: transparent; }
.hw-input-line input::placeholder { color: #bbb; font-weight: normal; }

.hw-manual-add { display: flex; gap: 15px; }
.hw-select { flex: 1; }
:deep(.hw-select .el-input__inner) { font-size: 16px; font-weight: bold; height: 44px; }
.hw-option { display: flex; justify-content: space-between; width: 100%; }
.hw-option .error { color: #d93025; }
.hw-number { width: 120px; }
:deep(.hw-number .el-input__inner) { font-size: 16px; font-weight: bold; height: 44px; }

.hw-hot-products { flex: 1; overflow-y: auto; padding-right: 10px; }
.hw-section-title { font-size: 14px; font-weight: bold; letter-spacing: 1px; margin-bottom: 15px; color: #888; }
.hw-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 15px; }
.hw-item-card { background: #fff; padding: 20px 15px; text-align: center; cursor: pointer; border: 1px solid #eee; transition: all 0.3s; }
.hw-item-card.hover-3d:hover { border-color: #111; transform: translateY(-5px); box-shadow: 0 15px 30px rgba(0,0,0,0.08); }
.hw-item-card .cate { font-size: 10px; color: #888; margin-bottom: 5px; text-transform: uppercase; }
.hw-item-card .name { font-size: 14px; font-weight: bold; margin-bottom: 10px; height: 38px; overflow: hidden; }
.hw-item-card .price { font-size: 16px; font-weight: 900; color: #111; }

/* 右侧购物车（极简黑底白字风格） */
.hw-cart-panel {
  width: 400px;
  background: #111;
  color: #fff;
  display: flex;
  flex-direction: column;
  box-shadow: -10px 0 30px rgba(0,0,0,0.1);
}
.cart-head { padding: 30px; border-bottom: 1px solid #333; display: flex; justify-content: space-between; align-items: center; }
.cart-head h2 { margin: 0; font-size: 20px; font-weight: 800; letter-spacing: 1px; }
.cart-head span { font-size: 12px; background: #fff; color: #111; padding: 4px 8px; font-weight: bold; }

.cart-body { flex: 1; overflow-y: auto; padding: 20px 30px; }
.cart-empty { text-align: center; color: #555; font-weight: bold; font-size: 14px; margin-top: 50px; letter-spacing: 1px; }
.cart-item { display: flex; justify-content: space-between; margin-bottom: 20px; padding-bottom: 20px; border-bottom: 1px solid #222; }
.c-info { flex: 1; padding-right: 15px; }
.c-name { font-size: 15px; font-weight: bold; margin-bottom: 10px; line-height: 1.4; }
.promo-tag { background: #d93025; color: #fff; font-size: 10px; padding: 2px 4px; margin-left: 5px; vertical-align: middle; }
.c-calc { display: flex; align-items: center; justify-content: space-between; font-size: 14px; color: #aaa; }
.c-right { text-align: right; display: flex; flex-direction: column; justify-content: space-between; align-items: flex-end; }
.c-subtotal { font-size: 16px; font-weight: bold; color: #fff; }
.c-del { background: transparent; border: none; color: #666; cursor: pointer; font-size: 16px; transition: color 0.3s; }
.c-del:hover { color: #d93025; }

/* 黑色面板里的单选框样式覆盖 */
.hw-radio :deep(.el-radio-button__inner) { background: #222; border-color: #444; color: #aaa; padding: 4px 8px; font-size: 12px; }
.hw-radio :deep(.el-radio-button__original-radio:checked + .el-radio-button__inner) { background: #fff; color: #111; border-color: #fff; box-shadow: none; }

.cart-foot { padding: 30px; border-top: 1px solid #333; background: #0a0a0a; }
.c-points { margin-bottom: 20px; }
.hw-checkbox :deep(.el-checkbox__label) { color: #aaa; font-size: 12px; font-weight: bold; }
.hw-checkbox :deep(.el-checkbox__input.is-checked + .el-checkbox__label) { color: #fff; }
.c-total { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 30px; }
.c-total span { font-size: 14px; color: #aaa; font-weight: bold; letter-spacing: 1px; }
.c-total .amount { font-size: 36px; color: #fff; line-height: 1; }

/* 弹窗覆盖 */
:deep(.hw-dialog) { border-radius: 0 !important; }
:deep(.hw-dialog .el-dialog__header) { border-bottom: 2px solid #111; padding-bottom: 15px; margin-right: 0; }
:deep(.hw-dialog .el-dialog__title) { font-weight: 800; letter-spacing: 1px; }
</style>
