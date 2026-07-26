import request from '@/utils/request'

export const createOrder = (data) => {
  const payload = {
    ...data,
    storeId: data.storeId || localStorage.getItem('storeId') || 1
  }
  return request.post('/order/create', payload)
}

export const getMemberPoints = (memberId) => {
  return request.get('/order/member-points', {
    params: { memberId }
  })
}

// ===== 收银员换班 API =====

/** 开班：传入找零备用金 */
export const openShift = (openingCash) => {
  return request.post('/shift/open', null, { params: { openingCash } })
}

/** 交班：传入实际清点现金 */
export const closeShift = (closingCash) => {
  return request.post('/shift/close', null, { params: { closingCash } })
}

/** 查询当前是否有活跃班次 */
export const getCurrentShift = () => {
  return request.get('/shift/current')
}
