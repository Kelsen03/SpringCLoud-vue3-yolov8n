<template>
  <div class="transfer-page">
    <div class="page-header">
      <div class="header-left">
        <h2>库存调拨与补货</h2>
        <span class="sub-text">处理门店间的库存流动及总部补货业务</span>
      </div>
    </div>
    
    <div class="content-container">
      <el-card shadow="never" class="transfer-card">
        <el-tabs type="card" class="custom-tabs">
          <!-- Tab 1: 库存调拨 -->
          <el-tab-pane label="门店间调拨">
            <div class="form-wrapper">
              <div class="form-header">
                <h3>🔄 库存调拨</h3>
                <p>将库存从一个门店转移到另一个门店</p>
              </div>
              
              <el-form :model="transferForm" label-width="100px" label-position="top" size="large">
                <el-form-item label="商品ID">
                  <el-input v-model="transferForm.productId" placeholder="请输入商品ID">
                    <template #prefix>🏷️</template>
                  </el-input>
                </el-form-item>

                <div class="store-select-row">
                  <el-form-item label="调出门店" style="flex: 1">
                    <el-select v-model="transferForm.fromStore" placeholder="选择调出方" style="width: 100%">
                      <el-option label="门店1 (北京)" :value="1" />
                      <el-option label="门店2 (上海)" :value="2" />
                      <el-option label="门店3 (广州)" :value="3" />
                    </el-select>
                  </el-form-item>
                  
                  <div class="arrow-icon">➜</div>

                  <el-form-item label="调入门店" style="flex: 1">
                    <el-select v-model="transferForm.toStore" placeholder="选择调入方" style="width: 100%">
                      <el-option label="门店1 (北京)" :value="1" />
                      <el-option label="门店2 (上海)" :value="2" />
                      <el-option label="门店3 (广州)" :value="3" />
                    </el-select>
                  </el-form-item>
                </div>

                <el-form-item label="调拨数量">
                  <el-input-number v-model="transferForm.count" :min="1" style="width: 100%" />
                </el-form-item>

                <el-form-item style="margin-top: 30px">
                  <el-button type="primary" style="width: 100%" @click="handleTransfer">提交调拨申请</el-button>
                </el-form-item>
              </el-form>
            </div>
          </el-tab-pane>

          <!-- Tab 2: 门店补货 -->
          <el-tab-pane label="总部补货">
            <div class="form-wrapper">
              <div class="form-header">
                <h3>📦 总部补货</h3>
                <p>总部仓库直接向门店发货</p>
              </div>

              <el-alert
                title="补货操作将直接增加指定门店的库存数量。"
                type="success"
                show-icon
                :closable="false"
                style="margin-bottom: 20px"
              />

              <el-form :model="replenishForm" label-width="100px" label-position="top" size="large">
                <el-form-item label="商品ID">
                  <el-input v-model="replenishForm.productId" placeholder="请输入商品ID">
                    <template #prefix>🏷️</template>
                  </el-input>
                </el-form-item>

                <!-- 新增商品信息输入 -->
                <div class="new-product-box">
                  <div class="box-title">
                    <span>✨ 新商品信息</span>
                    <span class="box-subtitle">(仅新商品入库时填写)</span>
                  </div>
                  <div class="box-content">
                    <el-form-item label="商品名称" class="compact-form-item">
                      <el-input v-model="replenishForm.productName" placeholder="例如：可口可乐" />
                    </el-form-item>
                    <el-form-item label="商品类别" class="compact-form-item">
                      <el-select v-model="replenishForm.category" placeholder="请选择类别" style="width: 100%;">
                        <el-option label="饮料" value="饮料" />
                        <el-option label="食品" value="食品" />
                        <el-option label="生活用品" value="生活用品" />
                        <el-option label="其他" value="其他" />
                      </el-select>
                    </el-form-item>
                    <el-form-item label="生产日期" class="compact-form-item">
                      <el-date-picker 
                        v-model="replenishForm.productionDate" 
                        type="date" 
                        placeholder="选择日期" 
                        value-format="YYYY-MM-DD"
                        style="width: 100%;"
                      />
                    </el-form-item>
                  </div>
                </div>

                <div class="store-select-row">
                  <el-form-item label="补货门店" style="flex: 1">
                    <el-select 
                      v-model="replenishForm.storeId" 
                      placeholder="请选择 (支持多选)" 
                      style="width: 100%"
                      multiple
                      collapse-tags
                      collapse-tags-tooltip
                    >
                      <el-option label="门店1 (北京)" :value="1" />
                      <el-option label="门店2 (上海)" :value="2" />
                      <el-option label="门店3 (广州)" :value="3" />
                      <el-option label="全部门店" :value="-1" />
                    </el-select>
                  </el-form-item>

                  <el-form-item label="补货数量 (每店)" style="flex: 1; margin-left: 20px;">
                    <el-input-number v-model="replenishForm.count" :min="1" style="width: 100%" />
                  </el-form-item>
                </div>

                <el-form-item style="margin-top: 20px">
                  <el-button type="success" style="width: 100%" @click="handleReplenish">确认补货入库</el-button>
                </el-form-item>
              </el-form>
            </div>
          </el-tab-pane>
        </el-tabs>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { reactive, watch } from 'vue'
