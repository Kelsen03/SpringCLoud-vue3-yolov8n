import axios from 'axios'
import { ElMessage } from 'element-plus'

const request = axios.create({
  // 生产环境用相对路径走 nginx 代理，开发环境直连 localhost
  baseURL: import.meta.env.PROD ? '/api' : 'http://localhost:8000',
  timeout: 5000
})

request.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = token
  }
  return config
})

// 响应拦截器：统一处理错误
request.interceptors.response.use(
  response => {
    return response
  },
  error => {
    let msg = ''
    if (error.response) {
      // 有响应，但状态码非 2xx
      msg = `请求错误 ${error.response.status}: ${error.response.data.message || '未知错误'}`
    } else {
      // 无响应（网络错误、超时、后端没起）
      msg = '连接后端失败，请检查网络或联系管理员'
    }
    
    ElMessage.error(msg)
    return Promise.reject(error)
  }
)

export default request
