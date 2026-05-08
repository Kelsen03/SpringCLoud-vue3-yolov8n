import request from '@/utils/request'

export const createOrder = (data) => {
  // 确保一定会传 storeId
  const payload = {
    ...data,
    storeId: data.storeId || localStorage.getItem('storeId') || 1
  }
  return request.post('/order/create', payload)
}

// 获取会员积分的专门接口，不再使用假的0元订单
export const getMemberPoints = (memberId) => {
  return request.get(`/order/member-points`, {
    params: { memberId }
  })
}
