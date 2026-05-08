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
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'
import { getProductRank, getStoreRank, getRegionPreference } from '@/api/analysis'

const rankChartRef = ref(null)
const storeChartRef = ref(null)
const preferenceChartRef = ref(null)

// 初始化图表
const initCharts = async () => {
  // 1. 获取并渲染商品销量排行
  try {
    const rankRes = await getProductRank()
    const rankData = rankRes.data || [] 
    // 后端返回字段: product_name, category, total_quantity
    
    const rankChart = echarts.init(rankChartRef.value)
    rankChart.setOption({
      tooltip: { 
        trigger: 'axis',
        formatter: (params) => {
          const item = rankData.find(d => d.product_name === params[0].name)
          return `${params[0].name}<br/>类别: ${item?.category || '未知'}<br/>销量: ${params[0].value}`
        }
      },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: { type: 'value', splitLine: { lineStyle: { type: 'dashed' } } },
      yAxis: { 
        type: 'category', 
        data: rankData.map(item => item.product_name).reverse() 
      },
      series: [{
        name: '销量',
        type: 'bar',
        data: rankData.map(item => item.total_quantity).reverse(),
        itemStyle: { 
          color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
            { offset: 0, color: '#83bff6' },
            { offset: 0.5, color: '#188df0' },
            { offset: 1, color: '#188df0' }
          ]),
          borderRadius: [0, 4, 4, 0]
        },
        label: { show: true, position: 'right' }
      }]
    })
  } catch (e) {
    console.error('获取商品排行失败', e)
  }

  // 2. 获取并渲染门店销售排行
  try {
    const storeRes = await getStoreRank()
    const storeData = storeRes.data || [] 
    
    const storeChart = echarts.init(storeChartRef.value)
    storeChart.setOption({
      tooltip: { trigger: 'item' },
      legend: { bottom: '0%' },
      series: [{
        name: '销售额',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: true,
          formatter: '{b}: {d}%'
        },
        data: storeData.map(item => ({
          value: item.total_sales,
          name: `门店 ${item.store_id}`
        }))
      }]
    })
  } catch (e) {
    console.error('获取门店排行失败', e)
  }

  // 3. 区域热销偏好 (新增)
  try {
    let prefData = []
    try {
      const res = await getRegionPreference()
      prefData = res.data || []
    } catch (e) {
      // 模拟数据 (当后端接口未就绪时展示效果)
      prefData = [
        { store_id: 1, category: '饮品', sales: 150 },
        { store_id: 1, category: '食品', sales: 200 },
        { store_id: 1, category: '生活用品', sales: 80 },
        { store_id: 2, category: '饮品', sales: 180 },
        { store_id: 2, category: '食品', sales: 120 },
        { store_id: 2, category: '生活用品', sales: 90 },
        { store_id: 3, category: '饮品', sales: 100 },
        { store_id: 3, category: '食品', sales: 110 },
        { store_id: 3, category: '生活用品', sales: 160 },
      ]
    }

    // 数据处理：转为 ECharts dataset 格式
    const stores = [...new Set(prefData.map(d => d.store_id))].sort()
    const categories = ['饮品', '食品', '生活用品']
    
    const series = categories.map(cat => {
      return {
        name: cat,
        type: 'bar',
        stack: 'total',
        label: { show: true },
        emphasis: { focus: 'series' },
        data: stores.map(storeId => {
          const item = prefData.find(d => d.store_id === storeId && d.category === cat)
          return item ? item.sales : 0
        })
      }
    })

    const prefChart = echarts.init(preferenceChartRef.value)
    prefChart.setOption({
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      legend: { top: '0%' },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true, top: '10%' },
      xAxis: { 
        type: 'category', 
        data: stores.map(s => `门店 ${s}`) 
      },
      yAxis: { type: 'value' },
      series: series
    })

  } catch (e) {
    console.error('获取区域偏好失败', e)
  }
}

onMounted(() => {
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