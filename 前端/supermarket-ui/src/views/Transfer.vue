<template>
  <div class="transfer-page">
    <div class="page-header">
      <div class="header-left">
        <h2 class="display-title">
          <span class="cn-title">{{ role === 'HQ' ? '库存调拨' : '店间借货' }}</span>
          <span class="en-title">/ Transfer.</span>
        </h2>
        <span class="sub-text">{{ role === 'HQ' ? '处理门店间的库存流动及总部补货业务' : '向其他门店发起借货请求或处理来自其他门店的借货申请' }}</span>
      </div>
    </div>
    
    <div class="content-container">
      <el-card shadow="never" class="transfer-card">
        <el-tabs type="card" class="custom-tabs" @tab-click="handleTabClick">
          
          <el-tab-pane :label="role === 'HQ' ? '直接调拨 (HQ) / Transfer' : '发起借货申请 / Request'">
            <div class="form-wrapper">
              <div class="form-header">
                <h3>🔄 {{ role === 'HQ' ? '库存直接调拨 / DIRECT TRANSFER' : '发起借货请求 / REQUEST STOCK' }}</h3>
                <p>{{ role === 'HQ' ? '直接将库存从一个门店转移到另一个门店' : '请求其他门店将库存调拨至本店' }}</p>
              </div>
              
              <el-form :model="transferForm" label-width="120px" label-position="top" size="large">
                <el-form-item label="商品ID / Product ID">
                  <el-input v-model="transferForm.productId" placeholder="请输入商品ID">
                    <template #prefix>🏷️</template>
                  </el-input>
                </el-form-item>

                <div class="store-select-row">
                  <el-form-item :label="role === 'HQ' ? '调出门店 / From' : '被借方 / From'" style="flex: 1">
                    <el-select v-model="transferForm.fromStore" placeholder="选择出货方" style="width: 100%">
                      <el-option label="门店1 (BJ)" :value="1" :disabled="role === 'STORE' && currentStoreId === 1" />
                      <el-option label="门店2 (SH)" :value="2" :disabled="role === 'STORE' && currentStoreId === 2" />
                      <el-option label="门店3 (GZ)" :value="3" :disabled="role === 'STORE' && currentStoreId === 3" />
                    </el-select>
                  </el-form-item>
                  
                  <div class="arrow-icon">➜</div>

                  <el-form-item :label="role === 'HQ' ? '调入门店 / To' : '调入本门店 / To'" style="flex: 1">
                    <el-select v-model="transferForm.toStore" placeholder="选择调入方" style="width: 100%" :disabled="role === 'STORE'">
                      <el-option label="门店1 (BJ)" :value="1" />
                      <el-option label="门店2 (SH)" :value="2" />
                      <el-option label="门店3 (GZ)" :value="3" />
                    </el-select>
                  </el-form-item>
                </div>

                <el-form-item label="调拨数量 / Quantity">
                  <el-input-number v-model="transferForm.count" :min="1" style="width: 100%" />
                </el-form-item>

                <el-form-item style="margin-top: 30px">
                  <el-button type="primary" style="width: 100%" @click="handleTransfer">
                    {{ role === 'HQ' ? '强制提交调拨 / FORCE TRANSFER' : '提交借货申请 / SUBMIT REQUEST' }}
                  </el-button>
                </el-form-item>
              </el-form>
            </div>
          </el-tab-pane>

          <el-tab-pane label="总部补货 / Replenish" v-if="role === 'HQ'">
            <div class="form-wrapper">
              <div class="form-header"><h3>总部补货 / REPLENISH</h3><p>选择商品，指定门店与数量，一键补货入库</p></div>

              <el-form :model="replenishForm" label-width="120px" label-position="top" size="large">

                <el-row :gutter="12">
                  <el-col :span="12">
                    <el-form-item label="选择商品 / Select Product">
                      <el-select v-model="replenishForm.productId" filterable placeholder="搜索商品名称或条形码" style="width:100%">
                        <el-option v-for="p in productList" :key="p.id" :label="(p.barcode||'') + ' ' + p.name" :value="p.id">
                          <span>{{ p.name }}</span>
                          <span style="float:right;color:#909399;font-size:12px">{{ p.category||'未分类' }}</span>
                        </el-option>
                      </el-select>
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item label="商品名称 / Product Name">
                      <el-input v-model="replenishForm.productName" placeholder="自动填充或手动输入新商品名" />
                    </el-form-item>
                  </el-col>
                </el-row>

                <el-row :gutter="12">
                  <el-col :span="8">
                    <el-form-item label="商品类别 / Category">
                      <el-select v-model="replenishForm.category" placeholder="选择类别" style="width:100%" filterable>
                        <el-option v-for="c in CATEGORIES" :key="c" :label="c" :value="c" />
                      </el-select>
                    </el-form-item>
                  </el-col>
                  <el-col :span="8">
                    <el-form-item label="保质期(月) / Shelf Life">
                      <el-input-number v-model="replenishForm.shelfLifeMonths" :min="1" :max="60" style="width:100%" />
                    </el-form-item>
                  </el-col>
                  <el-col :span="8">
                    <el-form-item label="生产日期 / Prod Date">
                      <el-date-picker v-model="replenishForm.productionDate" type="date" value-format="YYYY-MM-DD" style="width:100%" />
                    </el-form-item>
                  </el-col>
                </el-row>

                <el-row :gutter="12">
                  <el-col :span="12">
                    <el-form-item label="补货门店 / Stores">
                      <el-select v-model="replenishForm.storeId" multiple collapse-tags placeholder="选择门店" style="width:100%">
                        <el-option label="旗舰店（门店1）" :value="1" />
                        <el-option label="社区店（门店2）" :value="2" />
                        <el-option label="生鲜店（门店3）" :value="3" />
                        <el-option label="全部门店" :value="-1" />
                      </el-select>
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item label="补货数量 / Qty (per store)">
                      <el-input-number v-model="replenishForm.count" :min="1" :max="9999" style="width:100%" />
                    </el-form-item>
                  </el-col>
                </el-row>

                <el-button type="success" style="width:100%;margin-top:12px;height:44px;font-size:16px" @click="handleReplenish">确认补货入库 / REPLENISH</el-button>
              </el-form>

              <!-- 智能补货推荐 -->
              <el-divider />
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px">
                <h4 style="margin:0">智能补货推荐 / Smart Replenishment Recommend</h4>
                <el-button size="small" type="primary" @click="loadRecommend">刷新推荐 / Refresh</el-button>
              </div>
              <el-table :data="recommendList" border stripe size="small" max-height="300">
                <el-table-column label="商品名 / Product" min-width="120">
                  <template #default="{row}">
                    <span>{{ row.product_name }}</span>
                    <el-tag v-if="row.days_to_expire < 30" type="warning" size="small" style="margin-left:4px">临期{{ row.days_to_expire }}天</el-tag>
                  </template>
                </el-table-column>
                <el-table-column label="门店 / Store" width="90">
                  <template #default="{row}">{{ ['','旗舰店','社区店','生鲜店'][row.store_id]||row.store_id }}</template>
                </el-table-column>
                <el-table-column prop="stock" label="库存 / Stock" width="80" />
                <el-table-column prop="daily_sales" label="日均销量 / Daily" width="100" />
                <el-table-column label="建议补货 / Advise" width="120">
                  <template #default="{row}">
                    <span :style="{color:row.recommend_qty>0?'#f56c6c':'#67c23a',fontWeight:'bold'}">
                      {{ row.recommend_qty > 0 ? '+' + row.recommend_qty : '充足' }}
                    </span>
                  </template>
                </el-table-column>
                <el-table-column label="操作 / Action" width="100">
                  <template #default="{row}">
                    <el-button v-if="row.recommend_qty>0" size="small" type="primary" @click="quickReplenish(row)">补货 / Rep</el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </el-tab-pane>

          <el-tab-pane label="调拨单记录与审批 / Records & Approvals">
            <div class="list-wrapper" style="padding: 20px;">
              <el-button type="primary" plain @click="fetchTransferList" style="margin-bottom: 15px;">刷新列表 / REFRESH</el-button>
              <el-table :data="transferList" border stripe>
                <el-table-column prop="id" label="单号 / ID" width="100" />
                <el-table-column prop="createTime" label="时间 / Time" width="200" />
                <el-table-column prop="productId" label="商品ID / Product" width="120" />
                <el-table-column label="方向 / Direction" min-width="150">
                  <template #default="{ row }">
                    店{{ row.fromStore }} ➜ 店{{ row.toStore }}
                  </template>
                </el-table-column>
                <el-table-column prop="quantity" label="数量 / Qty" width="100" />
                <el-table-column prop="status" label="状态 / Status" min-width="150">
                  <template #default="{ row }">
                    <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
                  </template>
                </el-table-column>
                <el-table-column label="操作 / Action" width="200" fixed="right" align="center">
                  <template #default="{ row }">
                    <div v-if="row.status === 'PENDING' && (role === 'HQ' || currentStoreId === row.fromStore)">
                      <el-button size="small" type="success" @click="handleApprove(row.id)">同意 / YES</el-button>
                      <el-button size="small" type="danger" @click="handleReject(row.id)">拒绝 / NO</el-button>
                    </div>
                    <span v-else-if="row.status === 'PENDING' && currentStoreId === row.toStore" style="color:#909399; font-size:12px;">
                      等待审批 PENDING
                    </span>
                    <span v-else style="color:#c0c4cc; font-size:12px;">-</span>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </el-tab-pane>

        </el-tabs>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { reactive, watch, ref, onMounted } from 'vue'
