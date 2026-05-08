import { createRouter, createWebHistory } from 'vue-router' 
import Login from '@/views/Login.vue' 
import Register from '@/views/Register.vue' // 引入注册页
import Product from '@/views/Product.vue' 
import Inventory from '@/views/Inventory.vue' 
import Order from '@/views/Order.vue' 
import Analysis from '@/views/Analysis.vue'
import Transfer from '@/views/Transfer.vue'

// 新增功能模块
import Pos from '@/views/Pos.vue' // 收银台
import Procurement from '@/views/Procurement.vue' // 采购管理
import Operations from '@/views/Operations.vue' // 门店运营(盘点/报损/交接班)
import Promotions from '@/views/Promotions.vue' // 促销与营销
import AfterSales from '@/views/AfterSales.vue' // 售后与退换货
import Finance from '@/views/Finance.vue' // 财务对账

const routes = [ 
  { path: '/', component: Login }, 
  { path: '/register', component: Register }, // 注册路由
  { path: '/product', component: Product }, 
  { path: '/inventory', component: Inventory }, 
  { path: '/order', component: Order }, 
  { path: '/analysis', component: Analysis },
  { path: '/transfer', component: Transfer },
  
  // 新增路由
  { path: '/pos', component: Pos },
  { path: '/procurement', component: Procurement },
  { path: '/operations', component: Operations },
  { path: '/promotions', component: Promotions },
  { path: '/after-sales', component: AfterSales },
  { path: '/finance', component: Finance }
] 

const router = createRouter({ 
  history: createWebHistory(), 
  routes 
}) 

// 路由守卫
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const role = localStorage.getItem('role')

  if (to.path === '/' || to.path === '/register') {
    // 如果已登录，访问登录页或注册页时自动跳转到首页
    if (token && role) {
      if (role === 'HQ') {
        next('/product')
      } else if (role === 'STORE') {
        next('/order')
      } else if (role === 'CASHIER') {
        next('/pos') // 收银员直接进入收银台
      } else {
        next()
      }
    } else {
      next()
    }
  } else if (to.path === '/inventory') {
    // [网关放行测试] 库存列表页已在网关层放行，前端允许免登录访问以验证
    next()
  } else {
    // 如果未登录，访问其他页面跳转到登录页
    if (!token) {
      next('/')
    } else {
      next()
    }
  }
})

export default router 
