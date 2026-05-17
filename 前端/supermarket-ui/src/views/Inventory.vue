<template>
  <div class="inventory-page">
    <div class="page-header">
      <div class="header-left">
        <h2>门店库存监控</h2>
        <span class="sub-text">实时监控各门店商品库存状态及效期</span>
      </div>
      <div class="header-right">
        <div class="filter-bar">
          <span class="label">当前查看：</span>
          <el-select v-model="storeId" @change="load" size="large" style="width: 180px">
            <template #prefix>🏪</template>
            <el-option label="门店 1 (北京)" :value="1" />
            <el-option label="门店 2 (上海)" :value="2" />
            <el-option label="门店 3 (广州)" :value="3" />
          </el-select>
        </div>
      </div>
    </div>

    <el-card shadow="never" class="table-card">
      <el-table 
        :data="list" 
        border 
        stripe
        :header-cell-style="{ background: '#f5f7fa', color: '#606266', fontWeight: 'bold' }"
        style="width: 100%"
      >
        <el-table-column prop="productId" label="ID" width="80" align="center">
          <template #default="{ row }">
            <span style="color: #909399;">#{{ row.productId }}</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="productName" label="商品名称" min-width="160">
          <template #default="{ row }">
            <span style="font-weight: 500; color: #303133;">{{ row.productName }}</span>
          </template>
        </el-table-column>
        
        <el-table-column label="库存情况" width="180">
          <template #default="{ row }">
            <div class="stock-info">
              <span class="stock-num" :class="{ 'low-stock': row.stock <= row.warningStock }">
                {{ row.stock }}
              </span>
              <span class="warning-line"> / 预警: {{ row.warningStock }}</span>
            </div>
            <el-progress 
              :percentage="Math.min((row.stock / (row.warningStock * 3)) * 100, 100)" 
              :status="row.stock <= row.warningStock ? 'exception' : 'success'"
              :show-text="false"
              :stroke-width="6"
              style="margin-top: 5px;"
            />
          </template>
        </el-table-column>
        
        <el-table-column prop="productionDate" label="生产日期" width="140" align="center">
          <template #default="{ row }">
            <el-tag type="info" effect="plain" size="small">
              {{ row.productionDate ? dayjs(row.productionDate).format('YYYY-MM-DD') : '-' }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="shelfLifeMonths" label="保质期" width="100" align="center">
          <template #default="{ row }">
            {{ row.shelfLifeMonths }} 个月
          </template>
        </el-table-column>

        <!-- 缺货状态 -->
        <el-table-column label="状态标签" width="220">
          <template #default="scope">
            <div style="display: flex; gap: 8px; flex-wrap: wrap;">
              <!-- 库存预警 -->
              <el-tag
                v-if="scope.row.stock <= scope.row.warningStock"
                type="danger"
                effect="dark"
                round
              >
                ⚠️ 缺货预警
              </el-tag>
              
              <!-- 效期状态 -->
              <el-tag
                :type="getStatus(scope.row).type"
                effect="dark"
                round
              >
                {{ getStatus(scope.row).text === '已过期' ? '🚫' : (getStatus(scope.row).text === '临期预警' ? '⏳' : '✅') }}
                {{ getStatus(scope.row).text }}
              </el-tag>

              <el-tag 
                v-if="scope.row.stock > scope.row.warningStock && getStatus(scope.row).text === '正常'" 
                type="success" 
                effect="light"
                round
              >
                ✅ 库存正常
              </el-tag>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="130" align="center" fixed="right">
          <template #default="scope">
            <template v-if="role === 'HQ' || (role === 'STORE' && Number(storeId) === currentStoreId)">
              <el-popconfirm title="将库存清零，保留商品记录？" confirm-button-text="清零" cancel-button-text="取消" @confirm="handleClear(scope.row)">
                <template #reference>
                  <el-button type="warning" link size="small">清零</el-button>
                </template>
              </el-popconfirm>
              <el-popconfirm title="确定删除该库存记录？" confirm-button-text="删除" cancel-button-text="取消" @confirm="handleDelete(scope.row)">
                <template #reference>
                  <el-button type="danger" link size="small">删除</el-button>
                </template>
              </el-popconfirm>
            </template>
            <el-tag v-else type="info" size="small">仅查看</el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getInventoryList, deleteInventory, clearInventory } from '@/api/inventory'
