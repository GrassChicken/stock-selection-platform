/**
 * API: 系统设置
 */
import api from './request'

// 定时分析
export const getSchedule = () => api.get('/api/schedule')
export const saveSchedule = (data) => api.put('/api/schedule', data)

// 评分权重
export const getWeights = () => api.get('/api/settings/weights')
export const saveWeights = (data) => api.put('/api/settings/weights', data)
