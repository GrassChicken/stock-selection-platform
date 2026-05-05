# 智能选股平台 — 模块化迭代开发计划

> 版本: v2.0 | 创建日期: 2026-05-05 | 目标端口: **5100**
> 策略: 小模块快速迭代，边开发边调试

---

## 当前状态 (2026-05-05)

| 模块 | 状态 | 说明 |
|------|------|------|
| Phase 0 项目骨架 | ✅ 完成 | 前后端骨架、依赖安装、路由注册 |
| L1 一票否决引擎 | ✅ 完成 | `l1_filter.py` 逻辑完整 |
| L2 量化评分引擎 | ✅ 完成 | `l2_scorer.py` 技术指标+评分完整 |
| 板块热度计算 | ✅ 完成 | `sector_heat.py` 分组逻辑完整 |
| 买卖点计算 | ✅ 完成 | `trade_points.py` 基础实现 |
| Pipeline 串联 | ✅ 完成 | `pipeline.py` L1→L2→板块分组跑通 |
| AKShare 数据源 | ⚠️ 部分 | `akshare_client.py` 行情OK，财务数据格式需适配 |
| 后端 API 路由 | ⚠️ 部分 | 路由全部注册，但返回 mock 数据 |
| 前端页面 | ⚠️ 部分 | Dashboard.vue/Settings.vue 有框架，stores/components/api 空 |
| 定时调度 | ⚠️ 部分 | APScheduler 已集成，定时任务 TODO 未接引擎 |

---

## 迭代清单

### M1: 修复 API 尾斜杠 + 启动验证 ✅
- [x] 所有路由 `/` 改为 `""` 兼容无尾斜杠
- [x] `get_stock_info` → `get_stock_basic_info` 导入修复
- [x] 后端重启成功，所有 API 返回 200
- [x] `/api/analyze` 手动触发跑通 (前100只股票)

---

### M2: 后端 API 接入真实引擎 🔴 下一步

**目标**: 所有 API 接口返回真实引擎数据，不再返回 mock

#### M2.1 `/api/dashboard` 首页数据
- 调用 `get_market_overview()` 获取大盘指数
- 调用 pipeline 或缓存获取板块热度 + 统计
- 返回: `{sh_index, sz_index, cy_index, up_count, down_count, total_volume, sectors, stats}`
- 预计改动: `dashboard.py` (~50行)

#### M2.2 `/api/sectors` 板块列表
- 调用 pipeline 或缓存获取板块热度排名
- 返回: `[{name, heat, change_pct, stock_count}]`
- 预计改动: `sectors.py` (~30行)

#### M2.3 `/api/sectors/{name}/stocks` 板块股票
- 按板块名筛选，返回 Top 10 评分股票
- 预计改动: `sectors.py` (~30行)

#### M2.4 `/api/stocks/{code}` 个股评分
- 调用 `grade_stock()` 获取实时评分
- 返回完整评分数据
- 预计改动: `stocks.py` (~30行)

#### M2.5 `/api/analyze` 分析进度优化
- 当前 pipeline 只取前100只，改为全量或分批
- 分析结果缓存，供 dashboard/sectors 使用
- 预计改动: `analyze.py` + `pipeline.py` (~80行)

**验收标准**: 前端 Dashboard.vue 能显示真实 A 股数据

---

### M3: AKShare 财务数据适配 🟡

**目标**: `akshare_client.py` 财务接口稳定可用

#### M3.1 财务摘要格式适配
- `stock_financial_abstract_ths` 返回字段映射
- 标准化为 `{roe, profit_growth, revenue_growth, pe, pb, gross_margin, debt_ratio, ...}`
- 预计改动: `akshare_client.py` (~60行)

#### M3.2 资金流向数据
- `stock_individual_fund_flow` 深/沪市自动判断
- 提取 `{main_net_inflow_5d, margin_balance_trend}`
- 预计改动: `akshare_client.py` (~40行)

#### M3.3 缓存层优化
- 行情数据缓存 (Redis/内存)
- 财务数据按股票缓存，避免重复请求
- 预计改动: `cache.py` (~50行)

---

### M4: 前端状态层 + API 封装 🟡

**目标**: 前端能调后端真实接口

#### M4.1 Axios 请求封装
- `frontend/src/api/request.js` — 统一 axios 实例 + 拦截器
- `frontend/src/api/dashboard.js` — 首页接口
- `frontend/src/api/sectors.js` — 板块接口
- `frontend/src/api/stocks.js` — 个股接口
- `frontend/src/api/analyze.js` — 分析控制接口
- 预计文件: 5 个 (~200行)

#### M4.2 Pinia 状态管理
- `frontend/src/stores/dashboard.js` — 大盘数据 + 板块列表
- `frontend/src/stores/analysis.js` — 分析进度 + 任务状态
- 预计文件: 2 个 (~100行)

#### M4.3 Dashboard.vue 接入真实数据
- 替换 mock 数据为 store 数据
- 板块切换联动股票列表
- 分析按钮触发真实分析
- 预计改动: `Dashboard.vue` (~50行)

---

### M5: 前端组件开发 🟡

**目标**: 可复用组件库

#### M5.1 个股详情抽屉
- `StockDetailDrawer.vue` — 评分雷达图 + 指标明细 + 买卖点
- 预计文件: 1 个 (~200行)

#### M5.2 ECharts 图表组件
- `ScoreRadar.vue` — 评分雷达图
- `KLineChart.vue` — K 线走势图
- 预计文件: 2 个 (~200行)

#### M5.3 分析进度条
- `AnalysisProgress.vue` — 步骤进度实时展示
- 预计文件: 1 个 (~100行)

---

### M6: 定时任务 + 通知 🟢

#### M6.1 定时分析接入引擎
- `scheduler.py` 调用 `run_full_analysis()`
- 交易日判断 (跳过节假日)
- 预计改动: `scheduler.py` (~40行)

#### M6.2 飞书通知
- 分析完成推送飞书消息
- 预计改动: `scheduler.py` + 通知工具 (~40行)

---

### M7: 性能优化 🟢

#### M7.1 评分引擎优化
- 批量获取 K 线数据 (减少 API 调用)
- 并行计算评分
- 预计改动: `pipeline.py` (~60行)

#### M7.2 分析结果缓存
- 评分结果缓存到 Redis/DB
- Dashboard 直接读缓存，不重复计算
- 预计改动: `cache.py` + `analyze.py` (~80行)

---

## 执行优先级

```
M2 (API接入引擎) → M3 (财务数据适配) → M4 (前端状态层) → M5 (前端组件) → M6 (定时任务) → M7 (性能优化)
  ↑ 最优先             ↑ 依赖M3           ↑ 依赖M2            ↑ 依赖M4            ↑ 可选增强
```

## 每次迭代流程
1. 明确当前模块任务
2. 编码 → 测试 → 重启验证
3. Git 提交
4. 汇报进度

---

*文档版本: v2.0 | 更新日期: 2026-05-05*
