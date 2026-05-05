/**
 * API: 个股
 */
import api from './request'

export const getStock = (code) => api.get(`/api/stocks/${code}`)

export const getStockChart = (code) => api.get(`/api/stocks/${code}/chart`)

export const getTradePoints = (code) => api.get(`/api/stocks/${code}/trade-points`)
