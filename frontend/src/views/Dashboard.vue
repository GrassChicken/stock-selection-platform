<template>
  <div class="dashboard">
    <!-- 大盘概览 -->
    <el-row :gutter="16" class="market-bar">
      <el-col :xs="12" :sm="12" :md="6">
        <el-card shadow="hover" :class="store.shChange >= 0 ? 'up' : 'down'">
          <template #header>上证指数</template>
          <div class="index-value">{{ store.shIndex?.toFixed(2) || '--' }}</div>
          <div class="index-change">{{ store.shChange >= 0 ? '+' : '' }}{{ store.shChange?.toFixed(2) || '--' }}%</div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="12" :md="6">
        <el-card shadow="hover" :class="store.szChange >= 0 ? 'up' : 'down'">
          <template #header>深证成指</template>
          <div class="index-value">{{ store.szIndex?.toFixed(2) || '--' }}</div>
          <div class="index-change">{{ store.szChange >= 0 ? '+' : '' }}{{ store.szChange?.toFixed(2) || '--' }}%</div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="12" :md="6">
        <el-card shadow="hover" :class="store.cyChange >= 0 ? 'up' : 'down'">
          <template #header>创业板指</template>
          <div class="index-value">{{ store.cyIndex?.toFixed(2) || '--' }}</div>
          <div class="index-change">{{ store.cyChange >= 0 ? '+' : '' }}{{ store.cyChange?.toFixed(2) || '--' }}%</div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="12" :md="6">
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
        <div class="status-info">
          <span>📅 最近分析: {{ store.updateTime || '尚未分析' }}</span>
        </div>
        <el-button type="primary" @click="triggerAnalysis" :loading="store.analyzing">
          🔄 立即分析
        </el-button>
      </div>
      <el-progress v-if="store.analyzing" :percentage="store.progress" :stroke-width="8" style="margin-top: 12px" />
    </el-card>

    <!-- 板块热度 -->
    <div class="section-title">🏷️ 板块热度排行</div>
    
    <!-- 主板/创业板/科创板 Tab -->
    <div class="board-tabs">
      <span
        v-for="board in ['main', 'chinext', 'star']"
        :key="board"
        :class="['board-tab', { active: activeBoard === board }]"
        @click="switchBoard(board)"
      >
        {{ boardLabels[board] }}
        <span class="tab-count">({{ (store.boardStats[board] || {}).count || 0 }}只)</span>
      </span>
    </div>
    
    <div class="sector-cards">
      <el-card
        v-for="sector in boardSectors"
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
      <!-- PC 端表格 -->
      <el-table :data="stockList" stripe class="stock-table" style="width: 100%">
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

      <!-- 手机端卡片视图 -->
      <div class="stock-cards-mobile">
        <div v-for="stock in stockList" :key="stock.code" class="stock-card-mobile">
          <div class="stock-header">
            <span class="stock-rank">#{{ stock.rank }}</span>
            <span class="stock-code">{{ stock.code }}</span>
            <span class="stock-name">{{ stock.name }}</span>
          </div>
          <div class="stock-body">
            <div class="stock-price">
              <span class="price-value">¥{{ stock.price?.toFixed(2) }}</span>
              <span :class="['price-change', stock.change_pct >= 0 ? 'up' : 'down']">
                {{ stock.change_pct >= 0 ? '+' : '' }}{{ stock.change_pct?.toFixed(1) }}%
              </span>
            </div>
            <div class="stock-score">
              <el-tag :type="stock.rating === 'A+' ? 'danger' : stock.rating === 'A' ? 'warning' : 'info'" size="small">
                {{ stock.total_score }}分 {{ stock.rating }}
              </el-tag>
            </div>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 底部统计 -->
    <el-row :gutter="12" class="stats-bar">
      <el-col :xs="12" :sm="6" :md="6">
        <el-card shadow="never" class="stat-card">
          <span class="stat-label">A+ 优质</span>
          <span class="stat-value">{{ boardStats['A+'] || 0 }}</span>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6" :md="6">
        <el-card shadow="never" class="stat-card">
          <span class="stat-label">A 良好</span>
          <span class="stat-value">{{ boardStats['A'] || 0 }}</span>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6" :md="6">
        <el-card shadow="never" class="stat-card">
          <span class="stat-label">B 一般</span>
          <span class="stat-value">{{ boardStats['B'] || 0 }}</span>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6" :md="6">
        <el-card shadow="never" class="stat-card">
          <span class="stat-label">C 较弱</span>
          <span class="stat-value">{{ boardStats['C'] || 0 }}</span>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useDashboardStore } from '../stores/dashboard'

const store = useDashboardStore()
const selectedSector = ref('')
const activeBoard = ref('main')

const boardLabels = {
  main: '主板',
  chinext: '创业板',
  star: '科创板',
}

const boardSectors = computed(() => store.boardSectors[activeBoard.value] || [])
const boardStats = computed(() => store.boardStats[activeBoard.value] || {})

const stockList = computed(() => {
  const allStocks = []
  for (const sector of boardSectors.value) {
    if (sector.stocks) {
      sector.stocks.forEach((s, i) => allStocks.push({ rank: i + 1, ...s }))
    }
  }
  return allStocks
})

const triggerAnalysis = () => store.startAnalysis()
const switchBoard = (board) => { activeBoard.value = board }

onMounted(() => { store.fetchDashboard() })
</script>

<style scoped>
/* ========== 基础样式 ========== */
.dashboard { max-width: 1400px; margin: 0 auto; padding: 0 16px; }

