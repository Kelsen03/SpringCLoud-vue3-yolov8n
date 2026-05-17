<template>
  <div class="order-page page-container">
    <div class="page-header">
      <div class="header-left">
        <h2 class="display-title">
          <span class="cn-title">订单管理</span>
          <span class="en-title">/ Orders.</span>
        </h2>
        <span class="sub-text">Transactions & Bills / 交易与账单</span>
      </div>
      <div class="header-right">
        <div class="minimal-filter" v-if="role === 'HQ'">
          <span class="filter-label">门店 Store:</span>
          <select v-model="storeId" @change="load" class="minimal-select">
            <option :value="''">全部门店 (ALL)</option>
            <option :value="1">门店 1 (BJ)</option>
            <option :value="2">门店 2 (SH)</option>
            <option :value="3">门店 3 (GZ)</option>
          </select>
        </div>
      </div>
    </div>

    <!-- 统计看板与导出 -->
    <div class="stat-overview">
      <div class="stat-box">
        <div class="stat-label">总营收 <span class="en-text">/ TOTAL REVENUE</span></div>
        <div class="stat-value">¥ {{ totalAmountSum.toFixed(2) }}</div>
      </div>
      <div class="stat-box">
        <div class="stat-label">订单总数 <span class="en-text">/ TOTAL ORDERS</span></div>
        <div class="stat-value">{{ validOrderList.length }}</div>
      </div>
      <div class="stat-box">
        <div class="stat-label">已选金额 <span class="en-text">/ SELECTED AMOUNT</span></div>
        <div class="stat-value highlight">¥ {{ selectedAmountSum.toFixed(2) }}</div>
      </div>
      <div class="stat-actions">
        <button class="minimal-btn" @click="exportExcel">导出 EXCEL <span class="en-text">/ EXPORT</span></button>
      </div>
    </div>

    <div class="table-container" style="width: 100%;">
      <el-table 
        :data="validOrderList" 
        stripe
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" align="center" />
        
        <el-table-column prop="id" label="订单号 / Order ID" min-width="180">
          <template #default="{ row }">
            <span class="id-text">#{{ row.id }}</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="createTime" label="下单时间 / Date" min-width="200">
          <template #default="{ row }">
            <span class="mono-text">{{ dayjs(row.createTime).format('YYYY.MM.DD HH:mm') }}</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="memberId" label="会员 / Member" min-width="120">
          <template #default="{ row }">
            <span class="member-tag">{{ row.memberId ? 'M-' + row.memberId : '散客 GUEST' }}</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="totalPrice" label="金额 / Amount" min-width="150" align="right">
          <template #default="{ row }">
            <span class="price-text">¥ {{ row.totalPrice?.toFixed(2) || '0.00' }}</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="points" label="积分 / Points" min-width="120" align="right">
          <template #default="{ row }">
            <span class="points-text">+{{ row.points }}</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="status" label="状态 / Status" min-width="150" align="center">
          <template #default="scope">
            <span class="minimal-tag success">已完成 COMPLETED</span>
          </template>
        </el-table-column>
        
        <el-table-column label="操作 / Action" width="160" fixed="right" align="right">
          <template #default="scope">
            <button class="minimal-btn" @click="viewDetail(scope.row)">详情 VIEW</button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 订单详情对话框（极简风格） -->
    <el-dialog
      v-model="dialogVisible"
      title="订单详情 / ORDER DETAILS"
      width="400px"
      custom-class="minimal-dialog"
      :show-close="false"
    >
      <div class="receipt-card" v-loading="detailLoading" v-if="currentOrder">
        <div class="receipt-header">
          <h3>Supermarket OS</h3>
          <p class="receipt-store">{{ currentOrder.storeName || 'Store ' + (currentOrder.storeId || storeId || 1) }}</p>
          <div class="receipt-divider"></div>
        </div>
        
        <div class="receipt-info">
          <div class="info-row">
            <span>NO.</span>
            <span class="mono-text">{{ currentOrder.orderNo || currentOrder.id }}</span>
          </div>
          <div class="info-row">
            <span>TIME</span>
            <span class="mono-text">{{ dayjs(currentOrder.createTime).format('YYYY-MM-DD HH:mm') }}</span>
          </div>
          <div class="info-row" v-if="currentOrder.createBy">
            <span>CASHIER</span>
            <span>{{ currentOrder.createBy }}</span>
          </div>
        </div>
        
        <div class="receipt-divider dashed"></div>
        
        <div class="receipt-items">
          <div class="item-row header">
            <span class="item-name">ITEM</span>
            <span class="item-qty">QTY</span>
            <span class="item-price">AMT</span>
          </div>
          <div v-for="(item, index) in currentOrder.items" :key="index" class="item-row">
            <span class="item-name">{{ item.productName || ('Product #' + item.productId) }}</span>
            <span class="item-qty">x{{ item.quantity }}</span>
            <span class="item-price">¥{{ (item.price * item.quantity).toFixed(2) }}</span>
          </div>
        </div>
        
        <div class="receipt-divider"></div>
        
        <div class="receipt-total">
          <div class="total-row">
            <span>TOTAL</span>
            <span class="total-amount">¥{{ currentOrder.totalPrice?.toFixed(2) }}</span>
          </div>
          <div class="points-row" v-if="currentOrder.points">
            <span>POINTS EARNED</span>
            <span>+{{ currentOrder.points }}</span>
          </div>
          <div class="points-row" v-if="currentOrder.memberId">
            <span>MEMBER ID</span>
            <span>{{ currentOrder.memberId }}</span>
          </div>
        </div>
        
        <div class="receipt-footer">
          <p>THANK YOU</p>
          <button class="minimal-btn print-btn" @click="dialogVisible = false">CLOSE</button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'
