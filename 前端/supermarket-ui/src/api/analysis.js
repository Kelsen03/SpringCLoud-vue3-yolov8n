import request from '@/utils/request'

export const getProductRank = () => request.get('/analysis/productRank')
export const getStoreRank = () => request.get('/analysis/storeRank')
export const getRegionPreference = () => request.get('/analysis/regionPreference')

/** 补货推荐算法（含建议补货量） */
export const getReplenishRecommend = () => request.get('/analysis/replenish/recommend')

/** 补货历史（按门店可选） */
export const getReplenishHistory = (storeId) => {
  return request.get('/inventory/replenish/history', { params: { storeId } })
}
