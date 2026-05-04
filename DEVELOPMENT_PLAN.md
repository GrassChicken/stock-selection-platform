# 智能选股平台 — 开发计划

> 版本: v1.0 | 创建日期: 2026-05-04 | 目标端口: **5100**

---

## 一、技术栈最终确定

| 层级 | 方案 | 版本 | 说明 |
|------|------|------|------|
| 前端框架 | Vue 3 + Vite | 3.4+ | 组合式 API，轻量高效 |
| UI 组件库 | Element Plus | 2.5+ | 表格、卡片、表单、进度条 |
| 图表库 | Apache ECharts | 5.5+ | K线、雷达图、热力图、柱状图 |
| 状态管理 | Pinia | 2.1+ | 轻量级状态管理 |
| HTTP 客户端 | Axios | 1.6+ | 统一 API 请求 + 拦截器 |
| 后端框架 | FastAPI | 0.109+ | 异步高性能，自动 API 文档 |
| 评分引擎 | Python (原生) | 3.10+ | 与 FastAPI 同进程 |
| 调度器 | APScheduler | 3.10+ | 定时任务 (每日分析) |
| 缓存 | Redis | 7.x | 评分结果缓存、实时行情 |
| 数据库 | SQLite → PostgreSQL | — | 开发用 SQLite，生产切 PG |
| 数据源 | AKShare | 1.x | 免费 A 股数据 (行情/财务/资金) |
| Web 服务器 | Nginx (可选) | — | 静态文件 + 反向代理 |

---

## 二、项目目录结构

```
stock-selection-platform/
├── backend/                      # FastAPI 后端
│   ├── app/
│   │   ├── main.py              # FastAPI 入口
│   │   ├── config.py            # 配置管理 (端口 5100 等)
│   │   ├── models/              # 数据模型 (Pydantic)
│   │   │   ├── stock.py
│   │   │   ├── sector.py
│   │   │   └── analysis.py
│   │   ├── api/                  # API 路由
│   │   │   ├── dashboard.py     # 首页数据
│   │   │   ├── sectors.py       # 板块相关
│   │   │   ├── stocks.py        # 个股相关
│   │   │   ├── analyze.py       # 分析控制
│   │   │   └── schedule.py      # 定时任务管理
│   │   ├── engine/               # 核心评分引擎
│   │   │   ├── l1_filter.py     # L1 一票否决
│   │   │   ├── l2_scorer.py     # L2 量化评分
│   │   │   ├── sector_heat.py   # 板块热度计算
│   │   │   ├── trade_points.py  # 买卖点计算
│   │   │   └── llm_analyzer.py  # L3 AI 深度分析
│   │   ├── data/                 # 数据获取层
│   │   │   ├── akshare_client.py # AKShare 封装
│   │   │   ├── cache.py         # Redis 缓存
│   │   │   └── db.py            # 数据库操作
│   │   └── scheduler.py          # APScheduler 定时任务
│   ├── requirements.txt
│   └── .env                      # 环境变量
├── frontend/                     # Vue 3 前端
│   ├── src/
│   │   ├── main.js
│   │   ├── App.vue
│   │   ├── router/              # 路由配置
│   │   ├── stores/              # Pinia 状态
│   │   │   ├── dashboard.js
│   │   │   ├── sectors.js
│   │   │   └── analysis.js
│   │   ├── views/               # 页面组件
│   │   │   ├── Dashboard.vue    # 首页仪表盘
│   │   │   ├── Settings.vue     # 设置页
│   │   │   └── History.vue      # 历史记录
│   │   ├── components/          # 可复用组件
│   │   │   ├── MarketOverview.vue    # 大盘概览
│   │   │   ├── SectorHeatCards.vue   # 板块热度卡片
│   │   │   ├── StockTable.vue        # 股票列表表格
│   │   │   ├── StockDetailDrawer.vue # 个股详情抽屉
│   │   │   ├── AnalysisProgress.vue  # 分析进度条
│   │   │   ├── KLineChart.vue        # K线图表
│   │   │   ├── ScoreRadar.vue        # 评分雷达图
│   │   │   └── TradePointsCard.vue   # 买卖点卡片
│   │   ├── api/                 # API 请求封装
│   │   │   ├── request.js       # Axios 实例
│   │   │   ├── dashboard.js
│   │   │   ├── sectors.js
│   │   │   ├── stocks.js
│   │   │   └── analyze.js
│   │   ├── assets/              # 静态资源
│   │   │   └── styles/
│   │   └── utils/               # 工具函数
│   ├── package.json
│   ├── vite.config.js
│   └── index.html
├── docker-compose.yml           # Docker 编排 (可选)
├── deploy/                      # 部署脚本
│   ├── nginx.conf
│   ├── stock-platform.service   # systemd 服务文件
│   └── deploy.sh                # 一键部署脚本
└── docs/                        # 文档
    └── ARCHITECTURE.md
```

