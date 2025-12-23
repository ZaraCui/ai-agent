# 高德地图周围美食和商铺补充指南

## 📋 功能说明

使用高德地图的周边搜索 API，为每个景点获取：
- 🍜 **周围美食**：餐厅、咖啡厅、奶茶店等（最多 5 个）
- 🛒 **周围商铺**：超市、购物、便利店等（最多 5 个）

## 🚀 快速使用

### 前置条件
- 已设置 `GAODE_API_KEY` 环境变量
- 已有景点数据文件（`data/spots_*.json`）

### 运行脚本

**1. 处理所有城市**
```bash
python scripts/enrich_spots_nearby.py
# 选择：1
```

**2. 仅处理主要中国城市**
```bash
python scripts/enrich_spots_nearby.py
# 选择：2
```

**3. 处理特定城市**
```bash
python scripts/enrich_spots_nearby.py
# 选择：3
# 输入：beijing,shanghai,shenzhen
```

## 📊 数据格式

处理后的景点数据会包含：

```json
{
  "name": "天安门广场",
  "category": "outdoor",
  "lat": 39.903182,
  "lon": 116.397755,
  "rating": 4.0,
  "description": "...",
  
  "nearby_foods": [
    {
      "name": "全聚德（前门店）",
      "category": "烤鸭",
      "distance": 450.5,
      "phone": "010-xxxxx",
      "address": "..."
    },
    ...
  ],
  
  "nearby_shops": [
    {
      "name": "超市123",
      "category": "超市",
      "distance": 200.3,
      "phone": "010-xxxxx",
      "address": "..."
    },
    ...
  ]
}
```

## ⚙️ 配置说明

### 搜索范围
- **美食搜索半径**：1500 米
- **商铺搜索半径**：1500 米
- 可以在 `SEARCH_TYPES` 中修改

### 搜索关键词
编辑脚本中的 `SEARCH_TYPES` 字典来自定义搜索词：

```python
SEARCH_TYPES = {
    'foods': {
        'keywords': ['餐厅', '咖啡厅', '奶茶店', '...'],  # 添加更多关键词
    },
    'shops': {
        'keywords': ['超市', '购物', '...'],
    }
}
```

## 💡 高级用法

### 仅处理特定城市
编辑脚本，在 `main()` 函数中硬编码城市列表：

```python
cities_to_process = ['beijing', 'shanghai', 'shenzhen']
```

### 修改返回数量
在 `fetch_nearby_foods()` 和 `fetch_nearby_shops()` 函数中修改 `limit` 参数：

```python
foods = fetch_nearby_foods(lat, lon, limit=10)  # 返回 10 个美食
shops = fetch_nearby_shops(lat, lon, limit=10)  # 返回 10 个商铺
```

### 处理速度优化
增加或减少 `time.sleep()` 的时间来控制 API 调用频率：

```python
time.sleep(0.3)  # 景点间隔
time.sleep(0.2)  # 搜索词间隔
```

## 🐛 故障排查

### 错误：GAODE_API_KEY 环境变量未设置
```bash
export GAODE_API_KEY="your_key"
python scripts/enrich_spots_nearby.py
```

### 获取失败但脚本继续运行
- 脚本会跳过坐标无效的景点（lat=0, lon=0）
- 失败的景点会得到空的 `nearby_foods` 和 `nearby_shops`
- 检查 API 配额是否已用尽

### API 超时或限流
- 增加 `time.sleep()` 的延迟时间
- 减少单次获取的数量
- 分批处理不同城市

## 📈 性能指标

- **平均处理速度**：每个景点 1-2 秒（包括 API 调用）
- **API 调用数**：每个景点约 10-15 次调用
  - 美食搜索：~5 个关键词 × 1 页 = 5 次
  - 商铺搜索：~4 个关键词 × 1 页 = 4 次
- **总处理时间**（以北京 200 个景点为例）：约 10-15 分钟

## 🔗 相关文档

- [高德地图周边搜索 API](https://lbs.amap.com/api/webservice/guide/api/search)
- [GAODE_API_GUIDE.md](GAODE_API_GUIDE.md) - 高德 API 基础配置

## 📝 更新日志

- **v1.0** (2025-12-23) - 初始版本，支持美食和商铺搜索
