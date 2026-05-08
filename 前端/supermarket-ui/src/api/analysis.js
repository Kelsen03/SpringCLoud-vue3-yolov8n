import request from '@/utils/request'

// 获取商品销量排行榜
export const getProductRank = () => {
  return request.get('/analysis/productRank')
}

// 获取门店销售排行
export const getStoreRank = () => {
  return request.get('/analysis/storeRank')
}

// 获取区域偏好（新增）
export const getRegionPreference = () => {
  return request.get('/analysis/regionPreference')
}
