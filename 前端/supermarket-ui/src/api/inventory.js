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

// 发起借货请求
export const requestTransfer = (data) => {
  return request.post('/inventory/transfer/request', null, {
    params: data
  })
}

// 同意借货请求
export const approveTransfer = (transferId) => {
  return request.post('/inventory/transfer/approve', null, {
    params: { transferId }
  })
}

// 拒绝借货请求
export const rejectTransfer = (transferId) => {
  return request.post('/inventory/transfer/reject', null, {
    params: { transferId }
  })
}

// 获取调拨列表
export const getTransferList = (storeId) => {
  return request.get('/inventory/transfer/list', {
    params: { storeId }
  })
}

// 补货历史记录
export const getReplenishHistory = (storeId) => {
  return request.get('/inventory/replenish/history', { params: { storeId } })
}

// 清理库存（清零不删除）
export const clearInventory = (storeId, productId) => {
  return request.post('/inventory/clear', null, { params: { storeId, productId } })
}

// 删除库存
export const deleteInventory = (storeId, productId) => {
  return request.delete('/inventory/delete', {
    params: { storeId, productId }
  })
}
