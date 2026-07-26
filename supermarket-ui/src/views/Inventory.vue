<template>
  <div class="inventory-page page-container">
    <div class="page-header">
      <div class="header-left">
        <h2 class="display-title">
          <span class="cn-title">门店库存</span>
          <span class="en-title">/ Inventory.</span>
        </h2>
        <span class="sub-text">Stock Monitoring</span>
      </div>
      <div class="header-right">
        <div class="minimal-filter">
          <span class="filter-label">Store:</span>
          <select v-model="storeId" @change="load" class="minimal-select">
            <option :value="1">Store 01 (BJ)</option>
            <option :value="2">Store 02 (SH)</option>
            <option :value="3">Store 03 (GZ)</option>
          </select>
        </div>
      </div>
    </div>

    <div class="table-container">
      <el-table 
        :data="list" 
        stripe
        style="width: 100%"
      >
        <el-table-column prop="productId" label="编号 / ID" width="120" align="left">
          <template #default="{ row }">
            <span class="id-text">#{{ String(row.productId).padStart(4, '0') }}</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="productName" label="商品名称 / Product" min-width="200">
          <template #default="{ row }">
            <span class="product-name">{{ row.productName }}</span>
          </template>
        </el-table-column>
        
        <el-table-column label="库存情况 / Stock Level" width="250">
          <template #default="{ row }">
            <div class="stock-info">
              <span class="stock-num" :class="{ 'low-stock': row.stock <= row.warningStock }">
                {{ String(row.stock).padStart(3, '0') }}
              </span>
              <span class="warning-line">/ {{ String(row.warningStock).padStart(3, '0') }}</span>
            </div>
            <div class="minimal-progress-bar">
              <div class="minimal-progress-inner" 
                   :class="{ 'danger': row.stock <= row.warningStock }"
                   :style="{ width: Math.min((row.stock / (row.warningStock * 3)) * 100, 100) + '%' }">
              </div>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column label="生产日期 / Production" width="160" align="center">
          <template #default="{ row }">
            <span class="mono-text">{{ row.productionDate ? dayjs(row.productionDate).format('YYYY.MM.DD') : 'N/A' }}</span>
          </template>
        </el-table-column>

        <el-table-column label="状态 / Status" width="180">
          <template #default="scope">
            <div class="status-tags">
              <span v-if="scope.row.stock <= scope.row.warningStock" class="minimal-tag danger">缺货 LOW STOCK</span>
              <span class="minimal-tag" :class="getStatusClass(scope.row)">
                {{ getStatus(scope.row).text }}
              </span>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column label="操作 / Action" width="220" align="right" fixed="right">
          <template #default="scope">
            <template v-if="role === 'HQ' || (role === 'STORE' && Number(storeId) === currentStoreId)">
              <button 
                class="minimal-btn warning-btn"
                @click="handleClear(scope.row)"
                style="margin-right: 8px;"
              >
                清零 CLEAR
              </button>
              <button 
                class="minimal-btn danger-btn"
                @click="handleDelete(scope.row)"
              >
                删除 DEL
              </button>
            </template>
            <span v-else class="mono-text" style="color: var(--w-text-gray); font-size: 10px;">仅查看 READ ONLY</span>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getInventoryList, deleteInventory, clearInventory } from '@/api/inventory'
import { getProductList } from '@/api/product'
import { ElMessage, ElMessageBox } from 'element-plus'
import dayjs from 'dayjs'

const userStoreId = Number(localStorage.getItem('storeId'))
const currentStoreId = ref(userStoreId || 1) 
const storeId = ref(currentStoreId.value) 
const role = ref(localStorage.getItem('role')) 
const list = ref([])
const productMap = ref({}) 

const loadProducts = async () => {
  try {
    const res = await getProductList()
    if (res.data) {
      res.data.forEach(p => {
        productMap.value[p.id] = p
      })
    }
  } catch (e) {
    console.error('Failed to load products', e)
  }
}

