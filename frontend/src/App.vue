<template>
  <el-container class="app-container">
    <el-header class="app-header">
      <div class="header-left">
        <span class="logo">🦐</span>
        <span class="title">智能选股平台</span>
      </div>
      <div class="header-right">
        <div class="search-wrapper">
          <el-input
            v-model="searchText"
            placeholder="搜索股票代码/名称"
            :prefix-icon="Search"
            clearable
            @input="onSearchInput"
            @focus="showDropdown = true"
          />
          <div v-if="showDropdown && searchResults.length > 0" class="search-dropdown">
            <div
              v-for="item in searchResults"
              :key="item.code"
              class="search-item"
              @click="selectStock(item)"
            >
              <div class="search-item-left">
                <span class="search-code">{{ item.code }}</span>
                <span class="search-name">{{ item.name }}</span>
              </div>
              <div class="search-item-right">
                <el-tag size="small" :type="item.rating === 'A+' ? 'danger' : item.rating === 'A' ? 'warning' : 'info'">
                  {{ item.total_score }} {{ item.rating }}
                </el-tag>
              </div>
            </div>
          </div>
        </div>
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
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { Search } from '@element-plus/icons-vue'
import { searchStocks } from './api/analyze'

const router = useRouter()

const searchText = ref('')
const searchResults = ref([])
const showDropdown = ref(false)
let searchTimer = null

const onSearchInput = () => {
  clearTimeout(searchTimer)
  if (!searchText.value.trim()) {
    searchResults.value = []
    showDropdown.value = false
    return
  }
  searchTimer = setTimeout(async () => {
    try {
      searchResults.value = await searchStocks(searchText.value.trim())
      showDropdown.value = true
    } catch {
      searchResults.value = []
    }
  }, 300)
}

const selectStock = (item) => {
  showDropdown.value = false
  searchText.value = ''
  searchResults.value = []
  router.push({ name: 'StockDetail', params: { code: item.code } })
}

const handleClickOutside = (e) => {
  const wrapper = document.querySelector('.search-wrapper')
  if (wrapper && !wrapper.contains(e.target)) {
    showDropdown.value = false
  }
}

onMounted(() => document.addEventListener('click', handleClickOutside))
onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
  clearTimeout(searchTimer)
})
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

/* 搜索框 */
.search-wrapper { position: relative; margin-right: 16px; }
.search-wrapper .el-input { width: 240px; }
.search-wrapper .el-input__wrapper { background: rgba(255,255,255,0.15); border: none; box-shadow: none; }
.search-wrapper .el-input__inner { color: #fff; }
.search-wrapper .el-input__inner::placeholder { color: rgba(255,255,255,0.6); }

.search-dropdown {
  position: absolute; top: 100%; left: 0; right: 0;
  background: #fff; border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.15);
  max-height: 400px; overflow-y: auto; z-index: 2000;
  margin-top: 4px;
}
.search-item {
  display: flex; align-items: center; justify-content: space-between;
  padding: 10px 16px; cursor: pointer; border-bottom: 1px solid #f0f0f0;
  transition: background 0.15s;
}
.search-item:last-child { border-bottom: none; }
.search-item:hover { background: #f5f7fa; }
.search-item-left { display: flex; align-items: center; gap: 10px; }
.search-code { font-family: monospace; font-weight: 600; color: #303133; font-size: 14px; }
.search-name { color: #606266; font-size: 14px; }
</style>
