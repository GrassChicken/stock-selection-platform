#!/bin/bash
# 智能选股平台 - 重启脚本
# 同时管理后端(5100)和前端(3000)进程

set -e

# ==================== 配置 ====================
WORK_DIR="/root/.openclaw/workspace-fafaxia/projects/stock-selection-platform"
BACKEND_DIR="$WORK_DIR/backend"
FRONTEND_DIR="$WORK_DIR/frontend"
BACKEND_PID_FILE="$WORK_DIR/backend/.pid"
FRONTEND_PID_FILE="$WORK_DIR/frontend/.pid"
BACKEND_LOG="$WORK_DIR/backend/.service.log"
FRONTEND_LOG="$WORK_DIR/frontend/.service.log"

BACKEND_PORT=5100
FRONTEND_PORT=3000

# ==================== 颜色输出 ====================
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

info()  { echo -e "${BLUE}[INFO]${NC}  $1"; }
ok()    { echo -e "${GREEN}[OK]${NC}    $1"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }

# ==================== 参数解析 ====================
RESTART_BACKEND=true
RESTART_FRONTEND=false
STATUS_ONLY=false

for arg in "$@"; do
    case "$arg" in
        --backend-only)  RESTART_FRONTEND=false ;;
        --frontend)      RESTART_FRONTEND=true  ;;
        --status)        STATUS_ONLY=true       ;;
        --help|-h)
            echo "用法: $0 [选项]"
            echo ""
            echo "选项:"
            echo "  (默认)        重启后端 + 前端"
            echo "  --backend-only 只重启后端(推荐, 前端已构建并挂载)"
            echo "  --frontend     重启后端 + 前端开发服务器"
            echo "  --status       仅查看当前状态"
            echo "  --help, -h     显示帮助"
            exit 0
            ;;
        *) error "未知参数: $arg"; exit 1 ;;
    esac
done

# ==================== 查看状态 ====================
show_status() {
    echo ""
    echo "========================================"
    echo "🦐 智能选股平台 - 服务状态"
    echo "========================================"
    echo ""
    
    # 后端状态
    echo -n "  后端 (:$BACKEND_PORT)  "
    BE_PID=$(cat "$BACKEND_PID_FILE" 2>/dev/null || echo "")
    if [ -n "$BE_PID" ] && kill -0 "$BE_PID" 2>/dev/null; then
        echo -e "${GREEN}运行中${NC}  PID: $BE_PID"
    else
        BE_PORT_PID=$(ss -tlnp 2>/dev/null | grep ":$BACKEND_PORT " | grep -oP 'pid=\K\d+' || echo "")
        if [ -n "$BE_PORT_PID" ]; then
            echo -e "${YELLOW}端口占用${NC} PID: $BE_PORT_PID (无PID文件)"
        else
            echo -e "${RED}未运行${NC}"
        fi
    fi
    
    # 前端状态
    if [ "$RESTART_FRONTEND" = true ] || ss -tlnp 2>/dev/null | grep -q ":$FRONTEND_PORT "; then
        echo -n "  前端 (:$FRONTEND_PORT) "
        FE_PID=$(cat "$FRONTEND_PID_FILE" 2>/dev/null || echo "")
        if [ -n "$FE_PID" ] && kill -0 "$FE_PID" 2>/dev/null; then
            echo -e "${GREEN}运行中${NC}  PID: $FE_PID"
        else
            FE_PORT_PID=$(ss -tlnp 2>/dev/null | grep ":$FRONTEND_PORT " | grep -oP 'pid=\K\d+' || echo "")
            if [ -n "$FE_PORT_PID" ]; then
                echo -e "${YELLOW}端口占用${NC} PID: $FE_PORT_PID (无PID文件)"
            else
                echo -e "${RED}未运行${NC}"
            fi
        fi
    fi
    
    # HTTP 检查
    echo ""
    echo "  HTTP 检查:"
    BACKEND_HTTP=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$BACKEND_PORT/api/health 2>/dev/null || echo "000")
    if [ "$BACKEND_HTTP" = "200" ]; then
        echo -e "    后端 API: ${GREEN}正常 ($BACKEND_HTTP)${NC}"
    else
        echo -e "    后端 API: ${RED}异常 ($BACKEND_HTTP)${NC}"
    fi
    
    FRONTEND_HTTP=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$BACKEND_PORT/ 2>/dev/null || echo "000")
    if [ "$FRONTEND_HTTP" = "200" ]; then
        echo -e "    前端页面: ${GREEN}正常 ($FRONTEND_HTTP)${NC}"
    else
        echo -e "    前端页面: ${RED}异常 ($FRONTEND_HTTP)${NC}"
    fi
    
    echo ""
    echo "========================================"
    exit 0
}

