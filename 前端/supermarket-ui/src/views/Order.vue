<template>
  <div class="order-management-container">
    <div class="header-actions">
      <h2>订单管理</h2>
      <div class="action-buttons">
        <el-button type="success" icon="Download" @click="exportExcel">导出Excel</el-button>
        <el-button type="primary" icon="Refresh" @click="fetchOrders">刷新</el-button>
      </div>
    </div>
    
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stat-cards">
      <el-col :span="8">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-title" style="color: #1d1d1f;">当前列表订单总额</div>
          <div class="stat-value" style="color: #1d1d1f;">￥{{ totalAmountSum.toFixed(2) }}</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-title">当前列表订单总数</div>
          <div class="stat-value">{{ validOrderList.length }} 单</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-title">已选订单总额</div>
          <div class="stat-value highlight">￥{{ selectedAmountSum.toFixed(2) }}</div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-card shadow="never">
      <el-table 
        :data="validOrderList" 
        style="width: 100%" 
        v-loading="loading"
        @selection-change="handleSelectionChange"
        border
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="id" label="订单号" width="180" />
        <el-table-column prop="createTime" label="下单时间" width="180" />
        <el-table-column prop="memberId" label="会员ID" width="100">
          <template #default="scope">
            {{ scope.row.memberId || '散客' }}
          </template>
        </el-table-column>
        <el-table-column prop="totalPrice" label="订单金额" sortable>
          <template #default="scope">
            ￥{{ scope.row.totalPrice?.toFixed(2) || '0.00' }}
          </template>
        </el-table-column>
        <el-table-column prop="points" label="获得积分" width="100" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag type="success">已完成</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="scope">
            <el-button size="small" type="primary" plain @click="viewDetail(scope.row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 订单详情对话框（小票样式） -->
    <el-dialog
      v-model="dialogVisible"
      title="订单详情"
      width="400px"
      custom-class="receipt-dialog"
    >
      <div class="receipt-card" v-loading="detailLoading" v-if="currentOrder">
        <div class="receipt-header">
          <h3>连锁超市购物小票</h3>
          <p>No. {{ currentOrder.id }}</p>
          <p class="receipt-time">{{ currentOrder.createTime }}</p>
        </div>
        <div class="receipt-info">
          <div class="info-row">
            <span>收银员：</span>
            <span>{{ formatCashierName(currentOrder.cashierAccount || currentOrder.cashierId || currentOrder.createBy || currentOrder.cashier) }}</span>
          </div>
          <div class="info-row">
            <span>会员ID：</span>
            <span>{{ currentOrder.memberId || '散客' }}</span>
          </div>
          <div class="info-row" v-if="currentOrder.memberId">
            <span>本次积分：</span>
            <span style="color: #e6a23c; font-weight: bold;">+{{ currentOrder.points || 0 }}</span>
          </div>
        </div>
        <el-divider border-style="dashed" />
        
        <!-- 如果后端有返回 items，直接展示；如果没有，给出提示 -->
        <div v-if="!currentOrder.items || currentOrder.items.length === 0" class="no-items-tip">
          * 详细商品明细需要后端提供查询接口 *
        </div>
        
        <ul class="receipt-items" v-else>
          <li v-for="(item, index) in currentOrder.items" :key="index">
            <div class="item-name">{{ item.productName || '商品' + item.productId }}</div>
            <div class="item-calc">
              <span>{{ item.quantity }} x ￥{{ item.price?.toFixed(2) }}</span>
              <span class="item-total">￥{{ (item.price * item.quantity).toFixed(2) }}</span>
            </div>
          </li>
        </ul>
        
        <el-divider border-style="dashed" />
        <div class="receipt-total">
          <span>实付金额</span>
          <span class="total-price">￥{{ currentOrder.totalPrice?.toFixed(2) }}</span>
        </div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">关闭</el-button>
          <el-button type="primary" @click="printReceipt">
            打印小票
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import request from '@/utils/request'
import { ElMessage } from 'element-plus'
import * as XLSX from 'xlsx' // 需要安装 xlsx 库

const orderList = ref([])
const loading = ref(false)
const selectedOrders = ref([])

// 详情弹窗相关状态
const dialogVisible = ref(false)
const detailLoading = ref(false)
const currentOrder = ref(null)

// 获取订单列表
const fetchOrders = async () => {
  loading.value = true
  try {
    const res = await request.get('/order/list')
    // 处理后端返回的数据结构（支持直接返回数组或带包装的数据）
    orderList.value = Array.isArray(res.data) ? res.data : (res.data?.list || res.data?.records || [])
  } catch (e) {
    console.error(e)
    ElMessage.error('获取订单列表失败')
  } finally {
    loading.value = false
  }
}