import { getProductList } from '@/api/product'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'

const userStoreId = Number(localStorage.getItem('storeId'))
// 如果没有获取到 storeId，默认为 1 (兼容旧逻辑，避免所有人都无法操作)
const currentStoreId = ref(userStoreId || 1) 
const storeId = ref(currentStoreId.value) // 默认查看自己的门店
const role = ref(localStorage.getItem('role')) // 获取当前角色
const list = ref([])
const productMap = ref({}) // 商品ID -> 商品信息的映射

// 获取所有商品信息，建立ID到名称的映射
const loadProducts = async () => {
  try {
    const res = await getProductList()
    if (res.data) {
      res.data.forEach(p => {
        productMap.value[p.id] = p.name
      })
    }
  } catch (e) {
    console.error('加载商品列表失败', e)
  }
}

// 状态计算辅助函数
const getStatus = (row) => {
  if (!row.productionDate || !row.shelfLifeMonths) return { text: '未知', type: 'info' }
  
  const today = dayjs()
  const prodDate = dayjs(row.productionDate)
  const expireDate = prodDate.add(row.shelfLifeMonths, 'month')
  
  if (expireDate.isBefore(today)) {
    return { text: '已过期', type: 'danger' }
  }
  
  // 临期判断：剩余保质期 < 45天
  const daysLeft = expireDate.diff(today, 'day')
  if (daysLeft < 45) {
    return { text: '临期预警', type: 'warning' }
  }
  
  return { text: '正常', type: 'success' }
}

// 保持原有的isExpiring函数兼容性
const isExpiring = (row) => {
  const status = getStatus(row)
  return status.text === '临期预警' || status.text === '已过期'
}

// 清零库存
const handleClear = async (row) => {
  try {
    const res = await clearInventory(storeId.value, row.productId)
    if (res.data === 'ok') {
      ElMessage.success('库存已清零')
      load()
    } else {
      ElMessage.error(res.data || '清零失败')
    }
  } catch (e) { console.error(e) }
}

// 删除库存
const handleDelete = async (row) => {
  try {
    const res = await deleteInventory(storeId.value, row.productId)
    if (res.data === 'ok') {
      ElMessage.success('删除成功')
      load() // 刷新列表
    } else {
      ElMessage.error(res.data || '删除失败')
    }
  } catch (e) {
    console.error(e)
  }
}

const load = async () => {
  try {
    const res = await getInventoryList(storeId.value)
    list.value = res.data
  } catch (e) {
    console.error(e)
  }
}

onMounted(async () => {
  await loadProducts() // 先加载商品信息
  await load()         // 再加载库存
})
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-left h2 {
  margin: 0;
  font-size: 24px;
  color: #303133;
}

.sub-text {
  font-size: 13px;
  color: #909399;
  margin-top: 5px;
  display: block;
}

.filter-bar {
  display: flex;
  align-items: center;
  background: #fff;
  padding: 5px 10px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.label {
  font-size: 14px;
  color: #606266;
  margin-right: 10px;
}

.table-card {
  border: none;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}

.stock-info {
  display: flex;
  align-items: baseline;
}

.stock-num {
  font-size: 16px;
  font-weight: bold;
  color: #67C23A;
}

.stock-num.low-stock {
  color: #F56C6C;
}

.warning-line {
  font-size: 12px;
  color: #909399;
  margin-left: 5px;
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
  
  .header-right {
    width: 100%;
  }
  
  .filter-bar {
    width: 100%;
    justify-content: space-between;
  }
  
  .label {
    white-space: nowrap;
  }
}
</style>