<template>
  <div class="dashboard">
    <!-- 大盘概览 -->
    <el-row :gutter="16" class="market-bar">
      <el-col :span="6">
        <el-card shadow="hover" :class="dashboardData.sh_change >= 0 ? 'up' : 'down'">
          <template #header>上证指数</template>
          <div class="index-value">{{ dashboardData.sh_index?.toFixed(2) || '--' }}</div>
          <div class="index-change">{{ dashboardData.sh_change >= 0 ? '+' : '' }}{{ dashboardData.sh_change?.toFixed(2) || '--' }}%</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" :class="dashboardData.sz_change >= 0 ? 'up' : 'down'">
          <template #header>深证成指</template>
          <div class="index-value">{{ dashboardData.sz_index?.toFixed(2) || '--' }}</div>
          <div class="index-change">{{ dashboardData.sz_change >= 0 ? '+' : '' }}{{ dashboardData.sz_change?.toFixed(2) || '--' }}%</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" :class="dashboardData.cy_change >= 0 ? 'up' : 'down'">
          <template #header>创业板指</template>
          <div class="index-value">{{ dashboardData.cy_index?.toFixed(2) || '--' }}</div>
          <div class="index-change">{{ dashboardData.cy_change >= 0 ? '+' : '' }}{{ dashboardData.cy_change?.toFixed(2) || '--' }}%</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>涨跌家数</template>
          <div class="up-down">
            <span class="up-text">涨 {{ dashboardData.up_count || '--' }}</span>
            <span class="down-text">跌 {{ dashboardData.down_count || '--' }}</span>
          </div>
          <div class="volume">成交额 {{ dashboardData.total_volume || '--' }}万亿</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 分析状态 -->
    <el-card class="status-card" shadow="never">
      <div class="status-row">
        <div>
          <span>📅 最近分析: {{ dashboardData.update_time || '尚未分析' }}</span>
          <span style="margin-left: 24px">⏰ 下次定时: 2026-05-05 16:00</span>
        </div>
        <el-button type="primary" @click="triggerAnalysis" :loading="analyzing">
          🔄 立即分析
        </el-button>
      </div>
      <el-progress v-if="analyzing" :percentage="progress" :stroke-width="8" style="margin-top: 12px" />
    </el-card>

    <!-- 板块热度 -->
    <div class="section-title">🏷️ 板块热度排行</div>
    <div class="sector-cards">
      <el-card
        v-for="sector in dashboardData.sectors"
        :key="sector.name"
        shadow="hover"
        :class="['sector-card', { active: selectedSector === sector.name }]"
        @click="selectedSector = sector.name"
      >
        <div class="sector-heat">
          <span class="sector-name">🔥 {{ sector.name }}</span>
          <span class="heat-value">{{ sector.heat }}</span>
        </div>
        <el-progress :percentage="sector.heat" :color="sector.heat > 80 ? '#f56c6c' : sector.heat > 60 ? '#e6a23c' : '#67c23a'" :stroke-width="6" :show-text="false" />
        <div class="sector-change" :class="sector.change_pct >= 0 ? 'up' : 'down'">
          {{ sector.change_pct >= 0 ? '▲' : '▼' }} {{ Math.abs(sector.change_pct).toFixed(1) }}%
        </div>
      </el-card>
    </div>

    <!-- 板块股票列表 -->
    <div class="section-title">📋 {{ selectedSector || '全部' }}板块选股详情</div>
    <el-card shadow="never">
      <el-table :data="stockList" stripe style="width: 100%">
        <el-table-column prop="rank" label="排名" width="60" />
        <el-table-column prop="code" label="代码" width="90" />
        <el-table-column prop="name" label="名称" width="100" />
        <el-table-column prop="price" label="现价" width="90">
          <template #default="{ row }">{{ row.price?.toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="change_pct" label="涨跌幅" width="90">
          <template #default="{ row }">
            <span :class="row.change_pct >= 0 ? 'up' : 'down'">
              {{ row.change_pct >= 0 ? '+' : '' }}{{ row.change_pct?.toFixed(1) }}%
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="total_score" label="评分" width="80">
          <template #default="{ row }">
            <el-tag :type="row.rating === 'A+' ? 'danger' : row.rating === 'A' ? 'warning' : 'info'" size="small">
              {{ row.total_score }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="rating" label="评级" width="70">
          <template #default="{ row }">
            <el-tag :type="row.rating === 'A+' ? 'danger' : row.rating === 'A' ? 'warning' : 'info'" size="small">
              {{ row.rating }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="80">
          <template #default>
            <el-button size="small" type="primary" link>详情</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 底部统计 -->
    <el-row :gutter="16" class="stats-bar">
      <el-col :span="6"><el-card shadow="never" class="stat-card"><span class="stat-label">A+ 优质</span><span class="stat-value">{{ dashboardData.stats?.['A+'] || 0 }}</span></el-card></el-col>
      <el-col :span="6"><el-card shadow="never" class="stat-card"><span class="stat-label">A 良好</span><span class="stat-value">{{ dashboardData.stats?.A || 0 }}</span></el-card></el-col>
      <el-col :span="6"><el-card shadow="never" class="stat-card"><span class="stat-label">涨停股</span><span class="stat-value">{{ dashboardData.stats?.涨停 || 0 }}</span></el-card></el-col>
      <el-col :span="6"><el-card shadow="never" class="stat-card"><span class="stat-label">北向流入</span><span class="stat-value up">+52.3亿</span></el-card></el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const dashboardData = ref({})
const selectedSector = ref('')
const analyzing = ref(false)
const progress = ref(0)
const stockList = ref([])

// 模拟数据 (Phase 1 替换为真实 API)
const mockStocks = [
  { rank: 1, code: '688008', name: '澜起科技', price: 65.20, change_pct: 3.2, total_score: 86, rating: 'A+' },
  { rank: 2, code: '300782', name: '卓胜微', price: 112.50, change_pct: 1.8, total_score: 82, rating: 'A+' },
  { rank: 3, code: '603986', name: '兆易创新', price: 98.30, change_pct: -0.5, total_score: 78, rating: 'A' },
  { rank: 4, code: '002475', name: '立讯精密', price: 32.80, change_pct: 2.1, total_score: 75, rating: 'A' },
  { rank: 5, code: '600584', name: '长电科技', price: 28.50, change_pct: 4.5, total_score: 73, rating: 'A' },
  { rank: 6, code: '300661', name: '圣邦股份', price: 75.60, change_pct: 0.9, total_score: 65, rating: 'A' },
]

const triggerAnalysis = async () => {
  analyzing.value = true
  progress.value = 0
  try {
    await axios.post('/api/analyze?trigger=manual')
    const timer = setInterval(() => {
      progress.value += Math.random() * 15
      if (progress.value >= 100) {
        progress.value = 100
        clearInterval(timer)
        setTimeout(() => { analyzing.value = false }, 500)
      }
    }, 500)
  } catch (e) {
    analyzing.value = false
  }
}

onMounted(async () => {
  try {
    const { data } = await axios.get('/api/dashboard')
    dashboardData.value = data
  } catch {
    dashboardData.value = {
      sh_index: 3350.25, sh_change: 0.85,
      sz_index: 10850.30, sz_change: 1.12,
      cy_index: 2180.50, cy_change: 0.65,
      up_count: 2850, down_count: 2200, total_volume: 1.25,
      sectors: [
        { name: '科技', heat: 92, change_pct: 5.2 },
        { name: '新能源', heat: 78, change_pct: 3.1 },
        { name: '医药', heat: 75, change_pct: -0.8 },
        { name: '消费', heat: 65, change_pct: 1.5 },
        { name: '金融', heat: 60, change_pct: 2.0 },
      ],
      stats: { 'A+': 12, A: 28, B: 35, C: 15, '涨停': 85 },
      update_time: '2026-05-04 16:30',
    }
  }
  stockList.value = mockStocks
})
</script>

<style scoped>
.dashboard { max-width: 1400px; margin: 0 auto; }
.market-bar { margin-bottom: 16px; }
.market-bar .el-card { border-radius: 12px; }
.market-bar .el-card.up { border-top: 3px solid #f56c6c; }
.market-bar .el-card.down { border-top: 3px solid #67c23a; }
.index-value { font-size: 24px; font-weight: 700; }
.index-change { font-size: 14px; margin-top: 4px; }
.up .index-change { color: #f56c6c; }
.down .index-change { color: #67c23a; }
.up-down { display: flex; gap: 12px; font-size: 14px; font-weight: 600; }
.up-text { color: #f56c6c; }
.down-text { color: #67c23a; }
.volume { color: #999; font-size: 12px; margin-top: 4px; }
.status-card { margin-bottom: 16px; border-radius: 12px; }
.status-row { display: flex; justify-content: space-between; align-items: center; }
.section-title { font-size: 18px; font-weight: 600; margin: 20px 0 12px; }
.sector-cards { display: flex; gap: 12px; overflow-x: auto; padding-bottom: 8px; }
.sector-card { min-width: 180px; cursor: pointer; transition: all 0.2s; border-radius: 12px; }
.sector-card:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
.sector-card.active { border: 2px solid #667eea; }
.sector-heat { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.sector-name { font-weight: 600; font-size: 16px; }
.heat-value { font-size: 20px; font-weight: 700; color: #667eea; }
.sector-change { font-size: 12px; margin-top: 8px; }
.sector-change.up { color: #f56c6c; }
.sector-change.down { color: #67c23a; }
.stats-bar { margin-top: 20px; }
.stat-card { text-align: center; border-radius: 12px; }
.stat-label { display: block; color: #999; font-size: 12px; }
.stat-value { display: block; font-size: 24px; font-weight: 700; margin-top: 4px; }
.stat-value.up { color: #f56c6c; }
.up { color: #f56c6c !important; }
.down { color: #67c23a !important; }
</style>
