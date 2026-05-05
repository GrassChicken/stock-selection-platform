<template>
  <div class="settings">
    <div class="settings-header">
      <el-button class="back-btn" @click="$router.push('/')">
        <el-icon><ArrowLeft /></el-icon>
        返回
      </el-button>
      <h2>⚙️ 系统设置</h2>
    </div>
    <el-row :gutter="24">
      <el-col :xs="24" :md="12">
        <el-card shadow="hover" style="border-radius: 12px">
          <template #header>⏰ 定时分析设置</template>
          <el-form label-width="120px">
            <el-form-item label="开启定时">
              <el-switch v-model="schedule.enabled" />
            </el-form-item>
            <el-form-item label="执行时间">
              <el-time-picker v-model="scheduleTime" format="HH:mm" placeholder="选择时间" />
            </el-form-item>
            <el-form-item label="执行日期">
              <el-checkbox-group v-model="schedule.weekdays">
                <el-checkbox :label="0">周一</el-checkbox>
                <el-checkbox :label="1">周二</el-checkbox>
                <el-checkbox :label="2">周三</el-checkbox>
                <el-checkbox :label="3">周四</el-checkbox>
                <el-checkbox :label="4">周五</el-checkbox>
              </el-checkbox-group>
            </el-form-item>
            <el-form-item label="完成后通知">
              <el-checkbox v-model="schedule.notify_feishu">飞书消息</el-checkbox>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveSchedule" :loading="saving">保存设置</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
      <el-col :xs="24" :md="12">
        <el-card shadow="hover" style="border-radius: 12px">
          <template #header>📊 评分权重配置</template>
          <el-alert v-if="weightTotal !== 100" :title="`权重总和 ${weightTotal}%，必须等于100%`" type="warning" show-icon :closable="false" style="margin-bottom: 16px" />
          <el-form label-width="100px">
            <el-form-item label="基本面">
              <el-slider v-model="weights.fundamental" :max="100" show-input />
            </el-form-item>
            <el-form-item label="技术面">
              <el-slider v-model="weights.technical" :max="100" show-input />
            </el-form-item>
            <el-form-item label="资金面">
              <el-slider v-model="weights.capital" :max="100" show-input />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveWeights" :loading="saving" :disabled="weightTotal !== 100">保存权重</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
    </el-row>
    <el-card shadow="hover" style="border-radius: 12px; margin-top: 24px">
      <template #header>📦 系统信息</template>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="后端地址">http://localhost:5100</el-descriptions-item>
        <el-descriptions-item label="前端地址">http://localhost:3000</el-descriptions-item>
        <el-descriptions-item label="Python 版本">3.11</el-descriptions-item>
        <el-descriptions-item label="Vue 版本">3.4</el-descriptions-item>
        <el-descriptions-item label="数据源">AKShare</el-descriptions-item>
        <el-descriptions-item label="数据库">SQLite</el-descriptions-item>
      </el-descriptions>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'
import { getSchedule, saveSchedule as apiSaveSchedule, getWeights, saveWeights as apiSaveWeights } from '../api/settings'

const schedule = ref({
  enabled: true,
  hour: 16,
  minute: 0,
  weekdays: [0, 1, 2, 3, 4],
  notify_feishu: true,
})
const scheduleTime = ref(new Date(2026, 0, 1, 16, 0))
const saving = ref(false)

const weights = ref({
  fundamental: 50,
  technical: 30,
  capital: 20,
})

const weightTotal = computed(() =>
  Math.round((weights.value.fundamental + weights.value.technical + weights.value.capital) * 10) / 10
)

const saveSchedule = async () => {
  saving.value = true
  try {
    const h = scheduleTime.value.getHours()
    const m = scheduleTime.value.getMinutes()
    await apiSaveSchedule({ ...schedule.value, hour: h, minute: m })
    ElMessage.success('定时设置已保存 ✅')
  } catch (e) {
    ElMessage.error('保存失败: ' + (e.response?.data?.detail || e.message))
  } finally {
    saving.value = false
  }
}

const saveWeights = async () => {
  if (weightTotal.value !== 100) {
    ElMessage.warning('权重总和必须等于100%')
    return
  }
  saving.value = true
  try {
    await apiSaveWeights(weights.value)
    ElMessage.success('权重配置已保存 ✅')
  } catch (e) {
    ElMessage.error('保存失败: ' + (e.response?.data?.detail || e.message))
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  try {
    const s = await getSchedule()
    schedule.value = s
    scheduleTime.value = new Date(2026, 0, 1, s.hour || 16, s.minute || 0)
  } catch {}
  try {
    const w = await getWeights()
    weights.value = w
  } catch {}
})
</script>

<style scoped>
.settings { max-width: 1200px; margin: 0 auto; }
.settings-header { display: flex; align-items: center; gap: 16px; margin-bottom: 20px; }
.settings-header h2 { margin: 0; font-size: 22px; }
.back-btn { display: flex; align-items: center; gap: 4px; }
</style>
