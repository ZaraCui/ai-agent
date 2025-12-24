# Redis Cache Management Scripts
# 用于快速管理Redis缓存的辅助脚本

Write-Host "Travel Planning Agent - Redis Cache Management" -ForegroundColor Cyan
Write-Host "============================================================"

function Show-Menu {
    Write-Host "`n选择操作：" -ForegroundColor Yellow
    Write-Host "1. 启动 Redis (Docker)"
    Write-Host "2. 停止 Redis"
    Write-Host "3. 查看 Redis 状态"
    Write-Host "4. 测试 Redis 连接"
    Write-Host "5. 查看缓存统计"
    Write-Host "6. 清除所有缓存"
    Write-Host "7. 安装 Python 依赖"
    Write-Host "8. 运行缓存测试"
    Write-Host "9. 启动应用"
    Write-Host "0. 退出"
    Write-Host ""
}

function Start-Redis {
    Write-Host "`n启动 Redis..." -ForegroundColor Green
    docker run -d --name redis-cache -p 6379:6379 redis:7-alpine
    if ($LASTEXITCODE -eq 0) {
        Write-Host "OK Redis 启动成功" -ForegroundColor Green
    } else {
        Write-Host "X Redis 启动失败" -ForegroundColor Red
        Write-Host "可能 Redis 容器已存在，尝试启动现有容器..." -ForegroundColor Yellow
        docker start redis-cache
    }
}

function Stop-Redis {
    Write-Host "`n停止 Redis..." -ForegroundColor Yellow
    docker stop redis-cache
    if ($LASTEXITCODE -eq 0) {
        Write-Host "OK Redis 已停止" -ForegroundColor Green
    }
}

function Check-RedisStatus {
    Write-Host "`n检查 Redis 状态..." -ForegroundColor Cyan
    docker ps -a --filter "name=redis-cache" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
}

function Test-RedisConnection {
    Write-Host "`n测试 Redis 连接..." -ForegroundColor Cyan
    docker exec redis-cache redis-cli ping
    if ($LASTEXITCODE -eq 0) {
        Write-Host "OK Redis 连接正常" -ForegroundColor Green
    } else {
        Write-Host "X Redis 连接失败" -ForegroundColor Red
    }
}

function Get-CacheStats {
    Write-Host "`n获取缓存统计..." -ForegroundColor Cyan
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:5000/api/cache/stats" -Method Get
        $response.data | ConvertTo-Json -Depth 10
    } catch {
        Write-Host "X 无法连接到应用 API（确保应用正在运行）" -ForegroundColor Red
    }
}

function Clear-AllCache {
    Write-Host "`n清除所有缓存..." -ForegroundColor Yellow
    Write-Host "确定要清除所有缓存吗? (y/n): " -NoNewline
    $confirm = Read-Host
    if (($confirm -eq 'y') -or ($confirm -eq 'Y')) {
        try {
            $response = Invoke-RestMethod -Uri "http://localhost:5000/api/cache/invalidate/all" -Method Post
            Write-Host "OK 缓存已清除" -ForegroundColor Green
            $response.data | ConvertTo-Json
        } catch {
            Write-Host "X 清除缓存失败" -ForegroundColor Red
        }
    } else {
        Write-Host "已取消" -ForegroundColor Yellow
    }
}

function Install-Dependencies {
    Write-Host "`n安装 Python 依赖..." -ForegroundColor Cyan
    pip install redis hiredis
    if ($LASTEXITCODE -eq 0) {
        Write-Host "OK 依赖安装成功" -ForegroundColor Green
    }
}

function Run-CacheTest {
    Write-Host "`n运行缓存测试..." -ForegroundColor Cyan
    python test_redis_cache.py
}

function Start-Application {
    Write-Host "`n启动应用..." -ForegroundColor Cyan
    Write-Host "按 Ctrl+C 停止应用" -ForegroundColor Yellow
    python app.py
}

# 主循环
while ($true) {
    Show-Menu
    $choice = Read-Host "请输入选项"
    
    switch ($choice) {
        "1" { Start-Redis }
        "2" { Stop-Redis }
        "3" { Check-RedisStatus }
        "4" { Test-RedisConnection }
        "5" { Get-CacheStats }
        "6" { Clear-AllCache }
        "7" { Install-Dependencies }
        "8" { Run-CacheTest }
        "9" { Start-Application }
        "0" { 
            Write-Host "`n再见" -ForegroundColor Cyan
            exit 
        }
        default { 
            Write-Host "`n无效选项，请重试" -ForegroundColor Red 
        }
    }
    
    Write-Host "`n按任意键继续..." -ForegroundColor Gray
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}
