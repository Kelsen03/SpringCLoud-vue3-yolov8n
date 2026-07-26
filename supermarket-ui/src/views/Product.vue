<template>
  <div class="product-page page-container">
    <div class="page-header">
      <div class="header-left">
        <h2 class="display-title">
          <span class="cn-title">商品定价</span>
          <span class="en-title">/ Products.</span>
        </h2>
        <span class="sub-text">Management & Pricing</span>
      </div>
      <div class="header-right">
        <span class="role-indicator">{{ role === 'HQ' ? 'HQ Access' : 'Store View' }}</span>
      </div>
    </div>

    <div class="table-container">
      <el-table 
        :data="list" 
        stripe 
        style="width: 100%"
      >
        <el-table-column prop="id" label="编号 / ID" width="120" align="left">
          <template #default="{ row }">
            <span class="id-text">#{{ String(row.id).padStart(4, '0') }}</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="name" label="商品名称 / Name" min-width="200">
          <template #default="{ row }">
            <span class="product-name">{{ row.name }}</span>
          </template>
        </el-table-column>
        
        <el-table-column label="标准价格 / Standard Price" width="220" align="right">
          <template #default="{ row }">
            <div v-if="role === 'HQ'" class="minimal-input-wrapper">
              <span class="currency-symbol">¥</span>
              <input 
                type="number" 
                v-model="row.price" 
                class="minimal-input"
                step="0.1"
                min="0"
                :placeholder="row.price === 0 ? '0.00' : ''"
              />
            </div>
            <span v-else class="price-text">¥ {{ row.price.toFixed(2) }}</span>
          </template>
        </el-table-column>
        
        <el-table-column label="促销价格 / Promo Price" width="220" align="right">
          <template #default="{ row }">
            <div v-if="role === 'HQ'" class="minimal-input-wrapper">
              <span class="currency-symbol promo-symbol">¥</span>
              <input 
                type="number" 
                v-model="row.promoPrice" 
                class="minimal-input promo-input"
                step="0.1"
                min="0"
                placeholder="-"
              />
            </div>
            <span v-else class="price-text promo">
              {{ row.promoPrice ? '¥ ' + row.promoPrice.toFixed(2) : '-' }}
            </span>
          </template>
        </el-table-column>
        
        <el-table-column v-if="role === 'HQ'" label="操作 / Action" width="180" align="right">
          <template #default="{ row }">
            <button class="minimal-btn" @click="save(row)">
              {{ row.price === 0 ? '初始化 INIT' : '保存 SAVE' }}
            </button>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { getProductList, updateProduct } from '@/api/product'
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

const list = ref([])
const role = localStorage.getItem('role')

const load = async () => {
  try {
    const res = await getProductList()
    list.value = res.data || []
  } catch (e) {
    console.error('加载商品列表失败', e)
    ElMessage.error('Failed to load products')
  }
}

const save = async (row) => {
  try {
    await updateProduct(row)
    row.isNew = false
    ElMessage.success('Price updated')
  } catch (e) {
    ElMessage.error('Update failed')
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

.role-indicator {
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1px;
  padding: 8px 16px;
  border: 1px solid var(--w-text);
}

.id-text {
  font-family: 'Helvetica Neue', monospace;
  color: var(--w-text-gray);
  font-size: 14px;
}

.product-name {
  font-size: 18px;
  font-weight: 600;
  letter-spacing: -0.5px;
}

.price-text {
  font-family: 'Helvetica Neue', monospace;
  font-size: 16px;
  font-weight: 500;
}

.price-text.promo {
  color: #ff3b30;
}

/* 极简输入框 */
.minimal-input-wrapper {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  border-bottom: 1px solid var(--w-border);
  transition: border-color 0.3s ease;
}

.minimal-input-wrapper:focus-within {
  border-color: var(--w-text);
}

.currency-symbol {
  font-size: 14px;
  color: var(--w-text-gray);
  margin-right: 8px;
}

.promo-symbol {
  color: #ff3b30;
  opacity: 0.5;
}

.minimal-input {
  width: 80px;
  border: none;
  background: transparent;
  font-family: 'Helvetica Neue', monospace;
  font-size: 16px;
  font-weight: 500;
  text-align: right;
  padding: 8px 0;
  outline: none;
  color: var(--w-text);
}

.minimal-input.promo-input {
  color: #ff3b30;
}

/* 去除输入框上下箭头 */
.minimal-input::-webkit-outer-spin-button,
.minimal-input::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

.minimal-btn {
  background: transparent;
  border: 1px solid var(--w-text);
  color: var(--w-text);
  padding: 8px 24px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1px;
  transition: all 0.3s ease;
}

.minimal-btn:hover {
  background: var(--w-text);
  color: var(--w-bg);
}
</style>