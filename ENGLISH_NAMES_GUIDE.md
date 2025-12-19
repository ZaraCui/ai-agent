# 中国景点英文名称添加说明

## 概述
为了让外国用户也能使用本旅行规划应用，我们为所有中国城市的景点添加了英文名称。

## 更新内容

### 1. 数据文件更新
- 为**所有城市**的景点数据文件添加了 `name_en` 字段
- 总计更新了 **17,938 个景点**，覆盖率 **100%**

#### 中国城市 (7,403 个景点)
- 北京 (2,351 个景点)
- 香港 (635 个景点)
- 青岛 (486 个景点)
- 成都 (416 个景点)
- 杭州 (406 个景点)
- 深圳 (400 个景点)
- 南京 (349 个景点)
- 广州 (328 个景点)
- 以及其他 17 个中国城市

#### 国际城市 (10,535 个景点)
- 柏林 (7,135 个景点)
- 京都 (1,947 个景点)
- 悉尼 (1,369 个景点)
- 巴塞罗那、纽约、伦敦、巴黎、东京等

### 2. 翻译策略
使用智能规则匹配进行翻译：
- 识别城市名称（如：北京 → Beijing，上海 → Shanghai）
- 识别景点类型（如：博物馆 → Museum，公园 → Park）
- 保留专有名词（无法翻译的部分保留原中文名）
- 对已有英文名的景点保持不变

### 3. 前端界面更新
- **景点选择列表**：在中文名称下方显示英文名称（如果存在且不同）
- **行程规划卡片**：在景点标题下方显示英文名称
- 自动判断：当英文名与中文名相同时不重复显示

### 4. 新增脚本
创建了 `scripts/add_english_names.py` 脚本用于：
- 批量为景点添加英文名称
- 支持 `--force` 参数强制更新现有翻译
- 可扩展的翻译词汇表

## 使用方法

### 查看更新后的景点
所有景点 JSON 文件现在包含 `name_en` 字段：
```json
{
  "name": "故宫博物院",
  "name_en": "Beijing Palace Museum",
  "category": "museum",
  "duration_minutes": 180,
  "rating": 4.8,
  ...
}
```

### 重新运行翻译脚本（如需要）
```bash
# 仅添加缺失的英文名称
python scripts/add_english_names.py

# 强制更新所有英文名称
python scripts/add_english_names.py --force
```

### 添加新的翻译规则
编辑 `scripts/add_english_names.py` 中的 `CATEGORY_TRANSLATIONS` 字典：
```python
CATEGORY_TRANSLATIONS = {
    "新词汇": "New Translation",
    ...
}
```

## 示例效果

### 东莞景点示例
- **东莞博物馆** → Dongguang Museum
- **东莞植物园** → Dongguang Botanical Garden
- **东莞市科学技术博物馆** → Dongguang Science & Technology Museum

### 广州景点示例
- **广州塔** → Guangzhou Tower
- **陈家祠** → Chen Clan Ancestral Hall
- **白云山** → Baiyun Mountain

## 注意事项

1. **专有名词保留**：一些包含专有名词或特殊名称的景点可能保留部分中文
2. **翻译质量**：基于规则的翻译可能不如人工翻译精准，但能提供基本的英文参考
3. **持续改进**：可以根据用户反馈不断优化翻译规则和词汇表

## 技术细节

- **脚本位置**：`scripts/add_english_names.py`
- **前端文件**：`static/index.html`, `templates/index.html`
- **数据目录**：`data/`
- **编码**：UTF-8，确保中英文字符正确显示

## 未来改进方向

1. 集成专业翻译 API（如 Google Translate）提高翻译质量
2. 添加多语言支持（日语、韩语等）
3. 允许用户贡献和修正翻译
4. 建立景点名称翻译数据库
