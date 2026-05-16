import request from '@/utils/request'

export const getProductList = (params = {}) => {
  return request.get('/product/list', {
    params: {
      storeId: localStorage.getItem('storeId') || 1,
      ...params
    }
  })
}

// 新增：根据ID查询单个商品
export const getProductById = (id) => {
  // 由于后端没有专门的详情接口，我们复用列表接口并在前端筛选
  // 或者如果后端支持 ?id=xxx 参数更好，这里暂时用列表筛选
  return request.get('/product/list', {
    params: {
      storeId: localStorage.getItem('storeId') || 1
    }
  }).then(res => {
    const product = res.data.find(p => String(p.id) === String(id))
    return { data: product } // 模拟返回结构
  })
}

export const updateProduct = (data) => {
  return request.put('/product/update', data)
}

import axios from 'axios'

/** 条形码查商品 */
export const getProductByBarcode = (barcode) => {
  return request.get(`/product/barcode/${barcode}`)
}

/** 热门商品 TOP10（按销量） */
export const getHotProducts = () => {
  return request.get('/product/hot')
}

// AI 智能识别商品接口
export const aiRecognizeProduct = (base64Image) => {
  // 修改为指向您阿里云服务器上的 Python AI 服务端口 (5000)
  // 使用独立的 axios 实例，避免携带不必要的 token 导致跨域问题
  return axios.post('http://8.148.236.60:5000/api/detect', { image: base64Image }, {
    headers: {
      'Content-Type': 'application/json'
    }
  })
}
