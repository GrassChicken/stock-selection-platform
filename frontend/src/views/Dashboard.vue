<template>
  <div class="dashboard">
    <!-- 大盘概览 -->
    <el-row :gutter="16" class="market-bar">
      <el-col :xs="12" :sm="12" :md="6">
        <el-card shadow="hover" :class="['market-card', store.shChange >= 0 ? 'up' : 'down', 'animate-in']" style="animation-delay: 0.1s">
          <template #header>
            <div class="card-header">
              <el-icon :size="18"><TrendCharts /></el-icon>
              <span>上证指数</span>
            </div>
          </template>
          <div class="index-value"><CountUp :target="store.shIndex" /></div>
          <div class="index-change">
            <el-icon :size="14"><Top v-if="store.shChange >= 0" /><Bottom v-else /></el-icon>
            {{ store.shChange >= 0 ? '+' : '' }}{{ store.shChange?.toFixed(2) || '--' }}%
          </div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="12" :md="6">
        <el-card shadow="hover" :class="['market-card', store.szChange >= 0 ? 'up' : 'down', 'animate-in']" style="animation-delay: 0.2s">
          <template #header>
            <div class="card-header">
              <el-icon :size="18"><Histogram /></el-icon>
              <span>深证成指</span>
            </div>
          </template>
          <div class="index-value"><CountUp :target="store.szIndex" /></div>
          <div class="index-change">
            <el-icon :size="14"><Top v-if="store.szChange >= 0" /><Bottom v-else /></el-icon>
            {{ store.szChange >= 0 ? '+' : '' }}{{ store.szChange?.toFixed(2) || '--' }}%
          </div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="12" :md="6">
        <el-card shadow="hover" :class="['market-card', store.cyChange >= 0 ? 'up' : 'down', 'animate-in']" style="animation-delay: 0.3s">
          <template #header>
            <div class="card-header">
              <el-icon :size="18"><DataLine /></el-icon>
              <span>创业板指</span>
            </div>
          </template>
          <div class="index-value"><CountUp :target="store.cyIndex" /></div>
          <div class="index-change">
            <el-icon :size="14"><Top v-if="store.cyChange >= 0" /><Bottom v-else /></el-icon>
            {{ store.cyChange >= 0 ? '+' : '' }}{{ store.cyChange?.toFixed(2) || '--' }}%
          </div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="12" :md="6">
        <el-card shadow="hover" class="market-card animate-in" style="animation-delay: 0.4s">
          <template #header>
            <div class="card-header">
              <el-icon :size="18"><Sort /></el-icon>
              <span>涨跌家数</span>
            </div>
          </template>
          <div class="up-down">
            <span class="up-text"><el-icon :size="14"><Top /></el-icon> 涨 <CountUp :target="store.upCount" :decimals="0" /></span>
            <span class="down-text"><el-icon :size="14"><Bottom /></el-icon> 跌 <CountUp :target="store.downCount" :decimals="0" /></span>
          </div>
          <div class="volume"><el-icon :size="12"><Coin /></el-icon> 成交额 <CountUp :target="store.totalVolume" /> 万亿</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 分析状态 -->
    <el-card class="status-card animate-in" shadow="never" style="animation-delay: 0.5s">
      <div class="status-row">
        <div class="status-info">
          <el-icon :size="16" class="status-icon"><Clock /></el-icon>
          <span>最近分析: {{ store.updateTime || '尚未分析' }}</span>
          <span v-if="store.elapsed" class="elapsed-badge">耗时 <el-tag size="small" type="warning" effect="dark">{{ store.elapsed }}s</el-tag></span>
        </div>
        <el-button type="primary" @click="triggerAnalysis" :loading="store.analyzing" class="analyze-btn">
          <el-icon v-if="!store.analyzing" :size="16"><Refresh /></el-icon>
          {{ store.analyzing ? '分析中...' : '立即分析' }}
        </el-button>
      </div>
      <el-progress v-if="store.analyzing" :percentage="store.progress" :stroke-width="8" :color="customColors" style="margin-top: 12px">
        <template #default="{ percentage }"><span class="progress-text">{{ percentage }}% — {{ store.currentStep }}</span></template>
      </el-progress>
    </el-card>

    <!-- 板块热度 -->
    <div class="section-title animate-in" style="animation-delay: 0.6s"><el-icon :size="20"><StarFilled /></el-icon> 板块热度排行</div>
    
    <div class="board-tabs animate-in" style="animation-delay: 0.65s">
      <span v-for="(label, board) in boardLabels" :key="board" :class="['board-tab', { active: activeBoard === board }]" @click="switchBoard(board)">
        <el-icon :size="14"><OfficeBuilding v-if="board === 'main'" /><Cpu v-else-if="board === 'chinext'" /><Monitor v-else /></el-icon>
        {{ label }} <span class="tab-count">({{ (store.boardStats[board] || {}).count || 0 }}只)</span>
      </span>
    </div>
    
    <div class="sector-cards animate-in" style="animation-delay: 0.7s">
      <el-card v-for="(sector, idx) in boardSectors" :key="sector.name" shadow="hover"
        :class="['sector-card', { active: selectedSector === sector.name, hot: sector.heat > 80 }]"
        :style="{ animationDelay: `${0.75 + idx * 0.08}s` }" @click="selectedSector = sector.name">
        <div class="sector-heat">
          <span class="sector-name"><el-icon :size="16" class="fire-icon"><Sunny /></el-icon> {{ sector.name }}</span>
          <span class="heat-value"><CountUp :target="sector.heat" :decimals="0" /></span>
        </div>
        <el-progress :percentage="sector.heat" :color="sector.heat > 80 ? ['#ff6b6b','#f56c6c'] : sector.heat > 60 ? ['#ffd93d','#e6a23c'] : ['#67c23a','#85ce61']" :stroke-width="6" :show-text="false" class="sector-progress" />
        <div class="sector-change" :class="sector.change_pct >= 0 ? 'up' : 'down'">
          <el-icon :size="12"><Top v-if="sector.change_pct >= 0" /><Bottom v-else /></el-icon>
          {{ Math.abs(sector.change_pct).toFixed(1) }}%
        </div>
      </el-card>
      <div v-if="boardSectors.length === 0" class="empty-tip">
        <el-icon :size="48" color="#c0c4cc"><Document /></el-icon><p>暂无数据，请点击"立即分析"</p>
      </div>
    </div>

    <!-- 板块股票列表 -->
    <div class="section-title animate-in" style="animation-delay: 0.9s"><el-icon :size="20"><List /></el-icon> {{ selectedSector || '全部' }}板块选股详情</div>
    <el-card shadow="never" class="stock-card-wrap animate-in" style="animation-delay: 0.95s">
      <el-table :data="stockList" stripe class="stock-table" :row-class-name="tableRowClassName">
        <el-table-column prop="rank" label="排名" width="60">
          <template #default="{ row }"><span :class="['rank-badge', `rank-${row.rank}`]">{{ row.rank }}</span></template>
        </el-table-column>
        <el-table-column prop="code" label="代码" width="90" />
        <el-table-column prop="name" label="名称" width="100" />
        <el-table-column label="板块" width="80">
          <template #default="{ row }">
            <el-tag size="small" type="primary" effect="plain">{{ row._sector }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="类别" width="80">
          <template #default="{ row }">
            <el-tag size="small" :type="boardTagType[row._board] || 'info'" effect="dark">
              {{ boardLabelMap[row._board] || '其他' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="price" label="现价" width="90">
          <template #default="{ row }"><span :class="row.change_pct >= 0 ? 'up' : 'down'">¥{{ row.price?.toFixed(2) }}</span></template>
        </el-table-column>
        <el-table-column prop="change_pct" label="涨跌幅" width="90">
          <template #default="{ row }"><span :class="row.change_pct >= 0 ? 'up' : 'down'">{{ row.change_pct >= 0 ? '+' : '' }}{{ row.change_pct?.toFixed(1) }}%</span></template>
        </el-table-column>
        <el-table-column prop="total_score" label="评分" width="80">
          <template #default="{ row }"><el-tag :type="row.rating === 'A+' ? 'danger' : row.rating === 'A' ? 'warning' : 'info'" size="small" effect="dark">{{ row.total_score }}</el-tag></template>
        </el-table-column>
        <el-table-column prop="rating" label="评级" width="70">
          <template #default="{ row }"><el-tag :type="row.rating === 'A+' ? 'danger' : row.rating === 'A' ? 'warning' : 'info'" size="small" effect="plain">{{ row.rating }}</el-tag></template>
        </el-table-column>
        <el-table-column label="操作" width="80"><template #default="{ row }"><el-button size="small" type="primary" link @click="viewDetail(row)">详情</el-button></template></el-table-column>
      </el-table>

      <div class="stock-cards-mobile">
        <div v-for="stock in stockList" :key="stock.code" class="stock-card-mobile" @click="viewDetail(stock)">
          <div class="stock-header">
            <span :class="['stock-rank', `rank-${stock.rank}`]">{{ stock.rank }}</span>
            <span class="stock-code">{{ stock.code }}</span>
            <span class="stock-name">{{ stock.name }}</span>
            <el-tag size="small" :type="boardTagType[stock._board] || 'info'" effect="dark" class="board-tag">
              {{ boardLabelMap[stock._board] || '其他' }}
            </el-tag>
          </div>
          <div class="stock-meta">
            <el-tag size="small" type="primary" effect="plain">{{ stock._sector }}</el-tag>
          </div>
          <div class="stock-body">
            <div class="stock-price">
              <span :class="['price-value', stock.change_pct >= 0 ? 'up' : 'down']">¥{{ stock.price?.toFixed(2) }}</span>
              <span :class="['price-change', stock.change_pct >= 0 ? 'up' : 'down']">{{ stock.change_pct >= 0 ? '+' : '' }}{{ stock.change_pct?.toFixed(1) }}%</span>
            </div>
            <div class="stock-score"><el-tag :type="stock.rating === 'A+' ? 'danger' : stock.rating === 'A' ? 'warning' : 'info'" size="small" effect="dark">{{ stock.total_score }}分 {{ stock.rating }}</el-tag></div>
          </div>
          <div class="stock-detail-link"><el-icon><ArrowRight /></el-icon> 查看详情</div>
        </div>
        <div v-if="stockList.length === 0" class="empty-tip"><el-icon :size="48" color="#c0c4cc"><Document /></el-icon><p>暂无股票数据</p></div>
      </div>
    </el-card>

    <!-- 底部统计 -->
    <el-row :gutter="12" class="stats-bar animate-in" style="animation-delay: 1.1s">
      <el-col :xs="12" :sm="6" :md="6"><el-card shadow="never" class="stat-card stat-a"><el-icon :size="24" color="#f56c6c"><Trophy /></el-icon><span class="stat-label">A+ 优质</span><span class="stat-value"><CountUp :target="boardStats['A+'] || 0" :decimals="0" /></span></el-card></el-col>
      <el-col :xs="12" :sm="6" :md="6"><el-card shadow="never" class="stat-card stat-b"><el-icon :size="24" color="#e6a23c"><Medal /></el-icon><span class="stat-label">A 良好</span><span class="stat-value"><CountUp :target="boardStats['A'] || 0" :decimals="0" /></span></el-card></el-col>
      <el-col :xs="12" :sm="6" :md="6"><el-card shadow="never" class="stat-card stat-c"><el-icon :size="24" color="#409eff"><Collection /></el-icon><span class="stat-label">B 一般</span><span class="stat-value"><CountUp :target="boardStats['B'] || 0" :decimals="0" /></span></el-card></el-col>
      <el-col :xs="12" :sm="6" :md="6"><el-card shadow="never" class="stat-card stat-d"><el-icon :size="24" color="#909399"><Files /></el-icon><span class="stat-label">C 较弱</span><span class="stat-value"><CountUp :target="boardStats['C'] || 0" :decimals="0" /></span></el-card></el-col>
    </el-row>
  </div>
</template>

<script>
import { h, ref, watch, onMounted } from 'vue'
export default {
  components: {
    CountUp: {
      props: { target: { type: Number, default: 0 }, decimals: { type: Number, default: 2 }, duration: { type: Number, default: 1200 } },
      setup(props) {
        const display = ref(0)
        let anim = null
        const run = (t) => {
          cancelAnimationFrame(anim)
          if (!t && t !== 0) { display.value = 0; return }
          const s = display.value, t0 = performance.now()
          const tick = (now) => {
            const p = Math.min((now - t0) / props.duration, 1)
            const e = p === 1 ? 1 : 1 - Math.pow(2, -10 * p)
            display.value = s + (t - s) * e
            if (p < 1) anim = requestAnimationFrame(tick)
          }
          anim = requestAnimationFrame(tick)
        }
        watch(() => props.target, run, { immediate: true })
        onMounted(() => run(props.target))
        return () => h('span', display.value.toFixed(props.decimals))
      }
    }
  }
}
</script>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessageBox } from 'element-plus'
import { useDashboardStore } from '../stores/dashboard'
import {
  TrendCharts, Histogram, DataLine, Sort, Top, Bottom,
  Coin, Clock, Refresh, StarFilled, Sunny, Document, List,
  OfficeBuilding, Cpu, Monitor, Trophy, Medal, Collection, Files,
  ArrowRight
} from '@element-plus/icons-vue'

const store = useDashboardStore()
const router = useRouter()
const selectedSector = ref('')
const activeBoard = ref('main')
const boardLabels = { main: '主板', chinext: '创业板', star: '科创板' }
const boardLabelMap = { main: '主板', chinext: '创业板', star: '科创板' }
const customColors = [{ color: '#409eff', percentage: 33 }, { color: '#e6a23c', percentage: 66 }, { color: '#67c23a', percentage: 100 }]
const boardSectors = computed(() => store.boardSectors[activeBoard.value] || [])
const boardStats = computed(() => store.boardStats[activeBoard.value] || {})

// 按股票代码判断所属类别
const getBoard = (code) => {
  if (!code) return 'other'
  if (code.startsWith('60') || code.startsWith('00')) return 'main'
  if (code.startsWith('30')) return 'chinext'
  if (code.startsWith('68')) return 'star'
  return 'other'
}
const boardTagType = { main: 'danger', chinext: 'warning', star: '', other: 'info' }

const stockList = computed(() => {
  // 按选中的板块过滤
  const target = selectedSector.value
  const sectors = target ? boardSectors.value.filter(s => s.name === target) : boardSectors.value
  const r = []
  for (const s of sectors) {
    if (s.stocks) {
      s.stocks.forEach((x, i) => r.push({
        rank: i + 1,
        ...x,
        _sector: s.name,
        _board: getBoard(x.code),
      }))
    }
  }
  return r
})
const tableRowClassName = ({ rowIndex }) => rowIndex < 3 ? 'top-row' : ''
const triggerAnalysis = async () => {
  try {
    await ElMessageBox.confirm(
      '全量分析将遍历 A 股 5000+ 只股票，预计耗时 <b>3~5 分钟</b>。确定开始？',
      '⚠️ 确认分析',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        dangerouslyUseHTMLString: true,
        type: 'info',
      }
    )
    store.startAnalysis()
  } catch {
    // 用户取消
  }
}
const switchBoard = (b) => { activeBoard.value = b }
const viewDetail = (row) => { router.push({ name: 'StockDetail', params: { code: row.code } }) }
onMounted(() => store.fetchDashboard())
</script>

<style scoped>
@keyframes slideUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
.animate-in { animation: slideUp 0.6s ease-out both; }
@keyframes pulse { 0%,100% { box-shadow: 0 0 0 0 rgba(245,108,108,0.4); } 50% { box-shadow: 0 0 0 8px rgba(245,108,108,0); } }

.dashboard { max-width: 1400px; margin: 0 auto; padding: 0 16px; }
.market-bar { margin-bottom: 16px; }
.market-card { border-radius: 12px; transition: all 0.3s cubic-bezier(0.4,0,0.2,1); cursor: default; }
.market-card:hover { transform: translateY(-4px) scale(1.02); box-shadow: 0 8px 25px rgba(0,0,0,0.12); }
.market-card.up { border-top: 3px solid #f56c6c; }
.market-card.down { border-top: 3px solid #67c23a; }
.card-header { display: flex; align-items: center; gap: 6px; font-weight: 500; }
.index-value { font-size: 26px; font-weight: 700; transition: color 0.3s; }
.index-change { font-size: 14px; margin-top: 6px; display: flex; align-items: center; gap: 4px; }
.up .index-value, .up .index-change { color: #f56c6c; }
.down .index-value, .down .index-change { color: #67c23a; }
.up-down { display: flex; gap: 16px; font-size: 14px; font-weight: 600; align-items: center; }
.up-text { color: #f56c6c; display: flex; align-items: center; gap: 2px; }
.down-text { color: #67c23a; display: flex; align-items: center; gap: 2px; }
.volume { color: #999; font-size: 12px; margin-top: 6px; display: flex; align-items: center; gap: 4px; }

.status-card { margin-bottom: 16px; border-radius: 12px; }
.status-row { display: flex; justify-content: space-between; align-items: center; }
.status-info { font-size: 14px; display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }
.elapsed-badge { margin-left: 8px; }
.status-icon { color: #409eff; }
.analyze-btn { min-width: 120px; }
.progress-text { font-size: 12px; color: #606266; }

.section-title { font-size: 18px; font-weight: 600; margin: 20px 0 12px; display: flex; align-items: center; gap: 8px; }
.board-tabs { display: flex; gap: 8px; margin-bottom: 16px; flex-wrap: wrap; }
.board-tab { padding: 8px 20px; border-radius: 8px; cursor: pointer; background: #f5f7fa; color: #606266; font-size: 14px; font-weight: 500; transition: all 0.3s; user-select: none; display: flex; align-items: center; gap: 6px; }
.board-tab:hover { background: #e8eaf0; transform: translateY(-1px); }
.board-tab.active { background: linear-gradient(135deg,#409eff,#66b1ff); color: #fff; box-shadow: 0 2px 8px rgba(64,158,255,0.3); }
.tab-count { font-size: 12px; opacity: 0.8; }

.sector-cards { display: flex; gap: 12px; overflow-x: auto; padding-bottom: 8px; scroll-snap-type: x mandatory; }
.sector-card { min-width: 180px; cursor: pointer; border-radius: 12px; transition: all 0.3s cubic-bezier(0.4,0,0.2,1); scroll-snap-align: start; animation: slideUp 0.5s ease-out both; }
.sector-card:hover { transform: translateY(-4px); box-shadow: 0 8px 25px rgba(0,0,0,0.12); }
.sector-card.active { border: 2px solid #409eff; }
.sector-card.hot { animation: pulse 2s ease-in-out infinite, slideUp 0.5s ease-out both; }
.sector-heat { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.sector-name { font-weight: 600; font-size: 16px; display: flex; align-items: center; gap: 4px; }
.fire-icon { color: #f56c6c; }
.heat-value { font-size: 22px; font-weight: 700; background: linear-gradient(135deg,#667eea,#764ba2); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.sector-change { font-size: 12px; margin-top: 8px; display: flex; align-items: center; gap: 3px; }
.sector-change.up { color: #f56c6c; }
.sector-change.down { color: #67c23a; }

.rank-badge { display: inline-flex; align-items: center; justify-content: center; width: 24px; height: 24px; border-radius: 50%; font-size: 12px; font-weight: 700; background: #f0f0f0; color: #909399; }
.rank-1 { background: linear-gradient(135deg,#ffd700,#ffb300) !important; color: #fff !important; }
.rank-2 { background: linear-gradient(135deg,#c0c0c0,#a0a0a0) !important; color: #fff !important; }
.rank-3 { background: linear-gradient(135deg,#cd7f32,#b87333) !important; color: #fff !important; }
.top-row { background: #fdf6ec !important; }

.stock-table { display: block; }
.stock-cards-mobile { display: none; }
.board-tag { margin-left: auto; }

.stats-bar { margin-top: 20px; }
.stat-card { text-align: center; border-radius: 12px; padding: 16px 8px; transition: all 0.3s cubic-bezier(0.4,0,0.2,1); position: relative; overflow: hidden; }
.stat-card:hover { transform: translateY(-4px); box-shadow: 0 8px 25px rgba(0,0,0,0.1); }
.stat-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px; }
.stat-a::before { background: linear-gradient(90deg,#f56c6c,#ff6b6b); }
.stat-b::before { background: linear-gradient(90deg,#e6a23c,#ffd93d); }
.stat-c::before { background: linear-gradient(90deg,#409eff,#66b1ff); }
.stat-d::before { background: linear-gradient(90deg,#909399,#c0c4cc); }
.stat-label { display: block; color: #999; font-size: 12px; margin-top: 8px; }
.stat-value { display: block; font-size: 28px; font-weight: 700; margin-top: 4px; }

.empty-tip { text-align: center; padding: 40px 0; color: #909399; }
.empty-tip p { margin-top: 12px; font-size: 14px; }

@media (max-width:1024px) { .index-value { font-size: 22px; } .heat-value { font-size: 20px; } .sector-card { min-width: 160px; } .stat-value { font-size: 24px; } }
@media (max-width:768px) {
  .dashboard { padding: 0 8px; } .market-bar { margin-bottom: 12px; } .market-bar .el-col { margin-bottom: 8px; }
  .market-card:hover { transform: none; } .index-value { font-size: 18px; } .index-change { font-size: 12px; }
  .up-down { font-size: 12px; gap: 10px; } .volume { font-size: 11px; }
  .status-row { flex-direction: column; align-items: flex-start; gap: 8px; } .status-info { font-size: 12px; } .analyze-btn { width: 100%; }
  .section-title { font-size: 16px; margin: 16px 0 8px; } .board-tab { padding: 6px 14px; font-size: 13px; }
  .sector-cards { flex-direction: column; overflow-x: visible; gap: 8px; } .sector-card { min-width: 100%; }
  .sector-heat { margin-bottom: 6px; } .sector-name { font-size: 14px; } .heat-value { font-size: 18px; }
  .stock-table { display: none; } .stock-cards-mobile { display: block; }
  .stock-detail-link { text-align: center; color: #409eff; font-size: 12px; margin-top: 8px; padding: 4px 0; display: flex; align-items: center; justify-content: center; gap: 4px; }
  .stock-card-mobile:active { background: #fafafa; } .stock-card-mobile:last-child { border-bottom: none; }
  .stock-header { display: flex; align-items: center; gap: 8px; margin-bottom: 6px; }
  .stock-meta { margin-bottom: 6px; }
  .board-tag { margin-left: auto; }
  .stock-rank { display: inline-flex; align-items: center; justify-content: center; width: 22px; height: 22px; border-radius: 50%; font-size: 11px; font-weight: 700; background: #f5f7fa; color: #909399; }
  .stock-rank.rank-1 { background: linear-gradient(135deg,#ffd700,#ffb300) !important; color: #fff !important; }
  .stock-rank.rank-2 { background: linear-gradient(135deg,#c0c0c0,#a0a0a0) !important; color: #fff !important; }
  .stock-rank.rank-3 { background: linear-gradient(135deg,#cd7f32,#b87333) !important; color: #fff !important; }
  .stock-code { font-family: monospace; font-size: 13px; color: #909399; } .stock-name { font-size: 14px; font-weight: 600; }
  .stock-body { display: flex; justify-content: space-between; align-items: center; } .stock-price { display: flex; flex-direction: column; }
  .price-value { font-size: 16px; font-weight: 700; } .price-change { font-size: 12px; } .stock-score { display: flex; align-items: center; }
  .stats-bar { margin-top: 16px; } .stat-label { font-size: 11px; } .stat-value { font-size: 20px; } .stat-card { padding: 12px 8px; } .stat-card:hover { transform: none; }
}
@media (max-width:480px) { .index-value { font-size: 16px; } .index-change { font-size: 11px; } .board-tab { padding: 5px 10px; font-size: 12px; } .tab-count { display: none; } .price-value { font-size: 14px; } .stock-name { font-size: 13px; } .stat-value { font-size: 18px; } }
</style>
