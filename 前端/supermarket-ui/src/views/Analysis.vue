<template>
  <div class="analysis-page page-container">
    <div class="page-header">
      <div class="header-left">
        <h2 class="display-title">
          <span class="cn-title">数据分析</span>
          <span class="en-title">/ Analysis.</span>
        </h2>
        <span class="sub-text">Sales, Trends & Staff Performance / 数据驱动决策</span>
      </div>
      <div class="header-right">
        <button class="minimal-btn" @click="initCharts">刷新数据 REFRESH</button>
      </div>
    </div>
    
    <div class="dashboard-grid">
      <!-- 销量排行图 -->
      <div class="minimal-card rank-card">
        <div class="card-header">
          <span class="card-title">商品销量 TOP 10 <span class="en-text">/ TOP PRODUCTS</span></span>
        </div>
        <div ref="rankChartRef" style="width: 100%; height: 350px;"></div>
      </div>

      <!-- 门店销售排行图 -->
      <div class="minimal-card store-card">
        <div class="card-header">
          <span class="card-title">门店销售额占比 <span class="en-text">/ STORE REVENUE</span></span>
        </div>
        <div ref="storeChartRef" style="width: 100%; height: 350px;"></div>
      </div>
      
      <!-- 区域热销偏好 -->
      <div class="minimal-card preference-card">
        <div class="card-header">
          <span class="card-title">区域热销偏好分析 <span class="en-text">/ REGION PREFERENCE</span></span>
        </div>
        <div ref="preferenceChartRef" style="width: 100%; height: 500px;"></div>
      </div>

      <!-- 🌟 新增：收银员排班与对账分析 🌟 -->
      <div class="minimal-card shift-card">
        <div class="card-header">
          <span class="card-title">收银员排班与财务对账 <span class="en-text">/ CASHIER SHIFT & AUDIT</span></span>
        </div>
        <div class="table-container" style="padding: 20px;">
          <el-table :data="shiftRecords" stripe style="width: 100%">
            <el-table-column prop="store_id" label="门店 / Store" width="100">
              <template #default="{ row }">
                <span class="id-text">店{{ row.store_id }}</span>
              </template>
            </el-table-column>
            
            <el-table-column prop="cashier_username" label="收银员 / Cashier" width="120">
              <template #default="{ row }">
                <span class="product-name">{{ row.cashier_username }}</span>
              </template>
            </el-table-column>

            <el-table-column label="工作时间 / Time" width="220">
              <template #default="{ row }">
                <div class="time-range">
                  <span class="mono-text">{{ dayjs(row.shift_start).format('MM.DD HH:mm') }}</span>
                  <span style="color: var(--w-text-gray); margin: 0 4px;">-</span>
                  <span class="mono-text">{{ row.shift_end ? dayjs(row.shift_end).format('HH:mm') : '进行中' }}</span>
                </div>
              </template>
            </el-table-column>

            <el-table-column prop="work_hours" label="工时 / Hours" width="100" align="center">
              <template #default="{ row }">
                <span class="mono-text" style="font-weight: 600;">{{ row.work_hours }} h</span>
              </template>
            </el-table-column>

            <el-table-column prop="total_orders" label="订单数 / Orders" width="120" align="center">
              <template #default="{ row }">
                <span class="mono-text">{{ row.total_orders || 0 }}</span>
              </template>
            </el-table-column>

            <el-table-column label="备用金 / Opening" width="120" align="right">
              <template #default="{ row }">
                <span class="price-text">¥ {{ row.opening_cash?.toFixed(2) }}</span>
              </template>
            </el-table-column>

            <el-table-column label="系统应收 / System" width="120" align="right">
              <template #default="{ row }">
                <span class="price-text">¥ {{ row.system_cash?.toFixed(2) || '0.00' }}</span>
              </template>
            </el-table-column>

            <el-table-column label="实际交班 / Closing" width="120" align="right">
              <template #default="{ row }">
                <span class="price-text" v-if="row.status === 'CLOSED'">¥ {{ row.closing_cash?.toFixed(2) }}</span>
                <span v-else class="mono-text" style="color: var(--w-text-gray)">-</span>
              </template>
            </el-table-column>

            <el-table-column label="对账差异 / Diff" min-width="120" align="right" fixed="right">
              <template #default="{ row }">
                <span v-if="row.status === 'CLOSED'" 
                      class="price-text" 
                      :class="{ 'diff-danger': row.diff_cash < 0, 'diff-success': row.diff_cash >= 0 }">
                  {{ row.diff_cash > 0 ? '+' : '' }}{{ row.diff_cash?.toFixed(2) }}
                </span>
                <span v-else class="minimal-tag warning">当班中 ACTIVE</span>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { getStoreRank, getProductRank, getPreferenceAnalysis, getShiftRecordAnalysis } from '@/api/analysis'
import dayjs from 'dayjs'

const rankChartRef = ref(null)
const storeChartRef = ref(null)
const preferenceChartRef = ref(null)

let rankChart = null
let storeChart = null
let preferenceChart = null

const shiftRecords = ref([])

