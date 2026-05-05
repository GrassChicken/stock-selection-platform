/**
 * Axios 实例 + 拦截器
 */
import axios from 'axios'

const api = axios.create({
  baseURL: '', // 同源，直接相对路径
  timeout: 30000,
})

// 响应拦截：自动解包 data
api.interceptors.response.use(
  res => res.data,
  err => {
    console.error('[API Error]', err.response?.data || err.message)
    return Promise.reject(err)
  }
)

export default api
