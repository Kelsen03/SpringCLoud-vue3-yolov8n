import request from '@/utils/request'

export const getStoreRank = () => {
  return request.get('/analysis/storeRank')
}

export const getProductRank = () => {
  return request.get('/analysis/productRank')
}

export const getPreferenceAnalysis = () => {
  return request.get('/analysis/preference')
}

/** 补货推荐算法（含建议补货量） */
export const getReplenishRecommend = () => request.get('/analysis/replenish/recommend')

/** 补货历史（按门店可选） */
export const getReplenishHistory = (storeId) => {
  return request.get('/inventory/replenish/history', { params: { storeId } })
}

// 获取收银员工作记录分析
export const getShiftRecordAnalysis = () => {
  return request.get('/analysis/shiftRecord')
}