const initCharts = async () => {
  if (!rankChart) rankChart = echarts.init(rankChartRef.value)
  if (!storeChart) storeChart = echarts.init(storeChartRef.value)
  if (!preferenceChart) preferenceChart = echarts.init(preferenceChartRef.value)

  try {
    // 并发请求所有图表和表格数据
    const [rankRes, storeRes, prefRes, shiftRes] = await Promise.all([
      getProductRank(),
      getStoreRank(),
      getPreferenceAnalysis(),
      getShiftRecordAnalysis()
    ])

    // 填充排班表数据
    shiftRecords.value = shiftRes.data || []

    const productData = rankRes.data || []
    const storeData = storeRes.data || []
    const prefData = prefRes.data || []

    // 极简黑白灰配色体系
    const wColors = ['#000000', '#333333', '#666666', '#999999', '#cccccc', '#eeeeee']

    // 1. 商品销量排行 (柱状图)
    rankChart.setOption({
      backgroundColor: 'transparent',
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: { 
        type: 'value',
        axisLine: { show: false },
        splitLine: { lineStyle: { type: 'dashed', color: '#eee' } }
      },
      yAxis: { 
        type: 'category', 
        data: productData.map(item => item.product_name).reverse(),
        axisLine: { lineStyle: { color: '#000' } }
      },
      series: [
        {
          name: '销量',
          type: 'bar',
          data: productData.map(item => item.total_quantity).reverse(),
          itemStyle: { color: '#000000' },
          barWidth: '40%'
        }
      ]
    })

    // 2. 门店销售占比 (饼图)
    storeChart.setOption({
      backgroundColor: 'transparent',
      tooltip: { trigger: 'item' },
      legend: { top: 'bottom', icon: 'circle' },
      color: wColors,
      series: [
        {
          name: '销售额',
          type: 'pie',
          radius: ['40%', '70%'],
          avoidLabelOverlap: false,
          itemStyle: {
            borderRadius: 0,
            borderColor: '#fff',
            borderWidth: 2
          },
          label: { show: false, position: 'center' },
          emphasis: {
            label: { show: true, fontSize: '20', fontWeight: 'bold' }
          },
          labelLine: { show: false },
          data: storeData.map(item => ({
            name: '门店 ' + item.store_id,
            value: item.total_sales
          }))
        }
      ]
    })

    // 3. 区域偏好分析 (雷达图)
    // 提取所有门店和所有品类
    const stores = [...new Set(prefData.map(item => '门店 ' + item.store_id))]
    const categories = [...new Set(prefData.map(item => item.category))]
    
    // 动态计算每个品类的最大值（加一点冗余，使图表更好看）
    const radarIndicator = categories.map(cat => {
      const maxVal = Math.max(...prefData.filter(item => item.category === cat).map(item => item.sales || 0), 10)
      return { name: cat, max: Math.ceil(maxVal * 1.2) }
    })
    
    const radarData = stores.map(storeName => {
      const storeId = storeName.replace('门店 ', '')
      const values = categories.map(cat => {
        const found = prefData.find(item => item.store_id == storeId && item.category === cat)
        return found ? found.sales : 0
      })
      return { name: storeName, value: values }
    })

    preferenceChart.setOption({
      backgroundColor: 'transparent',
      tooltip: { trigger: 'item' },
      legend: { data: stores, bottom: 0, icon: 'circle' },
      color: wColors,
      radar: {
        indicator: radarIndicator,
        radius: '65%', // 放大雷达图
        splitArea: { show: false },
        axisLine: { lineStyle: { color: '#ccc' } },
        splitLine: { lineStyle: { color: '#eee' } }
      },
      series: [
        {
          name: '区域偏好',
          type: 'radar',
          data: radarData,
          symbolSize: 6,
          lineStyle: { width: 2 },
          areaStyle: { opacity: 0.1 } // 增加一点透明填充色区分度
        }
      ]
    })

  } catch (e) {
    console.error('获取图表数据失败', e)
  }
}

const handleResize = () => {
  if (rankChart) rankChart.resize()
  if (storeChart) storeChart.resize()
  if (preferenceChart) preferenceChart.resize()
}

onMounted(() => {
  nextTick(() => {
    initCharts()
    window.addEventListener('resize', handleResize)
  })
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  if (rankChart) rankChart.dispose()
  if (storeChart) storeChart.dispose()
  if (preferenceChart) preferenceChart.dispose()
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
  margin-bottom: 40px;
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

.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 30px;
}

.minimal-card {
  background: transparent;
  border: 1px solid var(--w-border);
  display: flex;
  flex-direction: column;
}

.card-header {
  padding: 20px;
  border-bottom: 1px solid var(--w-border);
}

.card-title {
  font-size: 16px;
  font-weight: 700;
  letter-spacing: 1px;
}

.en-text {
  font-size: 12px;
  color: var(--w-text-gray);
  font-weight: 500;
}

.rank-card {
  grid-column: 1 / 2;
}

.store-card {
  grid-column: 2 / 3;
}

.preference-card {
  grid-column: 1 / 3;
}

.shift-card {
  grid-column: 1 / 3;
}

.id-text, .mono-text, .price-text {
  font-family: 'Helvetica Neue', monospace;
  font-size: 14px;
}

.product-name {
  font-weight: 600;
}

.diff-danger {
  color: #ff3b30;
  font-weight: 700;
}

.diff-success {
  color: #34c759;
  font-weight: 700;
}

.minimal-tag {
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1px;
  padding: 4px 8px;
  border: 1px solid var(--w-border);
}

.minimal-tag.warning {
  color: #ff9500;
  border-color: #ff9500;
}

@media (max-width: 1024px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
  .rank-card, .store-card, .preference-card, .shift-card {
    grid-column: 1 / -1;
  }
}
</style>