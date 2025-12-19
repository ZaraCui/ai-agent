# 中国景点数据批量获取指南

## 功能说明

新增脚本 `scripts/fetch_china_spots.py` 可以批量获取中国景点数据。

## 两种模式

### 🌟 模式1: 批量获取主要城市（推荐）

获取中国35个主要城市的景点数据，包括：
- 一线城市：北京、上海、广州、深圳
- 新一线城市：成都、杭州、重庆、武汉、西安等
- 其他重要城市：昆明、厦门、大连、济南等

**优点**：
- ✅ 速度快（每个城市约1-2秒）
- ✅ 数据质量高
- ✅ 按城市分类清晰
- ✅ 总时间约1-2分钟

**使用方法**：
```bash
python scripts/fetch_china_spots.py --cities
```

### 模式2: 获取整个中国

获取整个中国范围内的所有景点数据。

**特点**：
- ⚠️ 数据量非常大（可能数万个景点）
- ⚠️ 耗时较长（可能超过60秒）
- ⚠️ 可能超时或失败

**使用方法**：
```bash
python scripts/fetch_china_spots.py --all
```

---

## 快速开始

### 第一步：查看使用说明

```bash
python scripts/fetch_china_spots.py
```

输出：
```
======================================================================
中国景点数据获取工具
======================================================================

使用方法:
  python fetch_china_spots.py --all      # 获取整个中国（数据量大，不推荐）
  python fetch_china_spots.py --cities   # 获取主要城市（推荐）✅

推荐使用 --cities 模式，更快且数据质量更好！
```

### 第二步：批量获取城市数据（推荐）

```bash
python scripts/fetch_china_spots.py --cities
```

### 预期输出示例

```
======================================================================
批量获取中国 35 个主要城市的景点数据
======================================================================

📍 模式: 批量获取中国主要城市
将获取约35个主要城市的景点数据

确认继续? (y/n): y

[1/35] 正在处理: Beijing
----------------------------------------------------------------------
✓ Beijing: 获取 156 个景点

[2/35] 正在处理: Shanghai
----------------------------------------------------------------------
✓ Shanghai: 获取 203 个景点

[3/35] 正在处理: Guangzhou
----------------------------------------------------------------------
✓ Guangzhou: 获取 328 个景点

... (继续处理其他城市) ...

======================================================================
批量获取完成！
======================================================================

✅ 成功: 35 个城市
❌ 失败: 0 个城市
📊 总景点数: 4567 个

🏙️  各城市景点数量 (前20):
  • Shanghai            :  203 个景点
  • Guangzhou           :  328 个景点
  • Beijing             :  156 个景点
  • Hangzhou            :  145 个景点
  • Chengdu             :  123 个景点
  ... (更多城市) ...

💾 数据已保存到: data/spots_china_cities_20251219_090500.json
📊 文件大小: 2.45 MB
💾 同时保存到: data/spots_china_cities.json

✨ 完成！
```

---

## 输出文件

### 生成的文件

1. **带时间戳的文件**：`data/spots_china_cities_YYYYMMDD_HHMMSS.json`
   - 用于备份，保留历史记录
   
2. **标准文件**：`data/spots_china_cities.json`
   - 最新版本，方便使用

### 数据格式

每个景点包含以下字段：

```json
{
  "name": "故宫",
  "category": "history",
  "duration_minutes": 60,
  "rating": 4.0,
  "lat": 39.9163,
  "lon": 116.3972,
  "city": "Beijing",
  "description": "A popular history spot in Beijing."
}
```

**新增字段**：
- `city`: 标记景点所属城市

---

## 包含的城市列表

### 一线城市（4个）
- Beijing（北京）
- Shanghai（上海）
- Guangzhou（广州）
- Shenzhen（深圳）

### 新一线城市（15个）
- Chengdu（成都）
- Hangzhou（杭州）
- Chongqing（重庆）
- Wuhan（武汉）
- Xi'an（西安）
- Suzhou（苏州）
- Zhengzhou（郑州）
- Nanjing（南京）
- Tianjin（天津）
- Changsha（长沙）
- Dongguan（东莞）
- Ningbo（宁波）
- Foshan（佛山）
- Qingdao（青岛）
- Shenyang（沈阳）

### 其他重要城市（16个）
- Kunming（昆明）
- Xiamen（厦门）
- Dalian（大连）
- Jinan（济南）
- Harbin（哈尔滨）
- Fuzhou（福州）
- Changchun（长春）
- Shijiazhuang（石家庄）
- Hefei（合肥）
- Nanchang（南昌）
- Guiyang（贵阳）
- Taiyuan（太原）
- Nanning（南宁）
- Urumqi（乌鲁木齐）
- Lanzhou（兰州）

**总计**: 35个主要城市

---

## 使用场景

### 场景1: 为旅行规划系统准备完整的中国城市数据

