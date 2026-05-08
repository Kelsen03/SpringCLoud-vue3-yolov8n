<template>
  <div class="product-page">
    <div class="page-header">
      <div class="header-left">
        <h2>商品定价与促销</h2>
        <span class="sub-text">管理全店商品价格策略</span>
      </div>
      <div class="header-right">
        <el-tag v-if="role === 'HQ'" type="success" effect="dark" size="large">总部权限</el-tag>
        <el-tag v-else type="warning" effect="dark" size="large">门店视图</el-tag>
      </div>
    </div>

    <el-card shadow="never" class="table-card">
      <el-table 
        :data="list" 
        border 
        stripe 
        highlight-current-row
        :header-cell-style="{ background: '#f5f7fa', color: '#606266', fontWeight: 'bold' }"
        style="width: 100%"
      >
        <el-table-column prop="id" label="商品编号" width="100" align="center">
          <template #default="{ row }">
            <el-tag type="info">{{ row.id }}</el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="name" label="商品名称" min-width="150">
          <template #default="{ row }">
            <span style="font-weight: 500">{{ row.name }}</span>
          </template>
        </el-table-column>
        
        <el-table-column label="标准价格 (￥)" width="180" align="center">
          <template #default="{ row }">
            <div v-if="role === 'HQ'" class="price-input-wrapper">
              <el-input-number 
                v-model="row.price" 
                :precision="2" 
                :step="0.1" 
                :min="0"
                controls-position="right"
                size="default"
                style="width: 100%"
                :placeholder="row.price === 0 ? '设置价格' : ''"
              />
            </div>
            <span v-else class="price-text">￥{{ row.price.toFixed(2) }}</span>
          </template>
        </el-table-column>
        
        <el-table-column label="促销价格 (￥)" width="180" align="center">
          <template #default="{ row }">
            <div v-if="role === 'HQ'" class="price-input-wrapper">
              <el-input-number 
                v-model="row.promoPrice" 
                :precision="2" 
                :step="0.1" 
                :min="0"
                controls-position="right"
                size="default"
                style="width: 100%"
              />
            </div>
            <span v-else class="price-text promo">
              {{ row.promoPrice ? '￥' + row.promoPrice.toFixed(2) : '-' }}
            </span>
          </template>
        </el-table-column>
        
        <el-table-column v-if="role === 'HQ'" label="操作" width="120" align="center" fixed="right">
          <template #default="{ row }">
            <el-button 
              type="primary" 
              size="small" 
              @click="save(row)" 
              plain
            >
              {{ row.price === 0 ? '初始化' : '保存修改' }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { getProductList, updateProduct } from '@/api/product'
import { getInventoryList } from '@/api/inventory'
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

const list = ref([])
const role = localStorage.getItem('role')
const storeId = Number(localStorage.getItem('storeId')) || 1

const load = async () => {
  try {
    const res = await getProductList()
    let products = res.data || []

    // 只有HQ才需要检查所有门店的库存，找出未定价的新商品
    // 门店用户只能看到已存在的商品(由HQ统一定价)
    if (role === 'HQ') {
      try {
        // 遍历所有门店(1,2,3)的库存，查找遗漏的商品
        const storeIds = [1, 2, 3]
        const allInventoryItems = []
        
        for (const sid of storeIds) {
          try {
            const invRes = await getInventoryList(sid)
            if (invRes.data) {
              allInventoryItems.push(...invRes.data)
            }
          } catch (err) {
            console.warn(`加载门店${sid}库存失败`, err)
          }
        }
        
        // 使用 String 类型进行比较，防止 ID 类型不一致导致重复添加
        const productIds = new Set(products.map(p => String(p.id)))
        
        allInventoryItems.forEach(item => {
          if (item.productId && !productIds.has(String(item.productId))) {
            // 如果库存中有，但商品列表中没有，手动添加供HQ定价
            products.push({
              id: item.productId,
              name: item.productName || '未命名商品',
              price: 0, // 默认为0，等待HQ设置
              promoPrice: null,
              isNew: true // 标记为新发现的库存商品
            })
            productIds.add(String(item.productId))
          }
        })
      } catch (invError) {
        console.warn('获取库存补充数据失败', invError)
      }
    }

    list.value = products
  } catch (e) {
    console.error('加载商品列表失败', e)
    ElMessage.error('加载失败')
  }
}

const save = async (row) => {
  try {
    await updateProduct(row)
    ElMessage.success('价格修改成功')
    // 如果是新商品，保存后它应该就真正存在了，重新加载列表
    load()
  } catch (e) {
    ElMessage.error('修改失败')
  }
}

onMounted(() => {
  load()
})
</script>

<style scoped>
.product-page {
  /* padding: 20px; 已由外层 content-wrapper 提供 padding，这里不再需要 */
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #ebeef5;
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

.table-card {
  border: 1px solid #ebeef5;
  border-radius: 8px;
}

.price-text {
  font-family: Monaco, monospace;
  font-weight: bold;
  color: #606266;
}

.price-text.promo {
  color: #f56c6c;
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
  
  .header-right {
    width: 100%;
    display: flex;
    justify-content: flex-end;
  }
  
  /* 表格内边距调整 */
  :deep(.el-table .cell) {
    padding: 0 8px;
  }
}
</style>