// 过滤出有效订单（总额大于0的订单），因为 0 元订单通常是用来查询积分的假订单
const validOrderList = computed(() => {
  return orderList.value.filter(order => order.totalPrice && order.totalPrice > 0)
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
  // 如果有选中的订单，就导出选中的；否则导出列表里所有的有效订单
  const dataToExport = selectedOrders.value.length > 0 ? selectedOrders.value : validOrderList.value
  
  if (dataToExport.length === 0) {
    ElMessage.warning('没有可导出的订单数据')
    return
  }

  // 1. 格式化要导出的数据，让表头更清晰
  const excelData = dataToExport.map(order => ({
    '订单号': order.id,
    '下单时间': order.createTime,
    '会员ID': order.memberId || '散客',
    '订单金额(元)': order.totalPrice,
    '获得积分': order.points,
    '状态': '已完成'
  }))

  // 2. 将数据转换为工作表
  const worksheet = XLSX.utils.json_to_sheet(excelData)
  
  // 3. 创建一个新的工作簿并添加工作表
  const workbook = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(workbook, worksheet, '订单数据')
  
  // 4. 生成 Excel 文件并下载
  const dateStr = new Date().toISOString().slice(0, 10)
  const fileName = selectedOrders.value.length > 0 
    ? `已选订单导出_${dateStr}.xlsx` 
    : `全部订单导出_${dateStr}.xlsx`
    
  XLSX.writeFile(workbook, fileName)
  ElMessage.success('导出成功！')
}

// 格式化收银员名称：提取账号中的英文字母部分
const formatCashierName = (account) => {
  // 如果后端完全没有返回任何收银员相关的字段，我们直接用当前登录的账号兜底
  if (!account) {
    const loginUser = localStorage.getItem('username') || localStorage.getItem('userAccount') || '自助'
    const match = loginUser.match(/^[a-zA-Z]+/)
    return match ? match[0] : loginUser
  }
  // 如果有账号，使用正则提取纯英文字母部分
  const match = account.match(/^[a-zA-Z]+/)
  return match ? match[0] : account
}

// 查看订单详情
const viewDetail = async (row) => {
  // 因为列表里可能没有 cashierAccount 字段，我们需要看看能不能从其它地方获取
  // 如果后端列表返回了 cashierAccount，就用它；否则尝试从 localStorage 里拿当前登录的人兜底（虽然不一定准）
  currentOrder.value = { 
    ...row,
    // 如果 row 里没有收银员信息，暂时留空，或者您也可以让后端在 /order/list 接口里加上 cashierAccount
  } 
  dialogVisible.value = true
  
    // 检查当前行有没有商品明细数组
  if (!row.items || row.items.length === 0) {
    // 如果列表接口没返回商品明细，尝试去请求后端的详情接口
    detailLoading.value = true
    try {
      // 尝试两种传参方式：id 和 orderId，因为我不确定您后端用的是哪个参数名
      const res = await request.get(`/order/detail`, { params: { orderId: row.id, id: row.id } })
      
      // 兼容两种返回格式：
      // 1. res.data.items (如果您在后端是直接把明细放在 items 属性里)
      // 2. res.data 本身就是个数组 (如果您在后端是直接返回 List<OrderItem>)
      // 3. 兼容后端可能返回的统一 Result 对象格式: res.data.data.items 或 res.data.data
      let detailItems = []
      
      const realData = res.data?.data || res.data
      
      if (Array.isArray(realData)) {
        detailItems = realData
      } else if (realData && Array.isArray(realData.items)) {
        detailItems = realData.items
      }

      if (detailItems.length > 0) {
        // 补充一下后端新返回的商品名字，因为后端返回的可能是 productId 而不是 productName
        currentOrder.value.items = detailItems.map(item => {
          return {
            ...item,
            productName: item.productName || `商品 (ID: ${item.productId})`
          }
        })
      } else {
        // 如果虽然请求成功了，但后端返回的 items 是空的，为了防止报错，给个空数组
        currentOrder.value.items = []
      }
    } catch (e) {
      console.warn('获取订单明细失败', e)
      ElMessage.error(e.response?.data?.message || '获取订单明细失败，请检查后端服务')
    } finally {
      detailLoading.value = false
    }
  }
}

// 打印小票
const printReceipt = () => {
  ElMessage.success('发送打印指令成功！')
  // 真实场景下这里会调用打印机 API
}

onMounted(() => {
  fetchOrders()
})
</script>

<style scoped>
.order-management-container {
  padding: 20px;
}
.header-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.action-buttons {
  display: flex;
  gap: 10px;
}
.stat-cards {
  margin-bottom: 20px;
}
.stat-card {
  text-align: center;
  padding: 10px 0;
}
.stat-title {
  font-size: 14px;
  color: #909399;
  margin-bottom: 10px;
}
.stat-value {
  font-size: 24px;
  font-weight: bold;
}
.stat-value.highlight {
  color: #f56c6c;
}

/* 订单详情弹窗的小票样式 */
.receipt-card {
  padding: 10px;
}

.receipt-header {
  text-align: center;
  margin-bottom: 20px;
}

.receipt-header h3 {
  margin: 0 0 5px 0;
  font-size: 18px;
}

.receipt-header p {
  margin: 0;
  color: #606266;
  font-size: 14px;
}

.receipt-time {
  font-size: 12px !important;
  color: #909399 !important;
  margin-top: 5px !important;
}

.receipt-info {
  font-size: 14px;
  color: #606266;
  margin-bottom: 15px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 5px;
}

.no-items-tip {
  text-align: center;
  color: #909399;
  font-size: 12px;
  padding: 20px 0;
  font-style: italic;
}

.receipt-items {
  list-style: none;
  padding: 0;
  margin: 15px 0;
}

.receipt-items li {
  margin-bottom: 10px;
}

.item-name {
  font-weight: 500;
  margin-bottom: 2px;
  font-size: 14px;
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
  margin-top: 15px;
  font-size: 16px;
  font-weight: bold;
}

.total-price {
  color: #f56c6c;
  font-size: 20px;
}
</style>