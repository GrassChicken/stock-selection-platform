<template>
  <el-container class="app-container">
    <el-header class="app-header">
      <div class="header-left">
        <span class="logo">🦐</span>
        <span class="title">智能选股平台</span>
      </div>
      <div class="header-right">
        <el-input
          v-model="searchText"
          placeholder="搜索股票代码/名称"
          style="width: 200px; margin-right: 16px"
          size="small"
          clearable
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-button size="small" @click="$router.push('/settings')">⚙️ 设置</el-button>
      </div>
    </el-header>
    <el-main class="app-main">
      <router-view />
    </el-main>
    <el-footer class="app-footer">
      <span>🦐 智能选股平台 v0.1.0 | 数据仅供参考，不构成投资建议</span>
    </el-footer>
  </el-container>
</template>

<script setup>
import { ref } from 'vue'
import { Search } from '@element-plus/icons-vue'

const searchText = ref('')
</script>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f7fa; }
.app-container { min-height: 100vh; }
.app-header {
  display: flex; align-items: center; justify-content: space-between;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white; padding: 0 24px; box-shadow: 0 2px 12px rgba(0,0,0,0.1);
}
.header-left { display: flex; align-items: center; gap: 12px; }
.logo { font-size: 28px; }
.title { font-size: 20px; font-weight: 600; }
.app-main { padding: 24px; }
.app-footer {
  text-align: center; color: #999; font-size: 12px;
  background: white; border-top: 1px solid #eee;
}
</style>