if [ "$STATUS_ONLY" = true ]; then
    show_status
fi

# ==================== 停止进程函数 ====================
stop_process() {
    local name=$1
    local port=$2
    local pid_file=$3
    
    info "停止 $name (端口 $port)..."
    
    # 方法 1: PID 文件
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file" 2>/dev/null)
        if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
            info "  PID 文件: $pid → 发送 SIGTERM..."
            kill "$pid" 2>/dev/null || true
            sleep 1
            # 如果还在，强制杀掉
            if kill -0 "$pid" 2>/dev/null; then
                warn "  进程未响应 SIGTERM，强制 SIGKILL..."
                kill -9 "$pid" 2>/dev/null || true
                sleep 1
            fi
        fi
        rm -f "$pid_file"
    fi
    
    # 方法 2: 通过端口查杀
    local port_pid=$(ss -tlnp 2>/dev/null | grep ":$port " | grep -oP 'pid=\K\d+' | head -1 || echo "")
    if [ -n "$port_pid" ]; then
        warn "  端口 $port 仍被 PID $port_pid 占用，强制清理..."
        kill -9 "$port_pid" 2>/dev/null || true
        sleep 1
    fi
    
    # 方法 3: 通过进程名查杀
    local process_pid=$(ps aux 2>/dev/null | grep -E "(uvicorn.*$port|vite.*$port)" | grep -v grep | awk '{print $2}' | head -1 || echo "")
    if [ -n "$process_pid" ]; then
        warn "  发现残留进程 PID $process_pid，清理中..."
        kill -9 "$process_pid" 2>/dev/null || true
        sleep 1
    fi
    
    # 验证端口已释放
    sleep 1
    local check=$(ss -tlnp 2>/dev/null | grep ":$port " || echo "")
    if [ -n "$check" ]; then
        warn "  端口 $port 仍未释放，等待 3 秒..."
        sleep 3
        check=$(ss -tlnp 2>/dev/null | grep ":$port " || echo "")
        if [ -n "$check" ]; then
            local final_pid=$(echo "$check" | grep -oP 'pid=\K\d+' | head -1 || echo "")
            error "  无法释放端口 $port (PID: $final_pid)，手动清理后重试"
            return 1
        fi
    fi
    
    ok "$name 已停止，端口 $port 已释放"
    return 0
}

# ==================== 启动后端 ====================
start_backend() {
    info "启动后端服务 (端口 $BACKEND_PORT)..."
    cd "$BACKEND_DIR"
    
    nohup ./venv/bin/uvicorn app.main:app \
        --host 0.0.0.0 \
        --port $BACKEND_PORT \
        --workers 1 \
        > "$BACKEND_LOG" 2>&1 &
    local pid=$!
    echo "$pid" > "$BACKEND_PID_FILE"
    info "  后端 PID: $pid"
    
    # 轮询等待启动
    for i in $(seq 1 15); do
        sleep 1
        # 检查进程
        if ! kill -0 "$pid" 2>/dev/null; then
            error "  后端进程已退出"
            error "  日志:"
            tail -20 "$BACKEND_LOG"
            return 1
        fi
        # 检查端口
        if ss -tlnp 2>/dev/null | grep -q ":$BACKEND_PORT "; then
            ok "  后端已启动 (第 ${i}s)"
            return 0
        fi
        echo "    等待中... ($i/15)"
    done
    
    error "  后端启动超时"
    tail -20 "$BACKEND_LOG"
    return 1
}

