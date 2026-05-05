<template>
  <div class="dashboard">
    <!-- 大盘概览 -->
    <el-row :gutter="16" class="market-bar">
      <el-col :span="6">
        <el-card shadow="hover" :class="store.shChange >= 0 ? 'up' : 'down'">
          <template #header>上证指数</template>
          <div class="index-value">{{ store.shIndex?.toFixed(2) || '--' }}</div>
          <div class="index-change">{{ store.shChange >= 0 ? '+' : '' }}{{ store.shChange?.toFixed(2) || '--' }}%</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" :class="store.szChange >= 0 ? 'up' : 'down'">
          <template #header>深证成指</template>
          <div class="index-value">{{ store.szIndex?.toFixed(2) || '--' }}</div>
          <div class="index-change">{{ store.szChange >= 0 ? '+' : '' }}{{ store.szChange?.toFixed(2) || '--' }}%</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" :class="store.cyChange >= 0 ? 'up' : 'down'">
          <template #header>创业板指</template>
          <div class="index-value">{{ store.cyIndex?.toFixed(2) || '--' }}</div>
          <div class="index-change">{{ store.cyChange >= 0 ? '+' : '' }}{{ store.cyChange?.toFixed(2) || '--' }}%</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>涨跌家数</template>
          <div class="up-down">
            <span class="up-text">涨 {{ store.upCount || '--' }}</span>
            <span class="down-text">跌 {{ store.downCount || '--' }}</span>
          </div>
          <div class="volume">成交额 {{ store.totalVolume || '--' }}万亿</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 分析状态 -->
    <el-card class="status-card" shadow="never">
      <div class="status-row">
        <div>
          <span>📅 最近分析: {{ store.updateTime || '尚未分析' }}</span>
          <span style="margin-left: 24px">⏰ 下次定时: 2026-05-05 16:00</span>
        </div>
        <el-button type="primary" @click="triggerAnalysis" :loading="store.analyzing">
          🔄 立即分析
        </el-button>
      </div>
      <el-progress v-if="store.analyzing" :percentage="store.progress" :stroke-width="8" style="margin-top: 12px" />
    </el-card>

    <!-- 板块热度 -->
    <div class="section-title">🏷️ 板块热度排行</div>
    <div class="sector-cards">
      <el-card
        v-for="sector in store.sectors"
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
      <el-col :span="6"><el-card shadow="never" class="stat-card"><span class="stat-label">A+ 优质</span><span class="stat-value">{{ store.stats?.['A+'] || 0 }}</span></el-card></el-col>
      <el-col :span="6"><el-card shadow="never" class="stat-card"><span class="stat-label">A 良好</span><span class="stat-value">{{ store.stats?.A || 0 }}</span></el-card></el-col>
      <el-col :span="6"><el-card shadow="never" class="stat-card"><span class="stat-label">B 一般</span><span class="stat-value">{{ store.stats?.B || 0 }}</span></el-card></el-col>
      <el-col :span="6"><el-card shadow="never" class="stat-card"><span class="stat-label">C 较弱</span><span class="stat-value">{{ store.stats?.C || 0 }}</span></el-card></el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useDashboardStore } from '../stores/dashboard'

const store = useDashboardStore()
const selectedSector = ref('')

// 板块股票列表
const stockList = computed(() => {
  const allStocks = []
  for (const sector of store.sectors) {
    if (sector.stocks) {
      sector.stocks.forEach((s, i) => {
        allStocks.push({ rank: i + 1, ...s })
      })
    }
  }
  return allStocks
})

const triggerAnalysis = () => {
  store.startAnalysis()
}

onMounted(() => {
  store.fetchDashboard()
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