import dayjs from 'dayjs'
import * as XLSX from 'xlsx'

const list = ref([])
const selectedOrders = ref([])
const role = localStorage.getItem('role')
const storeId = ref('')
const dialogVisible = ref(false)
const currentOrder = ref(null)
const detailLoading = ref(false)

const load = async () => {
  try {
    const res = await request.get('/order/list', {
      params: { storeId: storeId.value }
    })
    list.value = res.data || []
  } catch (e) {
    console.error('Failed to load orders', e)
  }
}

// 过滤出有效订单（总额大于0的订单）
const validOrderList = computed(() => {
  return list.value.filter(order => order.totalPrice && order.totalPrice > 0)
})

// 监听表格勾选事件
const handleSelectionChange = (val) => {
  selectedOrders.value = val
}

// 计算当前列表所有订单的总额
const totalAmountSum = computed(() => {
  return validOrderList.value.reduce((sum, order) => sum + (order.totalPrice || 0), 0)
})

// 计算已选订单的总额
const selectedAmountSum = computed(() => {
  return selectedOrders.value.reduce((sum, order) => sum + (order.totalPrice || 0), 0)
})

// 导出 Excel 功能
const exportExcel = () => {
  const dataToExport = selectedOrders.value.length > 0 ? selectedOrders.value : validOrderList.value
  
  if (dataToExport.length === 0) {
    ElMessage.warning('没有可导出的订单数据 / No data to export')
    return
  }

  const excelData = dataToExport.map(order => ({
    '订单号 (Order ID)': order.id,
    '下单时间 (Time)': dayjs(order.createTime).format('YYYY-MM-DD HH:mm:ss'),
    '会员ID (Member)': order.memberId || '散客 (Guest)',
    '订单金额 (Amount)': order.totalPrice,
    '获得积分 (Points)': order.points,
    '状态 (Status)': '已完成 (Completed)'
  }))

  const worksheet = XLSX.utils.json_to_sheet(excelData)
  const workbook = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(workbook, worksheet, 'Orders')
  
  const dateStr = dayjs().format('YYYYMMDD')
  const fileName = selectedOrders.value.length > 0 
    ? `Selected_Orders_${dateStr}.xlsx` 
    : `All_Orders_${dateStr}.xlsx`
    
  XLSX.writeFile(workbook, fileName)
  ElMessage.success('导出成功 / Export successful!')
}

const viewDetail = async (row) => {
  currentOrder.value = { ...row } 
  dialogVisible.value = true
  
  if (!row.items || row.items.length === 0) {
    detailLoading.value = true
    try {
      const res = await request.get(`/order/detail`, { params: { orderId: row.id, id: row.id } })
      
      let detailItems = []
      const realData = res.data?.data || res.data
      
      if (Array.isArray(realData)) {
        detailItems = realData
      } else if (realData && Array.isArray(realData.items)) {
        detailItems = realData.items
      }

      if (detailItems.length > 0) {
        currentOrder.value.items = detailItems
      } else {
        currentOrder.value.items = [{
          productId: 'N/A',
          productName: 'Item info unavailable',
          quantity: 1,
          price: row.totalPrice || 0
        }]
      }
    } catch (e) {
      console.error(e)
    } finally {
      detailLoading.value = false
    }
  }
}

onMounted(() => {
  load()
})
</script>

<style scoped>
.page-container {
  animation: fadeUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

@keyframes fadeUp {
  0% { opacity: 0; transform: translateY(30px); }
  100% { opacity: 1; transform: translateY(0); }
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 60px;
  padding-bottom: 20px;
  border-bottom: 2px solid var(--w-text);
}

.stat-overview {
  display: flex;
  gap: 40px;
  margin-bottom: 40px;
  padding: 30px;
  background: rgba(255, 255, 255, 0.5);
  border: 1px solid var(--w-border);
}

.stat-box {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
  border-right: 1px solid var(--w-border);
}

.stat-box:last-of-type {
  border-right: none;
}

.stat-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--w-text-gray);
  text-transform: uppercase;
  letter-spacing: 1px;
}

.stat-value {
  font-size: 32px;
  font-weight: 800;
  letter-spacing: -1px;
}

.stat-value.highlight {
  color: #ff3b30;
}

.stat-actions {
  display: flex;
  align-items: center;
  padding-left: 20px;
}