import { transferStock, replenishNewStock, requestTransfer, approveTransfer, rejectTransfer, getTransferList } from '@/api/inventory'
import { getProductList } from '@/api/product'
import { getReplenishRecommend } from '@/api/analysis'
import { ElMessage, ElMessageBox } from 'element-plus'

const role = ref(localStorage.getItem('role'))
const currentStoreId = Number(localStorage.getItem('storeId')) || 1

const transferForm = reactive({
  productId: 1,
  fromStore: role.value === 'STORE' ? (currentStoreId === 1 ? 2 : 1) : 1, // 如果是STORE，默认被借方不是自己
  toStore: role.value === 'STORE' ? currentStoreId : 2, // 如果是STORE，借入方永远是自己
  count: 10
})

const replenishForm = reactive({
  productId: '',
  storeId: [1],
  count: 50,
  productName: '',
  category: '',
  productionDate: new Date().toISOString().slice(0,10),
  shelfLifeMonths: 12
})

const productList = ref([])
const transferList = ref([])
const recommendList = ref([])

const loadRecommend = async () => {
  try {
    const res = await getReplenishRecommend()
    recommendList.value = (res.data || []).filter(r => r.recommend_qty > 0 || r.stock <= r.warning_stock)
  } catch(_){}
}

/** 快速补货：点击推荐列表的补货按钮 */
const quickReplenish = (row) => {
  replenishForm.productId = String(row.product_id)
  replenishForm.productName = row.product_name || ''
  replenishForm.category = ''
  replenishForm.storeId = [row.store_id]
  replenishForm.count = Math.max(row.recommend_qty, 10)
  replenishForm.productionDate = new Date().toISOString().slice(0,10)
  replenishForm.shelfLifeMonths = 12
  ElMessage.success(`已填入: ${row.product_name} → 门店${row.store_id} +${replenishForm.count}`)
}

