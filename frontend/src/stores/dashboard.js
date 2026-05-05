/**
 * Pinia Store: Dashboard
 */
import { defineStore } from 'pinia'
import { getDashboard, triggerAnalysis, getAnalysisStatus, getLatestResult } from '../api/dashboard'

export const useDashboardStore = defineStore('dashboard', {
  state: () => ({
    // 大盘数据
    shIndex: 0, shChange: 0,
    szIndex: 0, szChange: 0,
    cyIndex: 0, cyChange: 0,
    upCount: 0, downCount: 0, totalVolume: 0,
    updateTime: '',
    elapsed: 0, // 上次分析耗时(秒)
    // 板块
    sectors: [],
    boardSectors: { main: [], chinext: [], star: [] },
    stats: {},
    boardStats: { main: {}, chinext: {}, star: {} },
    // 分析状态
    analyzing: false,
    progress: 0,
    currentStep: '',
    taskId: '',
  }),

  actions: {
    async fetchDashboard() {
      try {
        const data = await getDashboard()
        this.shIndex = data.sh_index || 0
        this.shChange = data.sh_change || 0
        this.szIndex = data.sz_index || 0
        this.szChange = data.sz_change || 0
        this.cyIndex = data.cy_index || 0
        this.cyChange = data.cy_change || 0
        this.upCount = data.up_count || 0
        this.downCount = data.down_count || 0
        this.totalVolume = data.total_volume || 0
        this.updateTime = data.update_time || ''
        this.sectors = data.sectors || []
        this.stats = data.stats || {}
        this.boardStats = data.stats?.board_stats || { main: {}, chinext: {}, star: {} }
        // 获取分析耗时
        try {
          const latest = await getLatestResult()
          if (latest && latest.elapsed) this.elapsed = Math.round(latest.elapsed)
        } catch {}
        // 获取各 board 的板块数据
        const { getSectors } = await import('../api/sectors')
        for (const board of ['main', 'chinext', 'star']) {
          try {
            this.boardSectors[board] = await getSectors(board)
          } catch {
            this.boardSectors[board] = []
          }
        }
      } catch (e) {
        console.error('获取大盘数据失败:', e)
      }
    },

    async startAnalysis() {
      try {
        const task = await triggerAnalysis()
        this.taskId = task.task_id
        this.analyzing = true
        this.progress = 0
        this.currentStep = task.current_step
        this.pollStatus()
      } catch (e) {
        console.error('触发分析失败:', e)
      }
    },

    async pollStatus() {
      if (!this.taskId) return
      const poll = async () => {
        try {
          const status = await getAnalysisStatus(this.taskId)
          this.progress = status.progress || 0
          this.currentStep = status.current_step || ''
          if (status.status === 'completed' || status.status === 'failed') {
            this.analyzing = false
            await this.fetchDashboard() // 刷新数据
            return
          }
          setTimeout(poll, 2000)
        } catch {
          this.analyzing = false
        }
      }
      poll()
    },
  },
})