---

## 三、开发阶段规划

### Phase 0: 环境搭建与基础框架 (1-2 天)

**目标：前后端项目骨架就绪，能跑通 Hello World**

| 任务 | 产出 | 耗时 |
|------|------|------|
| 创建项目目录结构 | 完整目录树 | 0.5h |
| 后端 FastAPI 初始化 | main.py + 基础路由 + 端口 5100 | 1h |
| 前端 Vue 3 + Vite 初始化 | 项目脚手架 + Element Plus | 1h |
| 前后端联调通 | 前端调后端 /api/health 返回 OK | 0.5h |
| AKShare 数据源测试 | 验证能获取 A 股列表、行情、财务数据 | 2h |
| Redis 本地部署测试 | 缓存读写验证 | 1h |
| Git 仓库初始化 | README + .gitignore | 0.5h |

**里程碑：** `http://localhost:5100` 能访问到前端页面，后端 API 正常响应

---

### Phase 1: 数据层 + L1/L2 评分引擎 (3-4 天)

**目标：核心评分引擎跑通，能输出全量股票评分结果**

| 任务 | 产出 | 耗时 |
|------|------|------|
| AKShare 数据封装层 | akshare_client.py (行情/财务/资金) | 4h |
| 数据缓存策略 | Redis 缓存 + 失效策略 | 2h |
| L1 一票否决引擎 | l1_filter.py + 单元测试 | 3h |
| L2 基本面评分 | score_fundamental() + 测试 | 3h |
| L2 技术面评分 | score_technical() + 测试 | 3h |
| L2 资金面评分 | score_capital() + 测试 | 2h |
| 板块分组逻辑 | sector_heat.py + select_top_stocks() | 3h |
| 买卖点计算 | trade_points.py | 2h |
| 数据库模型设计 | SQLite 表结构 + SQLAlchemy | 3h |
| 完整流程串联 | L1 → L2 → 板块分组 → 入库 | 4h |

**里程碑：** 后端能一次性跑完 5400 只股票的过滤+评分+分组，输出结构化结果

---

### Phase 2: 后端 API 完整实现 (2-3 天)

**目标：所有 API 接口就绪，Swagger 文档可用**

| 任务 | 产出 | 耗时 |
|------|------|------|
| GET /api/dashboard | 大盘数据 + 统计信息 | 2h |
| GET /api/sectors | 板块热度排名列表 | 2h |
| GET /api/sectors/{name}/stocks | 板块 Top 10 股票 | 2h |
| GET /api/stocks/{code} | 个股评分和指标 | 2h |
| GET /api/stocks/{code}/chart | K 线数据 | 2h |
| GET /api/stocks/{code}/trade-points | 买卖点建议 | 1h |
| POST /api/analyze | 手动触发分析 | 2h |
| GET /api/analyze/status/{task_id} | 分析进度查询 | 2h |
| GET /api/schedule + PUT /api/schedule | 定时任务配置 | 2h |
| POST /api/analyze/ai/{code} | LLM 深度分析 | 3h |
| API 联调测试 | Postman / curl 验证所有接口 | 3h |

**里程碑：** `http://localhost:5100/api/docs` 能看到完整 Swagger 文档，所有接口可用

---

### Phase 3: 前端页面开发 (4-5 天)

**目标：完整 UI 页面开发完毕，能展示真实数据**

| 任务 | 产出 | 耗时 |
|------|------|------|
| 全局布局 + 导航栏 | App.vue + 顶部导航 | 2h |
| 大盘概览组件 | MarketOverview.vue | 2h |
| 分析状态栏 + 触发按钮 | AnalysisProgress.vue | 2h |
| 板块热度卡片组件 | SectorHeatCards.vue | 3h |
| 股票列表表格组件 | StockTable.vue | 3h |
| 个股详情抽屉组件 | StockDetailDrawer.vue | 4h |
| 评分雷达图组件 | ScoreRadar.vue (ECharts) | 3h |
| K 线图表组件 | KLineChart.vue (ECharts) | 3h |
| 买卖点卡片组件 | TradePointsCard.vue | 2h |
| 首页仪表盘页面 | Dashboard.vue (组装所有组件) | 4h |
| 设置页面 | Settings.vue (定时分析 + 权重配置) | 3h |
| 响应式适配 | 桌面/平板/移动端适配 | 3h |
| 主题和样式优化 | 全局 CSS + 暗色模式 (可选) | 2h |

**里程碑：** 前端页面完整可用，能展示后端真实数据

---

### Phase 4: 定时任务 + 实时推送 (1-2 天)

**目标：每日自动分析 + 前端实时进度展示**

| 任务 | 产出 | 耗时 |
|------|------|------|
| APScheduler 集成 | scheduler.py + 每日 16:00 触发 | 2h |
| 分析任务进度管理 | 任务状态表 + WebSocket 推送 | 3h |
| 前端进度实时更新 | AnalysisProgress.vue 轮询/WebSocket | 2h |
| 分析完成通知 | 飞书消息推送 (可选) | 2h |
| 交易日判断 | 跳过节假日/周末 | 1h |

