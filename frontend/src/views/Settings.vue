<template>
  <div class="settings">
    <h2>⚙️ 系统设置</h2>
    <el-row :gutter="24">
      <el-col :span="12">
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
              <el-button type="primary" @click="saveSchedule">保存设置</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="hover" style="border-radius: 12px">
          <template #header>📊 评分权重配置</template>
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
              <el-button type="primary" @click="saveWeights">保存权重</el-button>
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
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

const schedule = ref({
  enabled: true,
  hour: 16,
  minute: 0,
  weekdays: [0, 1, 2, 3, 4],
  notify_feishu: true,
})
const scheduleTime = ref(new Date(2026, 0, 1, 16, 0))

const weights = ref({
  fundamental: 50,
  technical: 30,
  capital: 20,
})

const saveSchedule = () => {
  ElMessage.success('定时设置已保存 ✅')
}

const saveWeights = () => {
  ElMessage.success('权重配置已保存 ✅')
}
</script>

<style scoped>
.settings { max-width: 1200px; margin: 0 auto; }
.settings h2 { margin-bottom: 20px; font-size: 22px; }
</style>
