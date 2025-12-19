# 景点数据获取 API 文档

## 问题背景

在使用 `scripts/fetch_osm_spots.py` 脚本爬取城市景点数据时，当景点数量过多时，终端会被大量输出淹没，难以查看和管理。

## 解决方案

我们提供了一个 **REST API 接口** `/api/fetch_spots`，可以通过 HTTP 请求获取景点数据，返回结构化的 JSON 响应，避免终端输出过多。

---

## API 接口说明

### 接口信息

- **端点**: `/api/fetch_spots`
- **方法**: `POST`
- **Content-Type**: `application/json`

### 请求参数

```json
{
  "city": "Beijing",              // 必需：城市名称（英文）
  "session_id": "optional-id"     // 可选：会话 ID，用于 WebSocket 进度更新
}
```

### 响应格式

#### 成功响应 (200 OK)

```json
{
  "status": "success",
  "message": "Successfully fetched and saved 150 spots for Beijing",
  "data": {
    "city": "Beijing",
    "spots_count": 150,
    "file_path": "data/spots_beijing.json",
    "top_spots": [
      {
        "name": "故宫",
        "category": "history",
        "duration_minutes": 60,
        "rating": 4.0,
        "lat": 39.9163,
        "lon": 116.3972,
        "description": "..."
      }
      // ... 最多显示前 10 个景点
    ],
    "categories": {
      "history": 45,
      "museum": 30,
      "outdoor": 25,
      "sightseeing": 50
    }
  }
}
```

#### 错误响应 (4xx/5xx)

```json
{
  "status": "error",
  "code": 404,
  "message": "No data found",
  "reason": "No spots found for city: XYZ. Please check the city name."
}
```

---

## 使用方法

### 方法 1: 使用 Python 测试脚本（推荐）

我们提供了一个测试脚本 `test_fetch_spots_api.py`，可以方便地测试 API。

#### 1.1 确保 Flask 服务器正在运行

```bash
python app.py
```

#### 1.2 运行测试脚本

```bash
# 获取单个城市的景点数据
python test_fetch_spots_api.py Beijing

# 获取多个单词的城市名
python test_fetch_spots_api.py New York

# 交互式模式
python test_fetch_spots_api.py
```

**输出示例：**

```
正在请求 API 获取 Beijing 的景点数据...
URL: http://localhost:5000/api/fetch_spots
Payload: {
  "city": "Beijing"
}

✅ 成功!

城市: Beijing
景点数量: 150
保存路径: data/spots_beijing.json

分类统计:
  - history: 45 个景点
  - museum: 30 个景点
  - outdoor: 25 个景点
  - sightseeing: 50 个景点

前 10 个景点预览:
  1. 故宫 (history)
  2. 天坛 (history)
  3. 颐和园 (outdoor)
  ...
```

---

### 方法 2: 使用 curl 命令

```bash
# 基本用法
curl -X POST http://localhost:5000/api/fetch_spots \
  -H "Content-Type: application/json" \
  -d '{"city": "Beijing"}'

# 获取完整响应（格式化输出）
curl -X POST http://localhost:5000/api/fetch_spots \
  -H "Content-Type: application/json" \
  -d '{"city": "Shanghai"}' | python -m json.tool
```

---

### 方法 3: 使用 Python requests 库

```python
import requests
import json

# API 配置
url = "http://localhost:5000/api/fetch_spots"
city = "Beijing"

# 发送请求
response = requests.post(url, json={"city": city})

# 处理响应
if response.status_code == 200:
    result = response.json()
    
    if result['status'] == 'success':
        data = result['data']
        print(f"✅ 成功获取 {data['spots_count']} 个景点")
        print(f"数据已保存到: {data['file_path']}")
        
        # 查看前几个景点
        for spot in data['top_spots'][:5]:
            print(f"- {spot['name']} ({spot['category']})")
    else:
        print(f"❌ 错误: {result['message']}")
else:
    print(f"❌ HTTP 错误: {response.status_code}")
```

---

### 方法 4: 使用 Postman 或其他 API 测试工具

1. 创建新的 POST 请求
2. URL: `http://localhost:5000/api/fetch_spots`
3. Headers: `Content-Type: application/json`
4. Body (raw JSON):
   ```json
   {
     "city": "Beijing"
   }
   ```
