# Redis缓存使用指南

## 概述

本项目已集成Redis缓存机制，用于提升API响应速度和减少数据库/文件系统访问。缓存系统是可选的，如果不配置Redis，应用将正常运行但不使用缓存。

## 功能特性

- ✅ **自动缓存管理**：关键API端点自动使用缓存
- ✅ **灵活配置**：通过环境变量控制缓存行为
- ✅ **故障容错**：Redis连接失败时自动降级，不影响应用运行
- ✅ **缓存统计**：提供API端点查看缓存使用情况
- ✅ **缓存管理**：支持按模式清除缓存或完全清空

## 快速开始

### 1. 安装Redis

#### Windows
```bash
# 使用Chocolatey安装
choco install redis-64

# 或从GitHub下载预编译版本
# https://github.com/microsoftarchive/redis/releases
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis
sudo systemctl enable redis
```

#### macOS
```bash
brew install redis
brew services start redis
```

#### Docker（推荐用于开发）
```bash
docker run -d --name redis-cache -p 6379:6379 redis:7-alpine
```

### 2. 安装Python依赖

```bash
pip install redis hiredis
# 或者
pip install -r requirements.txt
```

### 3. 配置环境变量

在项目根目录创建或编辑 `.env` 文件：

```env
# 启用Redis缓存
REDIS_ENABLED=True

# Redis服务器配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0

# 连接超时设置（秒）
REDIS_SOCKET_TIMEOUT=5
```

### 4. 启动应用

```bash
python app.py
```

查看日志确认Redis连接成功：
```
Redis cache connected successfully to localhost:6379
```

如果Redis未启用或连接失败：
```
Redis cache is disabled. Set REDIS_ENABLED=True to enable.
```

## 缓存策略

### 已缓存的API端点

| 端点 | 缓存键格式 | TTL（过期时间） | 说明 |
|------|-----------|----------------|------|
| `/api/cities` | `cities:list` | 24小时 | 城市列表不常变化 |
| `/api/spots/<city>` | `spots:{city}` | 12小时 | 城市景点数据 |
| `/plan_itinerary` | `plan:{city}:d{days}:s{hash}:m{mode}` | 1小时 | 行程规划结果（可选） |

### 缓存自动失效

缓存会在以下情况自动失效：
- TTL过期
- 手动清除缓存
- 数据文件更新后需手动清除对应缓存

## 缓存管理API

### 1. 查看缓存统计

```bash
GET /api/cache/stats
```

**响应示例：**
```json
{
  "status": "success",
  "data": {
    "enabled": true,
    "connected": true,
    "keys_count": 42,
    "used_memory": "1.23M",
    "connected_clients": 3,
    "keyspace_hits": 1250,
    "keyspace_misses": 89,
    "uptime_in_seconds": 86400
  }
}
```

### 2. 清除特定类型缓存

```bash
POST /api/cache/invalidate/<cache_type>
```

**cache_type可选值：**
- `cities` - 清除所有城市列表缓存
- `spots` - 清除所有景点数据缓存
- `plans` - 清除所有行程规划缓存
- `all` - 清除所有缓存

**示例：**
```bash
curl -X POST http://localhost:5000/api/cache/invalidate/spots
```

### 3. 按模式清除缓存

```bash
POST /api/cache/clear
Content-Type: application/json

{
  "pattern": "spots:shanghai*"
}
```

### 4. 清除所有缓存（谨慎使用）

```bash
POST /api/cache/clear
Content-Type: application/json

{
  "clear_all": true
}
```

## 使用场景

### 开发环境

开发时可能不需要缓存以便看到最新数据：

```env
REDIS_ENABLED=False
```

或在开发时频繁清除缓存：

```bash
curl -X POST http://localhost:5000/api/cache/invalidate/all
```

### 生产环境

生产环境推荐配置：

```env
REDIS_ENABLED=True
REDIS_HOST=your-redis-server.com
REDIS_PORT=6379
REDIS_PASSWORD=your-secure-password
REDIS_DB=0
REDIS_SOCKET_TIMEOUT=5
```

### 云部署（Vercel + Redis Cloud）

#### 使用Redis Cloud（推荐）

