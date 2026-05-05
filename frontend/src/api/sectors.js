/**
 * API: 板块
 */
import api from './request'

export const getSectors = (board = '') =>
  api.get('/api/sectors', { params: board ? { board } : {} })

export const getSectorStocks = (name) =>
  api.get(`/api/sectors/${encodeURIComponent(name)}/stocks`)
