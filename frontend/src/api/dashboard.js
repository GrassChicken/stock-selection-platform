/**
 * API: 大盘/首页
 */
import api from './request'

export const getDashboard = () => api.get('/api/dashboard')

export const triggerAnalysis = (trigger = 'manual') =>
  api.post(`/api/analyze?trigger=${trigger}`)

export const getAnalysisStatus = (taskId) =>
  api.get(`/api/analyze/status/${taskId}`)

export const getLatestResult = () =>
  api.get('/api/analyze/latest')
