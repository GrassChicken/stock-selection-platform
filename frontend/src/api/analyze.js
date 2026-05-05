/**
 * API: 分析控制
 */
import api from './request'

export const triggerAnalysis = (trigger = 'manual') =>
  api.post(`/api/analyze?trigger=${trigger}`)

export const getAnalysisStatus = (taskId) =>
  api.get(`/api/analyze/status/${taskId}`)

export const getLatestResult = () =>
  api.get('/api/analyze/latest')

export const searchStocks = (q) =>
  api.get('/api/analyze/search', { params: { q } })