```bash
# 1. 批量获取所有主要城市数据
python scripts/fetch_china_spots.py --cities

# 2. 启动应用
python app.py

# 3. 在Web界面中选择任意城市开始规划
```

### 场景2: 分析中国旅游景点分布

```python
import json

# 读取数据
with open('data/spots_china_cities.json', 'r', encoding='utf-8') as f:
    spots = json.load(f)

# 统计各城市景点数量
city_stats = {}
for spot in spots:
    city = spot.get('city', 'unknown')
    city_stats[city] = city_stats.get(city, 0) + 1

# 显示统计
for city, count in sorted(city_stats.items(), key=lambda x: x[1], reverse=True):
    print(f"{city}: {count} 个景点")
```

### 场景3: 按城市分割数据

```python
import json

# 读取合并的数据
with open('data/spots_china_cities.json', 'r', encoding='utf-8') as f:
    all_spots = json.load(f)

# 按城市分组
city_spots = {}
for spot in all_spots:
    city = spot.get('city', 'unknown')
    if city not in city_spots:
        city_spots[city] = []
    city_spots[city].append(spot)

# 保存每个城市的单独文件
for city, spots in city_spots.items():
    filename = f"data/spots_{city.lower()}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(spots, f, indent=2, ensure_ascii=False)
    print(f"保存 {city}: {len(spots)} 个景点 -> {filename}")
```

---

## 常见问题

### Q1: 为什么推荐使用 --cities 模式？

**A:** 
- ✅ 更快（1-2分钟 vs 可能超时）
- ✅ 数据质量更好（每个城市单独查询）
- ✅ 自动添加城市标记
- ✅ 更可靠（不易失败）

### Q2: 获取的数据会重复吗？

**A:** 不会。脚本会自动去重，确保每个景点只出现一次。

### Q3: 数据保存在哪里？

**A:** 
- 主文件：`data/spots_china_cities.json`
- 备份：`data/spots_china_cities_YYYYMMDD_HHMMSS.json`

### Q4: 可以修改城市列表吗？

**A:** 可以！编辑 `scripts/fetch_china_spots.py` 中的 `major_cities` 列表：

```python
major_cities = [
    "Beijing", "Shanghai", "Guangzhou", "Shenzhen",
    "你想要的城市名"
]
```

### Q5: 批量获取需要多久？

**A:** 
- 35个城市约需要 1-2 分钟
- 每个城市间隔1秒（避免请求过快）
- 总时间 = (城市数量 × 2秒) + 35秒 ≈ 105秒

### Q6: 如何处理失败的城市？

**A:** 脚本会显示失败的城市列表，你可以单独重试：

```bash
# 单独获取失败的城市
python scripts/fetch_osm_spots_clean.py Urumqi
```

### Q7: 数据是最新的吗？

**A:** 是的，数据来自 OpenStreetMap，每次运行都会获取最新数据。

---

## 高级用法

### 自定义城市列表

创建一个自定义城市列表文件 `my_cities.txt`：
```
Beijing
Shanghai
Hangzhou
Chengdu
```

然后修改脚本读取这个文件（需要自己实现）。

### 定时更新

创建定时任务定期更新数据：

**Windows 任务计划程序**：
```batch
# 每周日凌晨2点更新
python C:\Travel-Planning-Agent\scripts\fetch_china_spots.py --cities
```

**Linux Cron**：
```bash
# 每周日凌晨2点更新
0 2 * * 0 cd /path/to/Travel-Planning-Agent && python scripts/fetch_china_spots.py --cities
```

---

## 性能优化建议

### 如果获取速度慢

1. **增加超时时间**：编辑脚本，修改 `timeout` 参数
2. **减少城市数量**：只获取你需要的城市
3. **分批获取**：分多次运行，每次获取部分城市

### 如果某些城市失败

1. **检查网络连接**
2. **稍后重试**（OpenStreetMap API 可能暂时繁忙）
3. **单独获取失败的城市**

---

## 对比三种方案

| 方案 | 文件 | 优点 | 用途 |
|------|------|------|------|
| 单城市（简洁） | `fetch_osm_spots_clean.py` | 快速、简单 | 获取单个城市 |
| 批量城市 ⭐ | `fetch_china_spots.py --cities` | 批量、高效 | 获取所有主要城市 |
| 整个中国 | `fetch_china_spots.py --all` | 全面 | 研究/分析用途 |

**推荐流程**：
1. 使用 `fetch_china_spots.py --cities` 批量获取主要城市
2. 如需其他城市，使用 `fetch_osm_spots_clean.py <城市名>` 单独获取

---

## 总结

### 最简单的用法

```bash
# 一行命令获取中国35个主要城市的所有景点数据
python scripts/fetch_china_spots.py --cities
```

### 预期结果

- ✅ 35个城市的景点数据
- ✅ 约4000-6000个景点
- ✅ 按城市分类
- ✅ 2-3 MB JSON文件
- ✅ 1-2分钟完成

**开始使用吧！** 🎉🇨🇳