const load = async () => {
  try {
    const res = await getInventoryList(storeId.value)
    list.value = res.data || []
    
    list.value.forEach(item => {
      if (!item.productName && productMap.value[item.productId]) {
        item.productName = productMap.value[item.productId].name
      }
    })
  } catch (e) {
    console.error('Failed to load inventory', e)
  }
}

const handleClear = (row) => {
  ElMessageBox.confirm(
    `Set stock to 0 for #${row.productId}?`,
    'Warning',
    {
      confirmButtonText: 'CLEAR',
      cancelButtonText: 'CANCEL',
      type: 'warning',
      customClass: 'minimal-msgbox'
    }
  ).then(async () => {
    try {
      const res = await clearInventory(storeId.value, row.productId)
      if (res.data === 'ok') {
        ElMessage.success('Stock cleared')
        load()
      } else {
        ElMessage.error(res.data || 'Clear failed')
      }
    } catch (e) {
      ElMessage.error('Clear failed')
    }
  }).catch(() => {})
}

const handleDelete = (row) => {
  ElMessageBox.confirm(
    `Delete inventory for #${row.productId} in Store ${storeId.value}?`,
    'Warning',
    {
      confirmButtonText: 'DELETE',
      cancelButtonText: 'CANCEL',
      type: 'warning',
      customClass: 'minimal-msgbox'
    }
  ).then(async () => {
    try {
      const res = await deleteInventory(storeId.value, row.productId)
      if (res.data === 'ok') {
        ElMessage.success('Deleted successfully')
        load()
      } else {
        ElMessage.error(res.data || 'Delete failed')
      }
    } catch (e) {
      ElMessage.error('Delete failed')
    }
  }).catch(() => {})
}

const getStatus = (row) => {
  if (!row.productionDate || !row.shelfLifeMonths) {
    return { text: '未知 N/A', type: 'info' }
  }
  
  const prodDate = dayjs(row.productionDate)
  const expireDate = prodDate.add(row.shelfLifeMonths, 'month')
  const now = dayjs()
  const diffDays = expireDate.diff(now, 'day')
  
  if (diffDays < 0) {
    return { text: '已过期 EXPIRED', type: 'danger' }
  } else if (diffDays <= 30) {
    return { text: '临期 EXPIRING', type: 'warning' }
  } else {
    return { text: '正常 NORMAL', type: 'success' }
  }
}

const getStatusClass = (row) => {
  const status = getStatus(row).text
  if (status.includes('EXPIRED')) return 'danger'
  if (status.includes('EXPIRING')) return 'warning'
  if (status.includes('NORMAL')) return 'success'
  return ''
}

onMounted(async () => {
  await loadProducts()
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

.product-name {
  font-size: 18px;
  font-weight: 600;
  letter-spacing: -0.5px;
}

.stock-info {
  font-family: 'Helvetica Neue', monospace;
  margin-bottom: 8px;
}

.stock-num {
  font-size: 24px;
  font-weight: 700;
}

.stock-num.low-stock {
  color: #ff3b30;
}

.warning-line {
  font-size: 12px;
  color: var(--w-text-gray);
}

.minimal-progress-bar {
  width: 100%;
  height: 2px;
  background-color: var(--w-border);
}

.minimal-progress-inner {
  height: 100%;
  background-color: var(--w-text);
  transition: width 0.3s ease;
}

.minimal-progress-inner.danger {
  background-color: #ff3b30;
}

.status-tags {
  display: flex;
  flex-direction: column;
  gap: 8px;
  align-items: flex-start;
}

.minimal-tag {
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1px;
  padding: 4px 8px;
  border: 1px solid var(--w-border);
}

.minimal-tag.danger {
  color: #ff3b30;
  border-color: #ff3b30;
}

.minimal-tag.warning {
  color: #ff9500;
  border-color: #ff9500;
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

.danger-btn {
  border-color: #ff3b30;
  color: #ff3b30;
}

.danger-btn:hover {
  background: #ff3b30;
  color: white;
}

.warning-btn {
  border-color: #ff9500;
  color: #ff9500;
}

.warning-btn:hover {
  background: #ff9500;
  color: white;
}
</style>