.en-text {
  font-size: 10px;
  opacity: 0.6;
}

.display-title {
  margin: 0;
  font-weight: 800;
  line-height: 1;
  display: flex;
  align-items: baseline;
  gap: 12px;
}

.cn-title {
  font-size: 36px;
  letter-spacing: 2px;
}

.en-title {
  font-size: 64px;
  letter-spacing: -2px;
  color: var(--w-text-gray);
  opacity: 0.3;
}

.sub-text {
  font-size: 14px;
  color: var(--w-text-gray);
  text-transform: uppercase;
  letter-spacing: 2px;
  margin-left: 4px;
}

.minimal-filter {
  display: flex;
  align-items: center;
  gap: 12px;
}

.filter-label {
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.minimal-select {
  appearance: none;
  background: transparent;
  border: none;
  border-bottom: 1px solid var(--w-border);
  padding: 8px 24px 8px 0;
  font-family: 'Helvetica Neue', monospace;
  font-size: 16px;
  font-weight: 600;
  color: var(--w-text);
  outline: none;
  cursor: pointer;
  background-image: url("data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22292.4%22%20height%3D%22292.4%22%3E%3Cpath%20fill%3D%22%23000000%22%20d%3D%22M287%2069.4a17.6%2017.6%200%200%200-13-5.4H18.4c-5%200-9.3%201.8-12.9%205.4A17.6%2017.6%200%200%200%200%2082.2c0%205%201.8%209.3%205.4%2012.9l128%20127.9c3.6%203.6%207.8%205.4%2012.8%205.4s9.2-1.8%2012.8-5.4L287%2095c3.5-3.5%205.4-7.8%205.4-12.8%200-5-1.9-9.2-5.5-12.8z%22%2F%3E%3C%2Fsvg%3E");
  background-repeat: no-repeat;
  background-position: right 8px center;
  background-size: 10px auto;
}

.minimal-select:focus {
  border-bottom-color: var(--w-text);
}

.id-text, .mono-text {
  font-family: 'Helvetica Neue', monospace;
  color: var(--w-text-gray);
  font-size: 14px;
}

.price-text {
  font-family: 'Helvetica Neue', monospace;
  font-size: 16px;
  font-weight: 500;
}

.points-text {
  font-family: 'Helvetica Neue', monospace;
  color: #34c759;
  font-weight: 600;
}

.member-tag {
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1px;
  padding: 4px 8px;
  background: var(--w-hover-bg);
  color: var(--w-text);
}

.minimal-tag {
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1px;
  padding: 4px 8px;
  border: 1px solid var(--w-border);
}

.minimal-tag.success {
  color: #34c759;
  border-color: #34c759;
}

.minimal-btn {
  background: transparent;
  border: 1px solid var(--w-text);
  color: var(--w-text);
  padding: 6px 16px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1px;
  transition: all 0.3s ease;
}

.minimal-btn:hover {
  background: var(--w-text);
  color: var(--w-bg);
}

/* 极简小票样式 */
:deep(.minimal-dialog) {
  background: var(--w-bg);
  border: 1px solid var(--w-border);
  box-shadow: 0 20px 60px rgba(0,0,0,0.1);
  border-radius: 0;
}

:deep(.el-dialog__header) {
  padding: 20px 20px 0;
  margin-right: 0;
}

:deep(.el-dialog__title) {
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 2px;
}

.receipt-card {
  padding: 10px;
  font-family: 'Helvetica Neue', monospace;
  color: var(--w-text);
}

.receipt-header {
  text-align: center;
  margin-bottom: 20px;
}

.receipt-header h3 {
  margin: 0 0 5px;
  font-size: 18px;
  font-weight: 800;
  letter-spacing: -0.5px;
}

.receipt-store {
  margin: 0;
  font-size: 12px;
  color: var(--w-text-gray);
  text-transform: uppercase;
}

.receipt-divider {
  height: 2px;
  background: var(--w-text);
  margin: 15px 0;
}

.receipt-divider.dashed {
  height: 1px;
  background: transparent;
  border-top: 1px dashed var(--w-border);
}

.info-row {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  margin-bottom: 8px;
  color: var(--w-text-gray);
}

.item-row {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  margin-bottom: 12px;
}

.item-row.header {
  font-size: 10px;
  color: var(--w-text-gray);
  margin-bottom: 15px;
}

.item-name { flex: 2; }
.item-qty { flex: 1; text-align: center; }
.item-price { flex: 1; text-align: right; }

.receipt-total {
  margin-top: 20px;
}

.total-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 16px;
  font-weight: 700;
  margin-bottom: 10px;
}

.total-amount {
  font-size: 24px;
}

.points-row {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: var(--w-text-gray);
  margin-bottom: 5px;
}

.receipt-footer {
  text-align: center;
  margin-top: 40px;
}

.receipt-footer p {
  font-size: 12px;
  letter-spacing: 2px;
  margin-bottom: 20px;
}

.print-btn {
  width: 100%;
  padding: 12px;
}
</style>