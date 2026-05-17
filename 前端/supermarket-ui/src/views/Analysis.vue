<template>
  <div class="analysis-page">
    <div class="page-header">
      <div class="header-left">
        <h2>数据分析看板</h2>
        <span class="sub-text">多维度展示销售与库存数据趋势</span>
      </div>
      <div class="header-right">
        <el-button type="primary" plain size="small" @click="initCharts">🔄 刷新数据</el-button>
      </div>
    </div>
    
    <div class="dashboard-grid">
      <!-- 销量排行图 -->
      <el-card shadow="hover" class="chart-card rank-card">
        <template #header>
          <div class="card-header">
            <span>🔥 商品销量 TOP 10</span>
          </div>
        </template>
        <div ref="rankChartRef" style="width: 100%; height: 350px;"></div>
      </el-card>

      <!-- 门店销售排行图 -->
      <el-card shadow="hover" class="chart-card store-card">
        <template #header>
          <div class="card-header">
            <span>🏪 门店销售额占比</span>
          </div>
        </template>
        <div ref="storeChartRef" style="width: 100%; height: 350px;"></div>
      </el-card>
      
      <!-- 区域热销偏好 -->
      <el-card shadow="hover" class="chart-card preference-card">
        <template #header>
          <div class="card-header">
            <span>📊 区域/品类热销偏好分析</span>
          </div>
        </template>
        <div ref="preferenceChartRef" style="width: 100%; height: 400px;"></div>
      </el-card>

      <!-- 补货清单 -->
      <el-card shadow="hover" class="chart-card replenish-card">
        <template #header>
          <div class="card-header" style="display:flex;justify-content:space-between;align-items:center">
            <span>补货清单</span>
            <div style="display:flex;gap:8px">
              <el-select v-model="replenishStore" placeholder="全部门店" clearable size="small" style="width:140px" @change="loadReplenish">
                <el-option label="旗舰店" :value="1" />
                <el-option label="社区店" :value="2" />
                <el-option label="生鲜店" :value="3" />
              </el-select>
              <el-button type="success" size="small" @click="exportReplenish">导出Excel</el-button>
            </div>
          </div>
        </template>
        <div class="replenish-stats" v-if="replenishStats">
          <span>本月补货 {{ replenishStats.total }} 次</span>
          <span>旗舰店 {{ replenishStats.s1 }} 次</span>
          <span>社区店 {{ replenishStats.s2 }} 次</span>
          <span>生鲜店 {{ replenishStats.s3 }} 次</span>
        </div>
        <el-table :data="replenishList" border stripe size="small" max-height="350">
          <el-table-column prop="id" label="编号" width="70" />
          <el-table-column prop="product_name" label="商品名" min-width="140" />
          <el-table-column prop="category" label="品类" width="90" />
          <el-table-column label="门店" width="90">
            <template #default="{row}">{{ ['','旗舰店','社区店','生鲜店'][row.store_id]||'门店'+row.store_id }}</template>
          </el-table-column>
          <el-table-column prop="count" label="数量" width="70" />
          <el-table-column prop="production_date" label="生产日期" width="110" />
          <el-table-column prop="shelf_life_months" label="保质期(月)" width="90" />
          <el-table-column prop="create_time" label="补货时间" width="160" />
        </el-table>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import * as echarts from 'echarts'
import * as XLSX from 'xlsx'
import { getProductRank, getStoreRank, getRegionPreference, getReplenishHistory } from '@/api/analysis'

const rankChartRef = ref(null)
const storeChartRef = ref(null)
const preferenceChartRef = ref(null)

// 补货数据
const replenishStore = ref(null)
const replenishList = ref([])
const replenishStats = ref(null)

const loadReplenish = async () => {
  try {
    const res = await getReplenishHistory(replenishStore.value || null)
    const all = res.data || []
    // 过滤本月
    const now = new Date()
    const thisMonth = all.filter(r => {
      const t = new Date(r.create_time)
      return t.getMonth() === now.getMonth() && t.getFullYear() === now.getFullYear()
    })
    replenishList.value = thisMonth
    replenishStats.value = {
      total: thisMonth.length,
      s1: thisMonth.filter(r => r.store_id === 1).length,
      s2: thisMonth.filter(r => r.store_id === 2).length,
      s3: thisMonth.filter(r => r.store_id === 3).length
    }
  } catch (_) {}
}

