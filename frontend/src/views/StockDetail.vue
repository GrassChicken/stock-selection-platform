<template>
  <div class="stock-detail">
    <div v-if="loading" class="loading-wrap">
      <el-icon :size="40" class="loading-icon"><Loading /></el-icon>
      <p>正在获取 {{ code }} 的评分数据...</p>
    </div>
    <div v-else-if="stock" class="detail-content">
      <!-- 股票头部 -->
      <div class="stock-header">
        <el-button class="back-btn" @click="$router.back()">← 返回</el-button>
        <div class="stock-info">
          <h1>{{ stock.name }} <span class="stock-code">{{ stock.code }}</span></h1>
          <div class="stock-price-row">
            <span class="stock-price">¥{{ stock.price.toFixed(2) }}</span>
            <span :class="['stock-change', stock.change_pct >= 0 ? 'up' : 'down']">
              {{ stock.change_pct >= 0 ? '+' : '' }}{{ stock.change_pct.toFixed(2) }}%
            </span>
          </div>
          <el-tag size="large" :type="stock.rating === 'A+' ? 'danger' : stock.rating === 'A' ? 'warning' : stock.rating === 'B' ? '' : 'info'" effect="dark" class="rating-tag">
            总分 {{ stock.total_score }} {{ stock.rating }}级
          </el-tag>
        </div>
      </div>

      <!-- 基本信息 -->
      <el-card class="info-card" shadow="never">
        <template #header>📋 基本信息</template>
        <el-descriptions :column="3" border>
          <el-descriptions-item label="行业">{{ stock.industry || '--' }}</el-descriptions-item>
          <el-descriptions-item label="总市值">{{ stock.total_market_cap ? stock.total_market_cap + '亿' : '--' }}</el-descriptions-item>
          <el-descriptions-item label="流通市值">{{ stock.float_market_cap ? stock.float_market_cap + '亿' : '--' }}</el-descriptions-item>
          <el-descriptions-item label="PE">{{ stock.pe || '--' }}</el-descriptions-item>
          <el-descriptions-item label="PB">{{ stock.pb || '--' }}</el-descriptions-item>
          <el-descriptions-item label="分红">{{ stock.has_dividend ? '✅ 有' : '❌ 无' }}</el-descriptions-item>
        </el-descriptions>
      </el-card>

      <!-- 评分总览 -->
      <el-card class="score-overview" shadow="never">
        <template #header>📊 评分总览</template>
        <el-row :gutter="16">
          <el-col :xs="24" :md="8">
            <div class="score-item fundamental">
              <div class="score-label">基本面</div>
              <div class="score-value">{{ stock.fundamental_score }}<span class="score-max">/50</span></div>
              <el-progress :percentage="stock.fundamental_score / 50 * 100" :color="getScoreColor(stock.fundamental_score, 50)" :stroke-width="8" />
            </div>
          </el-col>
          <el-col :xs="24" :md="8">
            <div class="score-item technical">
              <div class="score-label">技术面</div>
              <div class="score-value">{{ stock.technical_score }}<span class="score-max">/30</span></div>
              <el-progress :percentage="stock.technical_score / 30 * 100" :color="getScoreColor(stock.technical_score, 30)" :stroke-width="8" />
            </div>
          </el-col>
          <el-col :xs="24" :md="8">
            <div class="score-item capital">
              <div class="score-label">资金面</div>
              <div class="score-value">{{ stock.capital_score }}<span class="score-max">/20</span></div>
              <el-progress :percentage="stock.capital_score / 20 * 100" :color="getScoreColor(stock.capital_score, 20)" :stroke-width="8" />
            </div>
          </el-col>
        </el-row>
      </el-card>

      <!-- 评分明细 -->
      <el-row :gutter="16">
        <el-col :xs="24" :md="8">
          <el-card class="detail-card" shadow="never">
            <template #header>📈 基本面明细 <el-tag size="small" type="danger">{{ stock.fundamental_score }}/50</el-tag></template>
            <div class="detail-list">
              <div v-for="(item, key) in fundamentalItems" :key="key" class="detail-row">
                <span class="detail-name">{{ item.name }}</span>
                <span class="detail-value">{{ formatValue(item.value, key) }}</span>
                <span class="detail-score">{{ item.score }}/{{ item.max }}</span>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :xs="24" :md="8">
          <el-card class="detail-card" shadow="never">
            <template #header>📉 技术面明细 <el-tag size="small" type="warning">{{ stock.technical_score }}/30</el-tag></template>
            <div class="detail-list">
              <div v-for="(item, key) in technicalItems" :key="key" class="detail-row">
                <span class="detail-name">{{ item.name }}</span>
                <span class="detail-value">{{ formatValue(item.value, key) }}</span>
                <span class="detail-score">{{ item.score }}/{{ item.max }}</span>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :xs="24" :md="8">
          <el-card class="detail-card" shadow="never">
            <template #header>💰 资金面明细 <el-tag size="small" type="info">{{ stock.capital_score }}/20</el-tag></template>
            <div class="detail-list">
              <div v-for="(item, key) in capitalItems" :key="key" class="detail-row">
                <span class="detail-name">{{ item.name }}</span>
                <span class="detail-value">{{ formatValue(item.value, key) }}</span>
                <span class="detail-score">{{ item.score }}/{{ item.max }}</span>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
    <el-empty v-else description="未找到该股票数据" />
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { Loading } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import api from '../api/request'