1. 注册 [Redis Cloud](https://redis.com/try-free/)
2. 创建免费数据库（30MB足够）
3. 获取连接信息
4. 在Vercel中设置环境变量：

```
REDIS_ENABLED=True
REDIS_HOST=redis-12345.c123.us-east-1-1.ec2.cloud.redislabs.com
REDIS_PORT=12345
REDIS_PASSWORD=your-password
REDIS_DB=0
```

#### 使用Upstash（Serverless Redis）

1. 注册 [Upstash](https://upstash.com/)
2. 创建Redis数据库
3. 使用REST API或Redis协议
4. 配置环境变量

## 性能优化建议

### 1. 调整TTL

根据数据更新频率调整缓存过期时间：

```python
# 在 agent/cache.py 中修改
cache.set(cache_key, result, ttl=7200)  # 2小时
```

### 2. 监控缓存命中率

定期检查缓存统计：

```bash
# 计算命中率
hit_rate = keyspace_hits / (keyspace_hits + keyspace_misses)
```

理想命中率应大于80%。

### 3. 缓存预热

应用启动时预加载常用数据：

```python
# 预加载所有城市数据
cities = get_all_cities()
for city in cities:
    cache.set(cache_key_for_spots(city), load_spots(city), ttl=43200)
```

### 4. 批量清除

数据更新后批量清除相关缓存：

```bash
# 更新了上海的景点数据后
curl -X POST http://localhost:5000/api/cache/clear \
  -H "Content-Type: application/json" \
  -d '{"pattern": "spots:shanghai"}'
```

## 故障排除

### Redis连接失败

**症状：**
```
Failed to connect to Redis: Error 111 connecting to localhost:6379. Connection refused.
```

**解决方案：**
1. 确认Redis服务已启动：
   ```bash
   # Windows
   redis-server
   
   # Linux/macOS
   sudo systemctl status redis
   redis-cli ping  # 应返回 PONG
   ```

2. 检查防火墙设置
3. 验证连接配置

### 缓存数据不更新

**症状：** 修改了数据文件但API返回旧数据

**解决方案：**
```bash
# 清除特定城市缓存
curl -X POST http://localhost:5000/api/cache/invalidate/spots

# 或清除所有缓存
curl -X POST http://localhost:5000/api/cache/invalidate/all
```

### 内存使用过高

**症状：** Redis内存占用持续增长

**解决方案：**

1. 设置Redis最大内存限制：
   ```bash
   # redis.conf
   maxmemory 256mb
   maxmemory-policy allkeys-lru
   ```

2. 减少TTL或更频繁地清理缓存

3. 监控缓存使用：
   ```bash
   redis-cli info memory
   ```

## 代码示例

### 在自定义函数中使用缓存

```python
from agent.cache import cached

@cached(prefix='my_expensive_function', ttl=3600)
def my_expensive_function(param1, param2):
    # 耗时操作
    result = expensive_computation(param1, param2)
    return result

# 第一次调用会执行函数
result1 = my_expensive_function('a', 'b')

# 相同参数的第二次调用会从缓存读取
result2 = my_expensive_function('a', 'b')  # 从缓存读取，速度快
```

### 手动缓存管理

```python
from agent.cache import cache

# 手动设置缓存
cache.set('my_key', {'data': 'value'}, ttl=600)

# 读取缓存
data = cache.get('my_key')

# 删除缓存
cache.delete('my_key')

# 批量删除
cache.clear_pattern('prefix:*')
```

## 安全注意事项

1. **生产环境必须设置密码：**
   ```env
   REDIS_PASSWORD=strong-random-password-here
   ```

2. **限制Redis访问：**
   - 使用防火墙限制Redis端口（6379）访问
   - 配置Redis仅监听内网地址
   - 使用VPN或SSH隧道

3. **敏感数据处理：**
   - 不要在缓存中存储敏感用户信息
   - 使用加密传输（TLS/SSL）

## 监控和日志

应用会记录缓存相关日志：

```python
# 日志级别设置
import logging
logging.basicConfig(level=logging.DEBUG)

# 查看缓存操作日志
[DEBUG] Cache hit: spots:shanghai
[DEBUG] Cache miss: plan:beijing:d3:s12ab34cd:mtransit
[DEBUG] Cache set: spots:tokyo (TTL: 43200s)
```

## 进一步优化

### 1. 使用Redis Cluster（大规模部署）

```env
REDIS_CLUSTER_ENABLED=True
REDIS_CLUSTER_NODES=node1:7000,node2:7001,node3:7002
```

### 2. 实现缓存预热脚本

创建 `scripts/cache_warmup.py`：

```python
from agent.cache import cache, cache_key_for_spots
import json
import os

def warmup_cache():
    for filename in os.listdir('data'):
        if filename.startswith('spots_'):
            city = filename[6:-5]
            with open(f'data/{filename}') as f:
                spots = json.load(f)
            cache_key = cache_key_for_spots(city)
            cache.set(cache_key, {
                'city': city,
                'spots': spots,
                'total': len(spots)
            }, ttl=43200)
            print(f'Warmed up cache for {city}')

if __name__ == '__main__':
    warmup_cache()
```

### 3. 监控仪表板

考虑使用以下工具监控Redis：
- RedisInsight（官方GUI）
- Redis Commander（Web界面）
- Prometheus + Grafana（生产监控）

## 总结

Redis缓存机制可以显著提升应用性能，特别是在高并发场景下。合理配置和监控缓存系统，可以：

- ⚡ 减少API响应时间80%以上
- 📉 降低服务器负载
- 💰 节省数据库访问成本
- 🚀 改善用户体验

如有问题，请参考本文档或查看应用日志进行排查。