# ==================== 启动前端 ====================
start_frontend() {
    info "启动前端开发服务器 (端口 $FRONTEND_PORT)..."
    cd "$FRONTEND_DIR"
    
    nohup npm run dev -- --port $FRONTEND_PORT --host 0.0.0.0 \
        > "$FRONTEND_LOG" 2>&1 &
    local pid=$!
    echo "$pid" > "$FRONTEND_PID_FILE"
    info "  前端 PID: $pid"
    
    # 轮询等待启动
    for i in $(seq 1 15); do
        sleep 1
        if ! kill -0 "$pid" 2>/dev/null; then
            error "  前端进程已退出"
            tail -20 "$FRONTEND_LOG"
            return 1
        fi
        if ss -tlnp 2>/dev/null | grep -q ":$FRONTEND_PORT "; then
            ok "  前端已启动 (第 ${i}s)"
            return 0
        fi
        echo "    等待中... ($i/15)"
    done
    
    error "  前端启动超时"
    tail -20 "$FRONTEND_LOG"
    return 1
}

# ==================== 主流程 ====================
echo ""
echo "========================================"
echo "🦐 智能选股平台 - 重启服务"
echo "========================================"
echo ""

# 停止后端
stop_process "后端" $BACKEND_PORT "$BACKEND_PID_FILE"

# 停止前端（如果需要）
if [ "$RESTART_FRONTEND" = true ]; then
    stop_process "前端" $FRONTEND_PORT "$FRONTEND_PID_FILE"
fi

echo ""

# 启动后端
if ! start_backend; then
    error "后端启动失败，退出"
    exit 1
fi

# 启动前端（如果需要）
if [ "$RESTART_FRONTEND" = true ]; then
    echo ""
    if ! start_frontend; then
        warn "前端启动失败（后端已正常运行）"
    fi
fi

# ==================== 最终验证 ====================
echo ""
echo "========================================"
echo "✅ 重启完成"
echo "========================================"
echo ""

sleep 1

BACKEND_HTTP=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$BACKEND_PORT/api/health 2>/dev/null || echo "000")
FRONTEND_HTTP=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$BACKEND_PORT/ 2>/dev/null || echo "000")

if [ "$BACKEND_HTTP" = "200" ]; then
    echo "  后端 API:    ✅ 正常"
else
    echo "  后端 API:    ❌ 异常 (HTTP $BACKEND_HTTP)"
fi

if [ "$FRONTEND_HTTP" = "200" ]; then
    echo "  前端页面:    ✅ 正常"
else
    echo "  前端页面:    ❌ 异常 (HTTP $FRONTEND_HTTP)"
fi

if [ "$RESTART_FRONTEND" = true ]; then
    FE_HTTP=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$FRONTEND_PORT/ 2>/dev/null || echo "000")
    if [ "$FE_HTTP" = "200" ]; then
        echo "  前端开发服:  ✅ 正常 (:$FRONTEND_PORT)"
    else
        echo "  前端开发服:  ⚠️ 异常 (HTTP $FE_HTTP)"
    fi
fi

echo ""
echo "  访问地址:"
echo "    前端页面:  http://120.55.195.194:$BACKEND_PORT/"
echo "    API 文档:  http://120.55.195.194:$BACKEND_PORT/api/docs"
echo "    健康检查:  http://120.55.195.194:$BACKEND_PORT/api/health"
echo ""
echo "  日志文件:"
echo "    后端:  $BACKEND_LOG"
if [ "$RESTART_FRONTEND" = true ]; then
    echo "    前端:  $FRONTEND_LOG"
fi
echo ""
echo "========================================"