// 品类→保质期映射
const SHELF_LIFE_MAP = {
  '烘焙面点':1,'乳制品':6,'饮品':9,'冷冻食品':9,'方便食品':9,
  '零食':12,'谷物早餐':12,'宠物食品':12,'主食粮谷':18,'干货特产':18,
  '母婴用品':18,'调味品':24,'罐头食品':24,'纸品个护':36,'家居清洁':36,'日杂百货':36,'酒类':36
}
const CATEGORIES = Object.keys(SHELF_LIFE_MAP)

// 选品类自动填保质期
watch(() => replenishForm.category, (cat) => {
  if (cat && SHELF_LIFE_MAP[cat]) replenishForm.shelfLifeMonths = SHELF_LIFE_MAP[cat]
})

onMounted(async () => {
  try {
    const res = await getProductList()
    productList.value = Array.isArray(res.data) ? res.data : []
  } catch(_){}
  loadRecommend()
})

const debounce = (fn, delay) => {
  let timer = null
  return (...args) => {
    if (timer) clearTimeout(timer)
    timer = setTimeout(() => fn(...args), delay)
  }
}

// 选商品自动填信息
watch(() => replenishForm.productId, (newVal) => {
  if (!newVal) return
  const p = productList.value.find(x => String(x.id) === String(newVal))
  if (p) {
    replenishForm.productName = p.name
    replenishForm.category = p.category || ''
  }
})