5. 点击 Send

---

## WebSocket 进度更新（高级）

如果你提供了 `session_id` 参数，可以通过 WebSocket 接收实时进度更新。

### JavaScript 示例

```javascript
// 连接 WebSocket
const socket = io('http://localhost:5000');
const sessionId = 'unique-session-id-' + Date.now();

// 加入会话
socket.emit('join_session', { session_id: sessionId });

// 监听进度更新
socket.on('fetch_progress', (data) => {
  console.log(`进度: ${data.progress}%`);
  console.log(`状态: ${data.stage}`);
  
  if (data.progress === 100) {
    if (data.error) {
      console.error('获取失败:', data.message);
    } else {
      console.log(`成功获取 ${data.spots_count} 个景点！`);
    }
  }
});

// 发送 API 请求
fetch('http://localhost:5000/api/fetch_spots', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    city: 'Beijing',
    session_id: sessionId
  })
})
.then(res => res.json())
.then(data => console.log('最终结果:', data));
```

---

## 常见问题

### Q1: 为什么比原来的脚本更好？

**优势：**
1. ✅ **结构化输出**：JSON 格式，易于解析和处理
2. ✅ **数据预览**：只显示前 10 个景点，避免终端被淹没
3. ✅ **分类统计**：自动统计各类景点数量
4. ✅ **错误处理**：清晰的错误信息和状态码
5. ✅ **可编程**：可以轻松集成到其他应用中
6. ✅ **进度追踪**：支持 WebSocket 实时进度更新

### Q2: 数据保存在哪里？

和原来的脚本一样，数据保存在 `data/spots_<cityname>.json` 文件中。

### Q3: 支持哪些城市？

支持任何 OpenStreetMap 中存在的城市，只要城市名称正确即可。

**推荐使用英文城市名：**
- ✅ Beijing, Shanghai, Guangzhou
- ✅ New York, Los Angeles, San Francisco
- ✅ London, Paris, Tokyo

### Q4: 如果景点太多怎么办？

API 响应只返回前 10 个景点作为预览，完整数据保存在文件中。你可以：

1. 直接读取生成的 JSON 文件
2. 使用 `/api/spots/<city>` 接口获取完整数据
3. 在前端界面中选择需要的景点

### Q5: API 超时怎么办？

默认超时时间是 60 秒。如果城市景点特别多，可能需要更长时间。你可以：

```python
# 增加超时时间
response = requests.post(url, json={"city": city}, timeout=120)
```

---

## 与现有系统集成

### 查看已有城市

```bash
curl http://localhost:5000/api/cities
```

### 获取特定城市的景点

```bash
curl http://localhost:5000/api/spots/beijing
```

### 规划行程

```bash
curl -X POST http://localhost:5000/plan_itinerary \
  -H "Content-Type: application/json" \
  -d '{
    "city": "beijing",
    "start_date": "2025-01-01",
    "days": 3
  }'
```

---

## 示例工作流

```bash
# 1. 启动服务器
python app.py

# 2. 获取新城市的景点数据（在另一个终端）
python test_fetch_spots_api.py Hangzhou

# 3. 查看生成的文件
cat data/spots_hangzhou.json

# 4. 在 Web 界面中使用新城市规划行程
# 访问 http://localhost:5000
```

---

## 技术细节

### 数据来源
- 使用 OpenStreetMap Overpass API
- 自动查询旅游景点、博物馆、纪念碑等
- 支持中文和英文名称

### 数据字段
```json
{
  "name": "景点名称",
  "category": "分类 (outdoor/museum/history/shopping/food)",
  "duration_minutes": 60,
  "rating": 4.0,
  "lat": 纬度,
  "lon": 经度,
  "description": "描述"
}
```

### 错误码
- `400`: 请求参数错误
- `404`: 未找到城市或景点
- `500`: 服务器错误

---

## 总结

使用新的 API 接口，你可以：
- ✅ 避免终端输出过多
- ✅ 获得结构化的 JSON 响应
- ✅ 方便地集成到其他应用
- ✅ 实时追踪数据获取进度

**推荐用法：**
```bash
# 最简单的方式
python test_fetch_spots_api.py <城市名>
```

祝使用愉快！🎉
