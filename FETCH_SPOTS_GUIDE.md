# 景点数据获取指南

## 问题

使用 `scripts/fetch_osm_spots.py` 时，景点太多会导致终端输出过多，难以查看。

## 解决方案 ✅

使用改进版脚本 **`scripts/fetch_osm_spots_clean.py`**

### 主要改进

✅ **简洁清晰的输出** - 只显示摘要信息和前10个景点预览  
✅ **分类统计** - 自动统计各类景点数量  
✅ **进度提示** - 清楚显示每个步骤的进度  
✅ **完整数据** - 所有景点数据仍然保存到文件  
✅ **友好错误提示** - 明确的错误信息和建议

---

## 快速使用

### 基本用法

```bash
# 获取单个城市的景点数据
python scripts/fetch_osm_spots_clean.py Guangzhou

# 获取其他城市
python scripts/fetch_osm_spots_clean.py Beijing
python scripts/fetch_osm_spots_clean.py Shanghai
python scripts/fetch_osm_spots_clean.py Shenzhen
```

### 多个单词的城市名

```bash
# 使用引号括起来
python scripts/fetch_osm_spots_clean.py "New York"
python scripts/fetch_osm_spots_clean.py "Los Angeles"
python scripts/fetch_osm_spots_clean.py "Hong Kong"
```

### 详细模式

```bash
# 显示更多处理进度
python scripts/fetch_osm_spots_clean.py Beijing --verbose
python scripts/fetch_osm_spots_clean.py Shanghai -v
```

---

## 输出示例

```
============================================================
正在获取 Guangzhou 的景点数据...
============================================================

[1/3] 查找城市地理信息...
✓ 找到城市区域 ID: 3603287346

[2/3] 从 OpenStreetMap 获取景点数据...
✓ API 请求成功

[3/3] 处理景点数据...

============================================================
✅ 成功获取 328 个景点
============================================================

📊 分类统计:
  • sightseeing     : 117 个景点
  • history         :  90 个景点
  • museum          :  86 个景点
  • outdoor         :  35 个景点

📍 前 10 个景点预览:
   1. "Airport" Sign (rest point) (sightseeing)
   2. 3号炮池 (history)
   3. Baishuizhai mountain main entrance (sightseeing)
   4. Chinese Coin House somewhere here (sightseeing)
   5. Chinese Opera Museum (museum)
   6. Deers (sightseeing)
   7. Spring Garden (sightseeing)
   8. 一号炮池 (history)
   9. 七十二家房客拍摄基地 (sightseeing)
  10. 万木草堂 (museum)
  ... 还有 318 个景点

💾 数据已保存到: data/spots_guangzhou.json

✨ 完成！你现在可以在旅行规划系统中使用 Guangzhou 了。
```

---

## 对比

### 旧版本 (fetch_osm_spots.py)

```bash
python scripts/fetch_osm_spots.py Guangzhou
```

**问题：**
- ❌ 终端被328条景点数据淹没
- ❌ 难以快速了解数据概况
- ❌ 没有分类统计
- ❌ 错误信息不够友好

### 新版本 (fetch_osm_spots_clean.py)

```bash
python scripts/fetch_osm_spots_clean.py Guangzhou
```

**优势：**
- ✅ 只显示前10个景点预览
- ✅ 提供清晰的分类统计
- ✅ 显示步骤进度
- ✅ 友好的错误提示
- ✅ 完整数据保存到文件

---

## 查看完整数据

虽然终端只显示前10个景点，但完整数据已保存到文件：

```bash
# 查看完整数据（Windows）
type data\spots_guangzhou.json

# 查看完整数据（Linux/Mac）
cat data/spots_guangzhou.json

# 或者在 Python 中读取
python -c "import json; data = json.load(open('data/spots_guangzhou.json', encoding='utf-8')); print(f'共 {len(data)} 个景点')"
```

---

## 批量获取多个城市

创建一个批处理脚本：

### Windows (batch_fetch.bat)

```batch
@echo off
python scripts/fetch_osm_spots_clean.py Guangzhou
python scripts/fetch_osm_spots_clean.py Shenzhen
python scripts/fetch_osm_spots_clean.py Hangzhou
python scripts/fetch_osm_spots_clean.py Chengdu
echo 完成！
```

### Linux/Mac (batch_fetch.sh)

```bash
#!/bin/bash
python scripts/fetch_osm_spots_clean.py Guangzhou
python scripts/fetch_osm_spots_clean.py Shenzhen
python scripts/fetch_osm_spots_clean.py Hangzhou
python scripts/fetch_osm_spots_clean.py Chengdu
echo "完成！"
```

---

## 常见问题

### Q: 为什么找不到城市？

**A:** 请检查：
- 使用英文城市名（推荐）
- 拼写是否正确
- 多个单词的城市名要用引号括起来

### Q: 景点数据不完整？

**A:** 这取决于 OpenStreetMap 的数据质量。不同城市的数据完整度不同。

### Q: 可以获取中文城市名吗？

**A:** 可以尝试，但建议使用英文名以获得更好的结果。

### Q: 数据保存在哪里？

**A:** `data/spots_<cityname>.json`  
例如：`data/spots_guangzhou.json`

### Q: 如何在系统中使用新城市？

**A:** 
1. 运行脚本获取数据
2. 启动应用：`python app.py`
3. 在 Web 界面中选择新城市
4. 开始规划行程

---

## 技术说明

### 数据来源
- **OpenStreetMap** - 开源地图数据
- **Overpass API** - OSM 数据查询接口
- **Nominatim** - 城市地理信息查询

### 景点类型
- `sightseeing` - 观光景点
- `history` - 历史遗迹
- `museum` - 博物馆
- `outdoor` - 户外景点

### 默认数据
- `duration_minutes`: 60（默认游玩时长）
- `rating`: 4.0（默认评分）

---

## 两种方案对比

### 方案1: 改进的脚本 ⭐ **推荐**

**文件**: `scripts/fetch_osm_spots_clean.py`

**优点：**
- ✅ 无需启动服务器
- ✅ 直接在终端运行
- ✅ 输出简洁清晰
- ✅ 使用简单

**使用：**
```bash
python scripts/fetch_osm_spots_clean.py <城市名>
```

### 方案2: REST API 接口

**文件**: `app.py` 中的 `/api/fetch_spots` 接口

**优点：**
- ✅ 可通过 HTTP 调用
- ✅ 返回 JSON 格式
- ✅ 支持 WebSocket 进度更新
- ✅ 可集成到前端

**使用：**
```bash
# 需要先启动服务器
python app.py

# 然后调用 API
python test_fetch_spots_api.py <城市名>
```

**推荐**: 如果只是想快速获取数据，使用方案1（改进的脚本）更简单直接！

---

## 总结

**最简单的使用方式：**

```bash
python scripts/fetch_osm_spots_clean.py <城市名>
```

**一行命令，获取景点数据，简洁清晰！** 🎉