const handleTransfer = async () => {
  if (transferForm.fromStore === transferForm.toStore) {
    ElMessage.warning('调出和调入门店不能相同')
    return
  }
  try {
    let res;
    if (role.value === 'HQ') {
      res = await transferStock(transferForm)
    } else {
      res = await requestTransfer(transferForm)
    }
    
    if (res.data === 'ok') {
      ElMessage.success(role.value === 'HQ' ? '调拨成功' : '借货申请已发送，等待对方审批')
    } else {
      ElMessage.error(res.data || '操作失败')
    }
  } catch (e) {
    console.error(e)
  }
}

const handleReplenish = async () => {
  if (replenishForm.count <= 0) {
    ElMessage.warning('补货数量必须大于0')
    return
  }
  if (!replenishForm.productId) {
    ElMessage.warning('请输入商品ID')
    return
  }
  
  let targetStores = []
  if (replenishForm.storeId.includes(-1)) {
    targetStores = [1, 2, 3]
  } else {
    targetStores = replenishForm.storeId
  }

  if (!targetStores || targetStores.length === 0) {
    ElMessage.warning('请选择至少一个门店')
    return
  }
  
  let successCount = 0
  for (const sid of targetStores) {
    try {
      const payload = {
        productId: Number(replenishForm.productId),
        storeId: sid,
        count: Number(replenishForm.count),
        productName: replenishForm.productName || undefined,
        category: replenishForm.category || undefined,
        productionDate: replenishForm.productionDate || undefined,
        shelfLifeMonths: replenishForm.shelfLifeMonths || 12
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
    replenishForm.productId = ''
    replenishForm.productName = ''
    replenishForm.category = ''
    replenishForm.productionDate = ''
    replenishForm.count = 100
    loadRecommend()
  } else {
    ElMessage.error('所有补货操作均失败')
  }
}

const fetchTransferList = async () => {
  try {
    const res = await getTransferList(role.value === 'HQ' ? null : currentStoreId)
    transferList.value = res.data || []
  } catch (e) {
    console.error(e)
  }
}

const handleApprove = async (id) => {
  try {
    const res = await approveTransfer(id)
    if (res.data === 'ok') {
      ElMessage.success('已同意借货')
      fetchTransferList()
    } else {
      ElMessage.error(res.data || '审批失败')
    }
  } catch (e) {
    console.error(e)
  }
}

const handleReject = async (id) => {
  try {
    const res = await rejectTransfer(id)
    if (res.data === 'ok') {
      ElMessage.success('已拒绝借货')
      fetchTransferList()
    } else {
      ElMessage.error(res.data || '操作失败')
    }
  } catch (e) {
    console.error(e)
  }
}

const handleTabClick = (tab) => {
  // tab.props.label 包含了中英文，我们需要使用 includes 进行模糊匹配
  if (tab.props.label && tab.props.label.includes('调拨单记录与审批')) {
    fetchTransferList()
  }
}

const getStatusType = (status) => {
  if (status === 'PENDING') return 'warning'
  if (status === 'APPROVED') return 'success'
  if (status === 'REJECTED') return 'danger'
  if (status === 'COMPLETED') return 'success'
  return 'info'
}

const getStatusText = (status) => {
  if (status === 'PENDING') return '待审批'
  if (status === 'APPROVED') return '已同意'
  if (status === 'REJECTED') return '已拒绝'
  if (status === 'COMPLETED') return '已完成'
  return status
}

onMounted(() => {
  // 如果默认就在列表Tab，可以加载一次
  // fetchTransferList()
})
</script>

<style scoped>
.transfer-page {
  /* padding: 20px; */
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
  width: 100%; /* 将固定宽度改为100%填满容器 */
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