const route = useRoute()
const code = computed(() => route.params.code || route.query.code || '')
const stock = ref(null)
const loading = ref(true)

// 评分明细配置
const fundLabels = {
  roe: 'ROE净资产收益率', profit_growth: '净利润增长率', pe_pct: 'PE行业分位',
  ocf: '经营现金流', debt: '资产负债率', gross_margin: '毛利率', dividend: '分红',
}
const techLabels = {
  ma: '均线排列', macd: 'MACD金叉', rsi: 'RSI指标', vol_ratio: '量比', above_ma20: '站上MA20',
  ma5: 'MA5', ma10: 'MA10', ma20: 'MA20', ma60: 'MA60', ma_bullish: '多头排列',
  macd_dif: 'DIF', macd_dea: 'DEA', macd_golden: 'MACD金叉',
}
const capLabels = {
  main_inflow: '主力净流入', margin: '融资余额', rating: '机构评级',
}

const parseDetails = (details, labels) => {
  const items = {}
  for (const [key, label] of Object.entries(labels)) {
    const d = details[key]
    if (d && typeof d === 'object' && 'score' in d) {
      items[key] = { name: label, value: d.value, score: d.score, max: d.max }
    } else if (d !== undefined) {
      items[key] = { name: label, value: d, score: '-', max: '-' }
    }
  }
  return items
}

const fundamentalItems = computed(() => parseDetails(stock.value?.fundamental_details || {}, fundLabels))
const technicalItems = computed(() => parseDetails(stock.value?.technical_details || {}, techLabels))
const capitalItems = computed(() => parseDetails(stock.value?.capital_details || {}, capLabels))

const getScoreColor = (score, max) => {
  const pct = score / max
  if (pct >= 0.8) return '#67c23a'
  if (pct >= 0.5) return '#e6a23c'
  return '#f56c6c'
}

const formatValue = (val, key) => {
  if (val === undefined || val === null || val === '-') return '--'
  if (typeof val === 'boolean') return val ? '✅' : '❌'
  const n = parseFloat(val)
  if (isNaN(n)) return val
  const unitKeys = ['roe', 'profit_growth', 'revenue_growth', 'gross_margin', 'debt_ratio', 'rsi']
  if (unitKeys.includes(key)) return n.toFixed(1) + (key === 'rsi' ? '' : '%')
  if (key === 'vol_ratio') return n.toFixed(2)
  if (key === 'ocf') return n.toFixed(1) + '亿'
  return n.toFixed(2)
}

const fetchStock = async (c) => {
  if (!c) { loading.value = false; return }
  loading.value = true
  try {
    const data = await api.get('/api/stock', { params: { code: c } })
    stock.value = data
  } catch (e) {
    ElMessage.error('获取股票数据失败: ' + (e.response?.data?.detail || e.message))
  } finally { loading.value = false }
}

watch(code, (c) => fetchStock(c), { immediate: true })
</script>

<style scoped>
.stock-detail { max-width: 1200px; margin: 0 auto; }
.loading-wrap { text-align: center; padding: 80px 0; }
.loading-icon { animation: spin 1s linear infinite; color: #409eff; }
@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }

.stock-header { display: flex; align-items: flex-start; gap: 20px; margin-bottom: 20px; }
.back-btn { flex-shrink: 0; }
.stock-info h1 { font-size: 24px; margin: 0 0 8px; }
.stock-code { font-size: 14px; color: #999; font-weight: normal; }
.stock-price-row { display: flex; align-items: baseline; gap: 12px; margin-bottom: 8px; }
.stock-price { font-size: 32px; font-weight: 700; }
.stock-change { font-size: 16px; font-weight: 600; }
.up { color: #f56c6c; } .down { color: #67c23a; }
.rating-tag { font-size: 16px !important; padding: 8px 16px !important; }

.info-card { margin-bottom: 16px; border-radius: 12px; }
.score-overview { margin-bottom: 16px; border-radius: 12px; }
.score-item { text-align: center; padding: 16px; }
.score-label { font-size: 14px; color: #606266; margin-bottom: 8px; }
.score-value { font-size: 28px; font-weight: 700; margin-bottom: 8px; }
.score-max { font-size: 14px; color: #999; font-weight: normal; }
.fundamental .score-value { color: #f56c6c; }
.technical .score-value { color: #e6a23c; }
.capital .score-value { color: #409eff; }

.detail-card { border-radius: 12px; margin-bottom: 16px; }
.detail-list { max-height: 300px; overflow-y: auto; }
.detail-row { display: flex; justify-content: space-between; align-items: center; padding: 6px 0; border-bottom: 1px solid #f0f0f0; }
.detail-row:last-child { border-bottom: none; }
.detail-name { font-size: 13px; color: #606266; flex: 1; }
.detail-value { font-size: 13px; font-weight: 600; color: #303133; min-width: 60px; text-align: right; }
.detail-score { font-size: 12px; color: #909399; min-width: 45px; text-align: right; margin-left: 8px; }

@media (max-width: 768px) {
  .stock-price { font-size: 24px; }
  .score-value { font-size: 22px; }
}
</style>
