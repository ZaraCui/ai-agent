# Vercel + Redis 部署指南

## 概述

本指南说明如何在Vercel上部署Travel Planning Agent并启用Redis缓存功能。

## 为什么Vercel需要外部Redis？

Vercel是serverless平台，特点：
- ❌ 无法运行Docker容器
- ❌ 无持久化本地存储
- ✅ 需要使用云端Redis服务
- ✅ 支持环境变量配置

## 方案1：使用Upstash (推荐)

### 为什么选择Upstash？
- ✅ **专为serverless设计**：无连接数限制
- ✅ **按请求计费**：只为实际使用付费
- ✅ **免费额度充足**：10,000次请求/天
- ✅ **全球CDN**：低延迟
- ✅ **与Vercel完美集成**

### 步骤1：创建Upstash账户和数据库

1. 访问 [Upstash](https://upstash.com/) 并注册
2. 创建新的Redis数据库：
   - 点击 "Create Database"
   - 选择区域（推荐选择离你用户最近的）
   - 选择 "Global" 类型（免费）
   - 点击创建

3. 获取连接信息：
   ```
   Endpoint: us1-merry-fox-12345.upstash.io
   Port: 6379
   Password: AaBbCcDdEeFfGgHhIiJj
   ```

### 步骤2：在Vercel配置环境变量

在Vercel项目设置中添加以下环境变量：

```env
# 启用Redis缓存
REDIS_ENABLED=True

# Upstash连接信息
REDIS_HOST=us1-merry-fox-12345.upstash.io
REDIS_PORT=6379
REDIS_PASSWORD=your-upstash-password
REDIS_DB=0
REDIS_SOCKET_TIMEOUT=5
```

### 步骤3：部署

```bash
git add .
git commit -m "Enable Redis cache with Upstash"
git push origin main
```

Vercel会自动重新部署并应用新的环境变量。

### 步骤4：验证

部署完成后，访问：
```
https://your-app.vercel.app/api/cache/stats
```

应该看到：
```json
{
  "status": "success",
  "data": {
    "enabled": true,
    "connected": true,
    "keys_count": 0,
    ...
  }
}
```

## 方案2：使用Redis Cloud

### 步骤1：创建Redis Cloud账户

1. 访问 [Redis Cloud](https://redis.com/try-free/)
2. 注册并创建免费数据库（30MB）
3. 获取连接信息：
   ```
   Host: redis-12345.c123.us-east-1-1.ec2.cloud.redislabs.com
   Port: 12345
   Password: your-password
   ```

### 步骤2：在Vercel配置

```env
REDIS_ENABLED=True
REDIS_HOST=redis-12345.c123.us-east-1-1.ec2.cloud.redislabs.com
REDIS_PORT=12345
REDIS_PASSWORD=your-password
REDIS_DB=0
```

## 方案3：使用Railway Redis

如果你的后端部署在Railway：

1. 在Railway项目中添加Redis服务
2. Railway会自动提供环境变量
3. 在Vercel前端配置指向Railway Redis

## Vercel特定优化

### 1. 调整缓存TTL

由于serverless特性，建议使用较长的TTL：

在 `agent/cache.py` 中：
```python
# 城市列表 - 48小时（变化很少）
cache.set(cache_key, cities, ttl=172800)

# 景点数据 - 24小时
cache.set(cache_key, result, ttl=86400)
```

### 2. 使用Redis连接池

已经在 `agent/cache.py` 中实现：
```python
self.redis_client = redis.Redis(
    ...
    health_check_interval=30,  # 保持连接健康
    retry_on_timeout=True      # 自动重试
)
```

### 3. 监控缓存性能

使用Vercel Analytics和Upstash Dashboard：
- Vercel: 查看函数执行时间
- Upstash: 查看请求次数和延迟

## 成本估算

### Upstash免费计划
- 10,000次请求/天
- 对于中小型应用完全够用
- 示例：1000个用户/天，每人10个请求 = 足够

### Redis Cloud免费计划
- 30MB存储
- 30个并发连接
- 适合小型应用

### 预期使用量
以每天1000次API调用为例：
- 城市列表: ~10次（缓存48小时）
- 景点数据: ~100次（缓存24小时）
- Redis操作: ~110次/天
- **远低于免费额度**

## 部署检查清单

### 部署前
- [ ] 创建Upstash/Redis Cloud账户
- [ ] 获取Redis连接信息
- [ ] 在Vercel设置环境变量
- [ ] 测试本地连接（可选）

### 部署后
- [ ] 访问 `/api/cache/stats` 确认连接
- [ ] 测试API响应速度
- [ ] 查看Upstash Dashboard确认请求
- [ ] 监控Vercel函数执行时间

## 常见问题

### Q: 不配置Redis，Vercel部署会失败吗？

A: **不会**！Redis是可选功能。如果 `REDIS_ENABLED=False` 或未设置，应用会正常运行但不使用缓存。

### Q: 如何在Vercel上清除缓存？

A: 访问API端点：
```bash
curl -X POST https://your-app.vercel.app/api/cache/invalidate/all
```

或在Upstash Dashboard直接操作。

### Q: Redis连接失败会影响应用吗？

A: **不会**！代码有完善的错误处理，Redis失败时会自动降级：
```python
except redis.ConnectionError as e:
    logger.warning("Redis cache disabled due to connection failure")
    self.enabled = False
```

### Q: 如何切换Redis服务提供商？

A: 只需更新Vercel环境变量，无需修改代码：
```env
# 从Redis Cloud切换到Upstash
REDIS_HOST=new-host.upstash.io
REDIS_PORT=6379
REDIS_PASSWORD=new-password
```

### Q: 本地开发和Vercel部署可以用不同的Redis吗？

A: **可以**！使用不同的 `.env` 文件：
- 本地: `.env` (使用localhost或Docker)
- Vercel: 环境变量（使用Upstash）

## 性能对比

### 无缓存（Vercel Serverless）
```
/api/cities: ~150-300ms (冷启动)
/api/spots: ~200-500ms (读取文件)
```

### 有缓存（Upstash Redis）
```
/api/cities: ~50-100ms (缓存命中)
/api/spots: ~80-150ms (缓存命中)
性能提升: 60-70%
```

## 监控和维护

### 1. Upstash Dashboard
- 查看请求数量
- 监控延迟
- 查看存储使用

### 2. Vercel Analytics
- 函数执行时间
- 冷启动频率
- 错误率

### 3. 自定义监控
在代码中添加日志：
```python
import logging
logger.info(f"Cache hit rate: {hits}/{total}")
```

## 高级配置

### 使用Redis TLS（生产环境推荐）

Upstash默认支持TLS，无需额外配置。

对于Redis Cloud，如果需要TLS：
```python
# 在 agent/cache.py 中添加
self.redis_client = redis.Redis(
    ...
    ssl=True,
    ssl_cert_reqs=None  # 或使用证书验证
)
```

### 多区域部署

如果使用Vercel Edge Functions：
1. 在Upstash选择 "Global" 数据库
2. 自动路由到最近的节点
3. 更低的延迟

## 故障排除

### Redis连接超时

检查：
1. Vercel环境变量是否正确
2. Redis服务是否在线
3. 防火墙设置（通常云服务自动配置）

查看Vercel日志：
```bash
vercel logs
```

### 缓存未生效

1. 确认 `REDIS_ENABLED=True`
2. 检查 `/api/cache/stats`
3. 查看Upstash Dashboard

## 成本优化建议

### 1. 合理设置TTL
```python
# 静态数据使用更长TTL
cities_ttl = 172800  # 48小时

# 用户特定数据使用短TTL
plan_ttl = 3600  # 1小时
```

### 2. 使用缓存键命名空间
```python
# 便于批量清除
cache_key = f"v1:spots:{city}"  # 版本控制
```

### 3. 监控免费额度
- 设置Upstash告警
- 每周检查使用量
- 优化缓存策略

## 总结

✅ **推荐配置**：Vercel + Upstash
- 零配置复杂度
- 最佳性能
- 免费额度充足

🚀 **快速开始**：
1. 注册Upstash (5分钟)
2. 在Vercel添加环境变量 (2分钟)
3. 重新部署 (1分钟)
4. 验证 `/api/cache/stats` (1分钟)

**总计：10分钟即可在生产环境启用Redis缓存！**

## 相关资源

- 📖 [Upstash文档](https://docs.upstash.com/)
- 🚀 [Vercel环境变量](https://vercel.com/docs/concepts/projects/environment-variables)
- 🔧 [本地Redis配置](REDIS_CACHE_GUIDE.md)