import { transferStock, replenishStock, replenishNewStock } from '@/api/inventory'
import { getProductById } from '@/api/product'
import { ElMessage, ElMessageBox } from 'element-plus'

// 调拨表单
const transferForm = reactive({
  productId: 1,
  fromStore: 1,
  toStore: 2,
  count: 10
})

// 补货表单 (升级版)
const replenishForm = reactive({
  productId: '',
  storeId: [1], // 默认为数组，方便多选
  count: 100,
  productName: '', // 新增商品名
  category: '',    // 新增类别
  productionDate: '' // 生产日期
})

// 防抖函数
const debounce = (fn, delay) => {
  let timer = null
  return (...args) => {
    if (timer) clearTimeout(timer)
    timer = setTimeout(() => fn(...args), delay)
  }
}

// 监听商品ID输入，自动填充信息或提示冲突（带防抖）
watch(() => replenishForm.productId, debounce(async (newVal) => {
  if (!newVal) return
  
  try {
    const res = await getProductById(newVal)
    const product = res.data
    
    // 再次检查当前输入框的值是否还是 newVal（防止网络延迟导致的旧结果覆盖新结果）
    // 注意：这里需要确保 replenishForm.productId 类型一致性
    if (String(replenishForm.productId) !== String(newVal)) return

    if (product) {
      // 如果商品已存在，自动填充名称
      replenishForm.productName = product.name
      // 提示用户
      ElMessage.info(`识别到已存在商品：${product.name}，将进行补货操作`)
    } else {
      // 如果是新ID（查不到商品），清空名称
      // 这样可以清除之前可能因误输入而自动填充的错误名称（例如 99 -> 鸡腿，变成 999 -> 空）
      replenishForm.productName = '' 
    }
  } catch (e) {
    // 查询出错或查不到，也视为新商品，清空名称
    replenishForm.productName = ''
  }
}, 500)) // 延迟 500ms 执行

// 处理调拨提交
const handleTransfer = async () => {
  if (transferForm.fromStore === transferForm.toStore) {
    ElMessage.warning('调出和调入门店不能相同')
    return
  }
  try {
    const res = await transferStock(transferForm)
    if (res.data === 'ok') {
      ElMessage.success('调拨成功')
    } else {
      ElMessage.error(res.data || '调拨失败')
    }
  } catch (e) {
    console.error(e)
  }
}

// 处理补货提交
const handleReplenish = async () => {
  if (replenishForm.count <= 0) {
    ElMessage.warning('补货数量必须大于0')
    return
  }
  if (!replenishForm.productId) {
    ElMessage.warning('请输入商品ID')
    return
  }
  
  // 处理多选逻辑
  let targetStores = []
  // 检查是否选择了“全部门店”
  if (replenishForm.storeId.includes(-1)) {
    targetStores = [1, 2, 3]
  } else {
    targetStores = replenishForm.storeId
  }

  if (!targetStores || targetStores.length === 0) {
    ElMessage.warning('请选择至少一个门店')
    return
  }
  
  // 批量执行补货
  let successCount = 0
  for (const sid of targetStores) {
    try {
      // 构造新接口参数
      const payload = {
        productId: Number(replenishForm.productId),
        storeId: sid,
        count: Number(replenishForm.count),
        productName: replenishForm.productName || undefined,
        category: replenishForm.category || undefined,
        productionDate: replenishForm.productionDate || undefined
      }

      const res = await replenishNewStock(payload)
      if (res.data === 'ok') {
        successCount++
      }
    } catch (e) {
      console.error(`门店${sid}补货失败`, e)
    }
  }

  if (successCount > 0) {
    ElMessage.success(`成功为 ${successCount} 个门店补货`)
    // 清空表单
    replenishForm.productId = ''
    replenishForm.productName = ''
    replenishForm.category = ''
    replenishForm.productionDate = ''
    replenishForm.count = 100
    // replenishForm.storeId 保持不变，方便连续操作
  } else {
    ElMessage.error('所有补货操作均失败')
  }
}
</script>

<style scoped>
.transfer-page {
  /* padding: 20px; */
}

.page-header {
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

.content-container {
  display: flex;
  justify-content: center;
}

.transfer-card {
  width: 800px;
  border: 1px solid #ebeef5;
  border-radius: 12px;
}

.form-wrapper {
  padding: 20px 40px;
}

.form-header {
  text-align: center;
  margin-bottom: 30px;
}

.form-header h3 {
  margin: 0 0 10px 0;
  font-size: 20px;
  color: #303133;
}

.form-header p {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.store-select-row {
  display: flex;
  align-items: center;
  gap: 20px;
}

.arrow-icon {
  font-size: 24px;
  color: #909399;
  margin-top: 10px;
}

.new-product-box {
  background: #fdf6ec;
  border: 1px dashed #e6a23c;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.box-title {
  margin-bottom: 15px;
  font-weight: bold;
  color: #e6a23c;
}

.box-subtitle {
  font-weight: normal;
  font-size: 12px;
  color: #909399;
  margin-left: 5px;
}

.box-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
}

.compact-form-item {
  margin-bottom: 0;
}
</style>