/* 大盘指数 */
.market-bar { margin-bottom: 16px; }
.market-bar .el-card { border-radius: 12px; transition: transform 0.2s; }
.market-bar .el-card:hover { transform: translateY(-2px); }
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

/* 分析状态 */
.status-card { margin-bottom: 16px; border-radius: 12px; }
.status-row { display: flex; justify-content: space-between; align-items: center; }
.status-info { font-size: 14px; }

/* 板块 Tab */
.section-title { font-size: 18px; font-weight: 600; margin: 20px 0 12px; }
.board-tabs { display: flex; gap: 8px; margin-bottom: 16px; flex-wrap: wrap; }
.board-tab {
  padding: 8px 20px; border-radius: 8px; cursor: pointer;
  background: #f5f7fa; color: #606266; font-size: 14px; font-weight: 500;
  transition: all 0.2s; user-select: none;
}
.board-tab:hover { background: #e8eaf0; }
.board-tab.active { background: #409eff; color: #fff; }
.tab-count { font-size: 12px; opacity: 0.8; margin-left: 4px; }

/* 板块卡片 */
.sector-cards { display: flex; gap: 12px; overflow-x: auto; padding-bottom: 8px; scroll-snap-type: x mandatory; }
.sector-card {
  min-width: 180px; cursor: pointer; transition: all 0.2s; border-radius: 12px;
  scroll-snap-align: start;
}
.sector-card:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
.sector-card.active { border: 2px solid #667eea; }
.sector-heat { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.sector-name { font-weight: 600; font-size: 16px; }
.heat-value { font-size: 20px; font-weight: 700; color: #667eea; }
.sector-change { font-size: 12px; margin-top: 8px; }
.sector-change.up { color: #f56c6c; }
.sector-change.down { color: #67c23a; }

/* 股票表格 */
.stock-table { display: block; }
.stock-cards-mobile { display: none; }

/* 底部统计 */
.stats-bar { margin-top: 20px; }
.stat-card { text-align: center; border-radius: 12px; transition: transform 0.2s; }
.stat-card:hover { transform: translateY(-2px); }
.stat-label { display: block; color: #999; font-size: 12px; }
.stat-value { display: block; font-size: 24px; font-weight: 700; margin-top: 4px; }
.up { color: #f56c6c !important; }
.down { color: #67c23a !important; }

/* ========== 平板端 (≤1024px) ========== */
@media (max-width: 1024px) {
  .index-value { font-size: 20px; }
  .heat-value { font-size: 18px; }
  .sector-card { min-width: 160px; }
  .stat-value { font-size: 20px; }
}

/* ========== 手机端 (≤768px) ========== */
@media (max-width: 768px) {
  .dashboard { padding: 0 8px; }
  
  /* 指数卡片 2×2 */
  .market-bar { margin-bottom: 12px; }
  .market-bar .el-col { margin-bottom: 8px; }
  .index-value { font-size: 18px; }
  .index-change { font-size: 12px; }
  .up-down { font-size: 12px; }
  .volume { font-size: 11px; }
  
  /* 状态栏 */
  .status-row { flex-direction: column; align-items: flex-start; gap: 8px; }
  .status-info { font-size: 12px; }
  .status-card .el-button { width: 100%; }
  
  /* 板块 Tab */
  .section-title { font-size: 16px; margin: 16px 0 8px; }
  .board-tab { padding: 6px 14px; font-size: 13px; }
  
  /* 板块卡片 纵向堆叠 */
  .sector-cards {
    flex-direction: column;
    overflow-x: visible;
    gap: 8px;
  }
  .sector-card { min-width: 100%; }
  .sector-heat { margin-bottom: 6px; }
  .sector-name { font-size: 14px; }
  .heat-value { font-size: 16px; }
  
  /* 表格隐藏，改用卡片 */
  .stock-table { display: none; }
  .stock-cards-mobile { display: block; }
  
  .stock-card-mobile {
    padding: 12px 0;
    border-bottom: 1px solid #f0f0f0;
  }
  .stock-card-mobile:last-child { border-bottom: none; }
  .stock-header { display: flex; align-items: center; gap: 8px; margin-bottom: 6px; }
  .stock-rank {
    display: inline-block; width: 22px; height: 22px; line-height: 22px;
    text-align: center; border-radius: 50%; background: #f5f7fa;
    font-size: 12px; font-weight: 600; color: #606266;
  }
  .stock-rank:nth-child(-n+3) { background: #f56c6c; color: #fff; }
  .stock-code { font-family: monospace; font-size: 13px; color: #909399; }
  .stock-name { font-size: 14px; font-weight: 600; }
  .stock-body { display: flex; justify-content: space-between; align-items: center; }
  .stock-price { display: flex; flex-direction: column; }
  .price-value { font-size: 16px; font-weight: 700; }
  .price-change { font-size: 12px; }
  .stock-score { display: flex; align-items: center; }
  
  /* 底部统计 2×2 */
  .stats-bar { margin-top: 16px; }
  .stat-label { font-size: 11px; }
  .stat-value { font-size: 18px; }
  .stat-card { padding: 8px; }
}

/* ========== 小屏手机 (≤480px) ========== */
@media (max-width: 480px) {
  .index-value { font-size: 16px; }
  .index-change { font-size: 11px; }
  .board-tab { padding: 5px 10px; font-size: 12px; }
  .tab-count { display: none; }
  .price-value { font-size: 14px; }
  .stock-name { font-size: 13px; }
}
</style>
