import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import Settings from '../views/Settings.vue'
import StockDetail from '../views/StockDetail.vue'

const routes = [
  { path: '/', name: 'Dashboard', component: Dashboard },
  { path: '/settings', name: 'Settings', component: Settings },
  { path: '/stock/:code', name: 'StockDetail', component: StockDetail },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