**里程碑：** 每天 16:00 自动执行分析，前端能实时看到进度

---

### Phase 5: 部署上线 (1-2 天)

**目标：生产环境部署，端口 5100 对外服务**

| 任务 | 产出 | 耗时 |
|------|------|------|
| 生产环境配置 | .env.production + config.py | 1h |
| Nginx 配置 | nginx.conf (静态文件 + 反向代理) | 1h |
| systemd 服务文件 | stock-platform.service | 1h |
| 一键部署脚本 | deploy.sh | 2h |
| Redis 生产部署 | redis.conf 优化 | 1h |
| 数据库迁移 | SQLite → PostgreSQL (可选) | 2h |
| 防火墙开放 5100 端口 | iptables / firewall-cmd | 0.5h |
| 端到端测试 | 全流程验证 | 2h |
| 监控和日志 | 日志轮转 + 健康检查 | 1h |

**里程碑：** `http://<服务器IP>:5100` 对外可用

---

### Phase 6: 优化迭代 (持续)

**目标：性能优化、功能增强、用户体验提升**

| 任务 | 说明 | 优先级 |
|------|------|--------|
| 评分引擎性能优化 | 批量计算、并行处理 | P0 |
| 前端加载速度优化 | 代码分割、懒加载 | P1 |
| 暗色主题 | 夜间模式 | P2 |
| 自选股功能 | 用户收藏股票 | P1 |
| 预警推送 | 止盈止损/异动飞书通知 | P1 |
| 历史趋势分析 | 评分历史走势图表 | P2 |
| 多用户权限 | 登录/注册/角色 | P2 |
| 移动端 App | PWA 或小程序 | P3 |

---

## 四、时间线总览

```
第 1 周 (Mon-Fri)
├── Mon-Tue: Phase 0 - 环境搭建 + 基础框架
├── Wed-Fri: Phase 1 - 数据层 + L1/L2 评分引擎

第 2 周 (Mon-Fri)
├── Mon-Wed: Phase 2 - 后端 API 完整实现
├── Thu-Fri: Phase 3 (前半) - 前端核心组件

第 3 周 (Mon-Fri)
├── Mon-Wed: Phase 3 (后半) - 前端页面完成
├── Thu-Fri: Phase 4 - 定时任务 + 实时推送

第 4 周 (Mon-Fri)
├── Mon-Wed: Phase 5 - 部署上线 (端口 5100)
├── Thu-Fri: 端到端测试 + 问题修复 + Phase 6 规划

预计总工期: 3-4 周 (核心功能可用)
```

---

## 五、部署配置 (端口 5100)

### 5.1 后端配置
```python
# backend/app/config.py
APP_HOST = "0.0.0.0"
APP_PORT = 5100
REDIS_URL = "redis://localhost:6379/0"
DB_URL = "sqlite:///./stock_platform.db"  # 开发环境
# DB_URL = "postgresql://user:pass@localhost:5432/stock_platform"  # 生产
```

### 5.2 启动命令
```bash
# 直接启动 (开发)
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 5100 --reload

# 生产启动 (后台运行)
nohup uvicorn app.main:app --host 0.0.0.0 --port 5100 --workers 4 > stock.log 2>&1 &
```

### 5.3 systemd 服务
```ini
# /etc/systemd/system/stock-platform.service
[Unit]
Description=智能选股平台
After=network.target redis.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/stock-selection-platform/backend
Environment="PATH=/opt/stock-selection-platform/venv/bin"
ExecStart=/opt/stock-selection-platform/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 5100 --workers 4
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### 5.4 访问方式
```
开发环境: http://localhost:5100
生产环境: http://<服务器公网IP>:5100
API 文档: http://<服务器公网IP>:5100/api/docs
```

---

## 六、风险与应对

| 风险 | 影响 | 应对措施 |
|------|------|----------|
| AKShare 数据不稳定 | 评分数据缺失 | 增加数据源降级策略 (东方财富备用) |
| 5400 只股票全量评分耗时 | 分析时间过长 | 并行计算 + 分批处理 + 增量更新 |
| 前端 ECharts K线性能 | 大数据量卡顿 | 数据降采样 + 懒加载 |
| LLM 调用费用 | Token 成本高 | 按需调用 + 缓存分析报告 |
| 服务器资源不足 | 响应慢 | 监控 CPU/内存，适时升级配置 |

---

## 七、启动建议

**建议从 Phase 0 + Phase 1 开始，先跑通核心评分引擎，再逐步完善 UI。**

我可以立即开始 Phase 0 的环境搭建，你觉得如何？

---

*文档版本: v1.0 | 创建日期: 2026-05-04*
*项目: 智能选股平台 | 目标端口: 5100*
