# AI景点描述生成器使用指南

## 📖 概述

这个工具使用ChatGPT API自动为景点生成多样化、生动的描述文本，解决原有描述同质化的问题。

## 🚀 快速开始

### 1. 配置OpenAI API密钥

在项目根目录的`.env`文件中添加你的OpenAI API密钥：

```bash
OPENAI_API_KEY=sk-your-api-key-here
```

**获取API密钥：** https://platform.openai.com/api-keys

### 2. 安装依赖

OpenAI库已经包含在`requirements.txt`中，如果已安装依赖则跳过此步：

```bash
pip install -r requirements.txt
```

### 3. 运行脚本

```bash
python scripts/generate_ai_descriptions.py
```

## 📋 功能特性

### ✨ 多种描述风格

脚本支持5种不同的描述风格，可以为景点生成多样化的内容：

1. **简洁实用** - 信息密集，突出实用信息
2. **文艺优美** - 优美的文学化描述
3. **历史文化** - 强调历史文化背景
4. **生活体验** - 从游客体验角度描述
5. **地理特色** - 强调地理和自然特色

还支持**随机模式**（推荐），为每个景点随机选择风格，增加多样性。

### 🎯 智能提示词

脚本使用精心设计的提示词，确保生成的描述：
- 长度适中（80-150字）
- 自然流畅，避免模板化
- 突出景点独特性
- 包含实用信息
- 语言生动但不夸张
- 避免"这是..."、"位于..."等模板化开头

### 🔧 灵活配置

- **选择城市**：处理特定城市或所有城市
- **数量控制**：限制每个城市处理的景点数量
- **模型选择**：支持gpt-3.5-turbo、gpt-4、gpt-4-turbo
- **预览模式**：先预览效果，不保存修改
- **断点续传**：支持从特定景点开始处理

## 💡 使用示例

### 示例1：测试单个城市（预览模式）

```bash
python scripts/generate_ai_descriptions.py
```

交互式输入：
```
城市: kunming
每个城市最多处理多少个景点: 5
选择风格: 6 (随机)
选择模型: 1 (gpt-3.5-turbo)
预览模式: y
确认开始处理: y
```

### 示例2：批量处理多个城市

```bash
python scripts/generate_ai_descriptions.py
```

交互式输入：
```
城市: beijing,shanghai,guangzhou
每个城市最多处理多少个景点: 20
选择风格: 6 (随机)
选择模型: 1 (gpt-3.5-turbo)
预览模式: n
确认开始处理: y
```

### 示例3：处理所有城市（慎用）

```bash
python scripts/generate_ai_descriptions.py
```

交互式输入：
```
城市: all
每个城市最多处理多少个景点: (留空，处理全部)
选择风格: 6 (随机)
选择模型: 1 (gpt-3.5-turbo)
预览模式: n
确认开始处理: y
```

## 📊 生成示例

### 原始描述（模板化）
```
这是昆明的一个自然景点白龙潭公园，是一个著名景点 | 位于：锦绣大街 | 景点类型：风景名胜 | 建议游览时间：2小时
```

### AI生成描述（简洁实用风格）
```
白龙潭公园是昆明市区内难得的山水园林，以清澈的龙潭和古树名木著称。公园内有多处泉眼，水质清冽，四季常流。适合周末休闲散步，也是摄影爱好者的好去处。建议游览2小时，春季樱花盛开时最美。
```

### AI生成描述（文艺优美风格）
```
白龙潭公园藏于城市一隅，泉水叮咚，古树参天。潭水碧绿如镜，倒映着四季变换的景致。漫步林间小径，听鸟语闻花香，仿佛置身世外桃源。这里是都市人寻找宁静的理想之地，每个季节都有独特的韵味。
```

## 💰 费用估算

使用OpenAI API会产生费用，以gpt-3.5-turbo为例：

- **每个描述成本**：约 $0.001-0.002（根据token数量）
- **100个景点**：约 $0.10-0.20
- **1000个景点**：约 $1.00-2.00

**建议**：
1. 先用预览模式测试少量景点
2. 使用gpt-3.5-turbo模型（性价比高）
3. 设置数量限制，分批处理

## ⚠️ 注意事项

### 1. API速率限制
脚本内置1秒延迟，避免触发API速率限制。如果账户有更高限制，可以在代码中调整`time.sleep(1)`。

### 2. 数据备份
建议在批量处理前备份数据文件：
```bash
cp -r data data_backup
```

### 3. 错误处理
如果某个景点生成失败，脚本会保留原描述并继续处理下一个。

### 4. 断点续传
如果中途中断，可以使用`start_from`参数从特定位置继续：
```python
process_city_spots('kunming', start_from=50)
```

## 🔍 检查生成结果

生成后，可以随机检查几个景点的描述质量：

```bash
# 查看昆明前5个景点的描述
python -c "
import json
with open('data/spots_kunming.json', 'r', encoding='utf-8') as f:
    spots = json.load(f)
for i, spot in enumerate(spots[:5]):
    print(f'{i+1}. {spot[\"name\"]}')
    print(f'   {spot[\"description\"]}\n')
"
```

## 📈 最佳实践

1. **先小规模测试**：选择1-2个城市，每个5-10个景点，使用预览模式
2. **检查质量**：查看生成的描述是否符合期望
3. **调整风格**：根据需要选择合适的风格或使用随机模式
4. **分批处理**：不要一次处理太多，避免长时间运行和费用失控
5. **版本控制**：使用git提交更改前的版本，方便回滚

## 🛠️ 高级用法

### 自定义提示词

如果需要调整描述风格，可以修改`generate_ai_descriptions.py`中的`prompt`变量：

```python
prompt = f"""请为以下景点生成描述...
要求：
1. 你的自定义要求
2. ...
"""
```

### 批量处理脚本

创建一个批处理脚本自动处理多个城市：

```python
from generate_ai_descriptions import process_city_spots

cities = ['beijing', 'shanghai', 'guangzhou', 'shenzhen']
for city in cities:
    print(f"Processing {city}...")
    process_city_spots(
        city, 
        max_spots=20,
        style="随机",
        model="gpt-3.5-turbo",
        dry_run=False
    )
```

## 🤝 与其他脚本的关系

- **improve_descriptions.py**：旧的描述改进脚本，基于模板
- **generate_ai_descriptions.py**：新的AI生成脚本，生成多样化描述

建议：先运行新的AI脚本，如果有API限制或费用考虑，再用旧脚本处理剩余景点。

## ❓ 常见问题

### Q1: API密钥无效
**A**: 确保`.env`文件中的`OPENAI_API_KEY`设置正确，并且账户有余额。

### Q2: 生成速度慢
**A**: 这是正常的，每个请求有1秒延迟以避免速率限制。处理100个景点约需2-3分钟。

### Q3: 生成的描述太长/太短
**A**: 可以在prompt中调整字数要求，如"60-100字"或"100-200字"。

### Q4: 想使用其他AI模型
**A**: 可以修改代码支持其他OpenAI兼容的API，如Claude、文心一言等。

### Q5: 如何批量回滚
**A**: 如果之前做了git commit或备份，可以恢复：
```bash
git checkout -- data/spots_*.json
# 或
cp data_backup/* data/
```

## 📞 技术支持

如果遇到问题，请检查：
1. OpenAI API密钥是否有效
2. 网络连接是否正常
3. 账户余额是否充足
4. Python环境是否正确安装依赖

## 📄 许可证

本工具遵循项目的主许可证。使用OpenAI API时，请遵守OpenAI的使用条款。
