#!/bin/bash
# Redis Cache Management Scripts
# 用于快速管理Redis缓存的辅助脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}Travel Planning Agent - Redis Cache Management${NC}"
echo "============================================================"

show_menu() {
    echo -e "\n${YELLOW}选择操作：${NC}"
    echo "1. 启动 Redis (Docker)"
    echo "2. 停止 Redis"
    echo "3. 查看 Redis 状态"
    echo "4. 测试 Redis 连接"
    echo "5. 查看缓存统计"
    echo "6. 清除所有缓存"
    echo "7. 安装 Python 依赖"
    echo "8. 运行缓存测试"
    echo "9. 启动应用"
    echo "0. 退出"
    echo ""
}

start_redis() {
    echo -e "\n${GREEN}启动 Redis...${NC}"
    if docker run -d --name redis-cache -p 6379:6379 redis:7-alpine; then
        echo -e "${GREEN}✓ Redis 启动成功！${NC}"
    else
        echo -e "${RED}✗ Redis 启动失败${NC}"
        echo -e "${YELLOW}可能 Redis 容器已存在，尝试启动现有容器...${NC}"
        docker start redis-cache
    fi
}

stop_redis() {
    echo -e "\n${YELLOW}停止 Redis...${NC}"
    if docker stop redis-cache; then
        echo -e "${GREEN}✓ Redis 已停止${NC}"
    fi
}

check_redis_status() {
    echo -e "\n${CYAN}检查 Redis 状态...${NC}"
    docker ps -a --filter "name=redis-cache" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
}

test_redis_connection() {
    echo -e "\n${CYAN}测试 Redis 连接...${NC}"
    if docker exec redis-cache redis-cli ping; then
        echo -e "${GREEN}✓ Redis 连接正常！${NC}"
    else
        echo -e "${RED}✗ Redis 连接失败${NC}"
    fi
}

get_cache_stats() {
    echo -e "\n${CYAN}获取缓存统计...${NC}"
    if curl -s http://localhost:5000/api/cache/stats | python -m json.tool; then
        echo -e "${GREEN}✓ 获取成功${NC}"
    else
        echo -e "${RED}✗ 无法连接到应用 API（确保应用正在运行）${NC}"
    fi
}

clear_all_cache() {
    echo -e "\n${YELLOW}清除所有缓存...${NC}"
    read -p "确定要清除所有缓存吗？(y/n): " confirm
    if [[ $confirm == "y" || $confirm == "Y" ]]; then
        if curl -s -X POST http://localhost:5000/api/cache/invalidate/all | python -m json.tool; then
            echo -e "${GREEN}✓ 缓存已清除${NC}"
        else
            echo -e "${RED}✗ 清除缓存失败${NC}"
        fi
    else
        echo -e "${YELLOW}已取消${NC}"
    fi
}

install_dependencies() {
    echo -e "\n${CYAN}安装 Python 依赖...${NC}"
    if pip install redis hiredis; then
        echo -e "${GREEN}✓ 依赖安装成功！${NC}"
    fi
}

run_cache_test() {
    echo -e "\n${CYAN}运行缓存测试...${NC}"
    python test_redis_cache.py
}

start_application() {
    echo -e "\n${CYAN}启动应用...${NC}"
    echo -e "${YELLOW}按 Ctrl+C 停止应用${NC}"
    python app.py
}

# 主循环
while true; do
    show_menu
    read -p "请输入选项: " choice
    
    case $choice in
        1) start_redis ;;
        2) stop_redis ;;
        3) check_redis_status ;;
        4) test_redis_connection ;;
        5) get_cache_stats ;;
        6) clear_all_cache ;;
        7) install_dependencies ;;
        8) run_cache_test ;;
        9) start_application ;;
        0) 
            echo -e "\n${CYAN}再见！${NC}"
            exit 0
            ;;
        *) 
            echo -e "\n${RED}无效选项，请重试${NC}"
            ;;
    esac
    
    echo -e "\n${NC}按回车继续..."
    read
done
