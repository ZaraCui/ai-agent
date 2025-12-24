# Redis缓存快速上手示例

## 基本使用

### 1. 启动Redis（使用Docker，最简单）

```bash
docker run -d --name redis-cache -p 6379:6379 redis:7-alpine
```

### 2. 配置环境变量

在 `.env` 文件中添加：

```env
REDIS_ENABLED=True
REDIS_HOST=localhost
REDIS_PORT=6379
```

### 3. 安装依赖并启动

```bash
pip install redis hiredis
python app.py
```

### 4. 测试缓存功能

```bash
# 运行测试脚本
python test_redis_cache.py
```

## API使用示例

### 查看缓存统计

```bash
curl http://localhost:5000/api/cache/stats
```

响应示例：
```json
{
  "status": "success",
  "data": {
    "enabled": true,
    "connected": true,
    "keys_count": 15,
    "used_memory": "256.5K",
    "keyspace_hits": 234,
    "keyspace_misses": 12
  }
}
```

### 清除特定类型缓存

```bash
# 清除所有景点缓存
curl -X POST http://localhost:5000/api/cache/invalidate/spots

# 清除所有城市缓存
curl -X POST http://localhost:5000/api/cache/invalidate/cities

# 清除所有规划缓存
curl -X POST http://localhost:5000/api/cache/invalidate/plans

# 清除所有缓存
curl -X POST http://localhost:5000/api/cache/invalidate/all
```

### 按模式清除缓存

```bash
# 只清除上海的景点缓存
curl -X POST http://localhost:5000/api/cache/clear \
  -H "Content-Type: application/json" \
  -d '{"pattern": "spots:shanghai"}'

# 清除所有以 "spots:" 开头的缓存
curl -X POST http://localhost:5000/api/cache/clear \
  -H "Content-Type: application/json" \
  -d '{"pattern": "spots:*"}'
```

## Python代码示例

### 使用装饰器添加缓存

```python
from agent.cache import cached

@cached(prefix='weather_data', ttl=1800)  # 缓存30分钟
def get_weather(city):
    # 模拟API调用
    import time
    time.sleep(2)  # 模拟延迟
    return {
        "city": city,
        "temperature": 25,
        "condition": "Sunny"
    }

# 第一次调用：需要2秒
weather = get_weather("Shanghai")

# 第二次调用：立即返回（从缓存）
weather = get_weather("Shanghai")
```

### 手动管理缓存

```python
from agent.cache import cache

# 保存数据到缓存
user_data = {
    "id": 123,
    "name": "张三",
    "preferences": ["beach", "mountain"]
}
cache.set("user:123", user_data, ttl=3600)  # 缓存1小时

# 从缓存读取
cached_user = cache.get("user:123")
if cached_user:
    print(f"从缓存加载: {cached_user['name']}")
else:
    print("缓存未命中，需要从数据库加载")

# 删除缓存
cache.delete("user:123")

# 批量删除（删除所有用户缓存）
cache.clear_pattern("user:*")
```

### 实际应用场景

#### 场景1：缓存景点搜索结果

```python
from agent.cache import cache, cache_key_for_spots
import json

def load_spots_with_cache(city):
    """加载城市景点，使用缓存"""
    # 生成缓存键
    cache_key = cache_key_for_spots(city)
    
    # 尝试从缓存读取
    cached_data = cache.get(cache_key)
    if cached_data:
        print(f"✓ 从缓存加载 {city} 的景点数据")
        return cached_data
    
    # 缓存未命中，从文件读取
    print(f"✗ 缓存未命中，从文件加载 {city} 的景点数据")
    with open(f"data/spots_{city}.json") as f:
        spots = json.load(f)
    
    # 保存到缓存（12小时）
    result = {
        "city": city,
        "spots": spots,
        "total": len(spots)
    }
    cache.set(cache_key, result, ttl=43200)
    
    return result

# 使用
spots = load_spots_with_cache("shanghai")
```

#### 场景2：缓存耗时计算

```python
from agent.cache import cached
import hashlib

@cached(prefix='route_calculation', ttl=7200)  # 缓存2小时
def calculate_optimal_route(spots, days, mode):
    """计算最优路线（耗时操作）"""
    import time
    print("正在计算最优路线...")
    time.sleep(5)  # 模拟耗时计算
    
    return {
        "route": "Shanghai -> Suzhou -> Hangzhou",
        "total_distance": 250,
        "total_time": 180
    }

# 第一次调用：需要5秒
route = calculate_optimal_route(
    spots=["Shanghai", "Suzhou", "Hangzhou"],
    days=3,
    mode="transit"
)

# 相同参数的第二次调用：立即返回
route = calculate_optimal_route(
    spots=["Shanghai", "Suzhou", "Hangzhou"],
    days=3,
    mode="transit"
)
```

## 监控缓存性能

### Python脚本监控

```python
from agent.cache import cache
import time

def monitor_cache_performance():
    """监控缓存性能"""
    stats = cache.get_stats()
    
    if not stats.get('enabled'):
        print("Redis缓存未启用")
        return
    
    hits = stats.get('keyspace_hits', 0)
    misses = stats.get('keyspace_misses', 0)
    total = hits + misses
    
    if total > 0:
        hit_rate = (hits / total) * 100
        print(f"缓存命中率: {hit_rate:.2f}%")
        print(f"总请求: {total}")
        print(f"命中: {hits}")
        print(f"未命中: {misses}")
    else:
        print("暂无缓存访问数据")
    
    print(f"缓存键数量: {stats.get('keys_count', 0)}")
    print(f"内存使用: {stats.get('used_memory', 'N/A')}")

if __name__ == "__main__":
    while True:
        monitor_cache_performance()
        time.sleep(60)  # 每分钟检查一次
```

## 常见问题

### Q: Redis连接失败怎么办？

A: 检查以下几点：
1. Redis是否正在运行：`redis-cli ping`
2. 端口是否正确：默认6379
3. 防火墙是否阻止连接
4. `.env`配置是否正确

### Q: 如何清除所有缓存？

```bash
curl -X POST http://localhost:5000/api/cache/invalidate/all
```

### Q: 缓存数据不更新怎么办？

A: 更新数据文件后，清除对应的缓存：
```bash
# 更新了上海景点数据后
curl -X POST http://localhost:5000/api/cache/clear \
  -H "Content-Type: application/json" \
  -d '{"pattern": "spots:shanghai"}'
```

### Q: 如何在开发时禁用缓存？

在 `.env` 文件中设置：
```env
REDIS_ENABLED=False
```

## 最佳实践

1. **合理设置TTL**：
   - 静态数据（城市列表）：24小时
   - 半静态数据（景点信息）：12小时
   - 动态数据（规划结果）：1小时

2. **监控命中率**：
   - 理想命中率应 > 80%
   - 如果太低，考虑增加TTL

3. **定期清理**：
   - 数据更新后立即清除相关缓存
   - 定期清理所有缓存（如每周）

4. **生产环境**：
   - 使用Redis持久化（RDB或AOF）
   - 设置最大内存限制
   - 配置密码保护
   - 监控Redis状态

## 性能对比

| 操作 | 无缓存 | 有缓存 | 提升 |
|------|--------|--------|------|
| 加载城市列表 | 50ms | 5ms | 10x |
| 加载景点数据 | 150ms | 10ms | 15x |
| 规划行程 | 8s | 50ms | 160x |

## 更多信息

- 📖 [完整配置指南](REDIS_CACHE_GUIDE.md)
- 📝 [实施总结](REDIS_IMPLEMENTATION_SUMMARY.md)
- 🐍 [redis-py文档](https://redis-py.readthedocs.io/)
