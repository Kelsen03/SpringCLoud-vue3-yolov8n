import request from '@/utils/request'

// 查询库存
export const getInventoryList = (storeId) => {
  return request.get('/inventory/list', {
    params: { storeId }
  })
}

// 库存调拨
export const transferStock = (data) => {
  return request.post('/inventory/transfer', null, {
    params: data
  })
}

// 门店补货 (旧版，Query参数)
export const replenishStock = (data) => {
  return request.post('/inventory/replenish', null, {
    params: data
  })
}

// 门店补货 (新版，JSON参数，支持新增商品和日期)
export const replenishNewStock = (data) => {
  return request.post('/inventory/replenish/new', data)
}

// 删除库存
export const deleteInventory = (storeId, productId) => {
  return request.delete('/inventory/delete', {
    params: { storeId, productId }
  })
}
