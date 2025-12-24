# 高德地图 API 景点数据采集指南

## 📋 准备工作

### 1. 获取 API Key
- 访问：https://console.amap.com
- 注册并登录
- 创建新应用（应用类型选择：Web 服务）
- 复制你的 API Key

### 2. 配置 API Key

**方式一：环境变量（推荐）**
```bash
export GAODE_API_KEY="your_actual_api_key_here"
```

**方式二：.env 文件**
```bash
# 复制示例文件
cp .env.example .env

# 编辑 .env，填入你的 API Key
# GAODE_API_KEY=your_actual_api_key_here
```

**方式三：Docker 环境**
```bash
docker run -e GAODE_API_KEY="your_key" your_image
```

## 🚀 运行脚本

### 获取所有城市数据
```bash
python scripts/fetch_gaode_scenic.py
```

### 仅获取特定城市（可选）
编辑脚本中的 `CITIES` 字典，注释掉不需要的城市。

## 📊 输出

脚本会生成以下文件：
- `data/spots_beijing.json`
- `data/spots_shanghai.json`
- ... 等等

每个文件包含该城市的景点数据，格式如下：
```json
[
  {
    "name": "景点名称",
    "category": "sightseeing|museum|outdoor|history",
    "duration_minutes": 120,
    "rating": 4.0,
    "lat": 39.9,
    "lon": 116.4,
    "description": "景点描述和地址信息",
    "city": "北京"
  }
]
```

## ⚙️ 配置说明

### API 配额
- 高德地图 Web 服务 API：日均 50,000 次调用
- 本脚本单次运行约需 25 个城市 × 1-50 页 = ~1000-2000 次调用
- 足够日常使用

### 超时处理
- 单次请求超时：15 秒
- 请求间隔：0.5 秒（避免限流）
- 城市间隔：1 秒

## 🐛 故障排查

### 错误：GAODE_API_KEY 环境变量未设置
**解决**：按照上面的"配置 API Key"部分设置

### 错误：高德 API 返回 status != '1'
**可能原因**：
- API Key 无效
- API Key 没有启用"Web 服务"权限
- 搜索词无效

**解决**：
1. 检查 API Key 是否正确
2. 在高德控制台确认已启用"Web 服务"API
3. 尝试手动访问：
```
https://restapi.amap.com/v3/place/text?key=YOUR_KEY&keywords=景点&region=北京&output=json
```

### 请求超时
**原因**：网络问题或 API 服务响应慢

**解决**：
1. 检查网络连接
2. 增加超时时间（编辑脚本中的 `timeout=15` 参数）
3. 稍后重试

## 💡 高级用法

### 修改搜索关键词
编辑脚本中的 `keywords` 参数，比如：
```python
'keywords': '博物馆',  # 只搜索博物馆
'keywords': '公园',    # 只搜索公园
```

### 修改每页数量
```python
'pagesize': 50,  # 最多 50，可改为 20, 30 等
```

### 添加更多城市
编辑 `CITIES` 字典：
```python
CITIES = {
    "beijing": "北京",
    "yourciity": "你的城市",
    ...
}
```

## 📞 支持

如有问题，检查：
1. API Key 有效性
2. 网络连接
3. 高德控制台的 API 使用情况