const exportReplenish = () => {
  const data = replenishList.value.map(r => ({
    '编号': r.id,
    '商品名': r.product_name,
    '品类': r.category,
    '门店': ['','旗舰店','社区店','生鲜店'][r.store_id]||r.store_id,
    '数量': r.count,
    '生产日期': r.production_date,
    '保质期(月)': r.shelf_life_months,
    '补货时间': r.create_time
  }))
  const ws = XLSX.utils.json_to_sheet(data)
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, '本月补货清单')
  XLSX.writeFile(wb, `补货清单_${new Date().toISOString().slice(0,7)}.xlsx`)
}

// 初始化图表
const initCharts = async () => {
  // 1. 商品销量 TOP10
  try {
    const rankRes = await getProductRank()
    const rankData = (rankRes.data || []).slice(0, 10)

    const rankChart = echarts.init(rankChartRef.value)
    if (rankData.length === 0) {
      rankChart.setOption({ title: { text: '暂无数据', left:'center', top:'center', textStyle:{color:'#999'} } })
    } else {
      rankChart.setOption({
        tooltip: { trigger: 'axis', formatter: (p) => `${p[0].name}<br/>销量: ${p[0].value}` },
        grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
        xAxis: { type: 'value', splitLine: { lineStyle: { type: 'dashed' } } },
        yAxis: { type: 'category', data: rankData.map(i => i.product_name).reverse() },
        series: [{
          type: 'bar',
          data: rankData.map(i => i.total_quantity).reverse(),
          itemStyle: { color: new echarts.graphic.LinearGradient(0,0,1,0,[{offset:0,color:'#83bff6'},{offset:1,color:'#188df0'}]), borderRadius:[0,4,4,0] },
          label: { show: true, position: 'right' }
        }]
      })
    }
  } catch (e) { console.error('商品排行失败', e) }

  // 2. 门店销售额占比
  try {
    const storeRes = await getStoreRank()
    const storeData = storeRes.data || []

    const storeChart = echarts.init(storeChartRef.value)
    if (storeData.length === 0) {
      storeChart.setOption({ title: { text: '暂无数据', left:'center', top:'center', textStyle:{color:'#999'} } })
    } else {
      storeChart.setOption({
        tooltip: { trigger: 'item' },
        legend: { bottom: '0%' },
        series: [{
          type: 'pie', radius: ['40%','70%'], itemStyle: { borderRadius:10, borderColor:'#fff', borderWidth:2 },
          label: { show:true, formatter:'{b}: {d}%' },
          data: storeData.map(i => ({ value: i.total_sales, name: `门店 ${i.store_id}` }))
        }]
      })
    }
  } catch (e) { console.error('门店排行失败', e) }

  // 3. 区域热销偏好
  try {
    const res = await getRegionPreference()
    const prefData = res.data || []

    if (prefData.length === 0) {
      const prefChart = echarts.init(preferenceChartRef.value)
      prefChart.setOption({
        title: { text: '暂无数据\n请先进行收银交易', left:'center', top:'center', textStyle:{color:'#999',fontSize:14} }
      })
    } else {
      const stores = [...new Set(prefData.map(d => d.store_id))].sort()
      const categories = [...new Set(prefData.map(d => d.category))]

      const series = categories.map(cat => ({
        name: cat, type: 'bar', stack: 'total',
        label: { show: true }, emphasis: { focus: 'series' },
        data: stores.map(s => {
          const item = prefData.find(d => d.store_id === s && d.category === cat)
          return item ? item.sales : 0
        })
      }))

      const prefChart = echarts.init(preferenceChartRef.value)
      prefChart.setOption({
        tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
        legend: { top: '0%' },
        grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true, top: '10%' },
        xAxis: { type: 'category', data: stores.map(s => `门店 ${s}`) },
        yAxis: { type: 'value' },
        series
      })
    }
  } catch (e) {
    console.error('获取区域偏好失败', e)
  }
}

onMounted(() => {
  loadReplenish()

  initCharts()
  // 监听窗口大小变化，重绘图表
  window.addEventListener('resize', () => {
    echarts.getInstanceByDom(rankChartRef.value)?.resize()
    echarts.getInstanceByDom(storeChartRef.value)?.resize()
    echarts.getInstanceByDom(preferenceChartRef.value)?.resize()
  })
})
</script>

<style scoped>
.analysis-page {
  /* padding: 20px; */
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

.dashboard-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-template-rows: auto auto;
  gap: 20px;
  grid-template-areas: 
    "rank store"
    "pref pref";
}

.rank-card {
  grid-area: rank;
}

.store-card {
  grid-area: store;
}

.preference-card {
  grid-area: pref;
}

.card-header {
  font-weight: bold;
  font-size: 16px;
  color: #303133;
}
</style>