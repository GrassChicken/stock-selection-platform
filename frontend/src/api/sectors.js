/**
 * API: 板块
 */
import api from './request'

export const getSectors = () => api.get('/api/sectors')

export const getSectorStocks = (name) =>
  api.get(`/api/sectors/${encodeURIComponent(name)}/stocks`)
