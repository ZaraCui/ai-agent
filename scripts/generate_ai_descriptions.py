#!/usr/bin/env python3
"""
使用ChatGPT API生成多样化的景点描述
Generate diverse spot descriptions using ChatGPT API
"""

import json
import os
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

# 尝试导入OpenAI库
try:
    from openai import OpenAI
except ImportError:
    print("❌ 未安装openai库，请运行: pip install openai")
    exit(1)

# 加载环境变量
load_dotenv()

# 初始化OpenAI客户端
def get_openai_client():
    """获取OpenAI客户端"""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key or api_key == 'your_openai_api_key_here':
        print("❌ 请在.env文件中设置OPENAI_API_KEY")
        print("   获取API Key: https://platform.openai.com/api-keys")
        exit(1)
    return OpenAI(api_key=api_key)

# 描述风格模板
DESCRIPTION_STYLES = [
    "简洁实用",  # 简洁、信息密集
    "文艺优美",  # 优美的文学化描述
    "历史文化",  # 强调历史文化背景
    "生活体验",  # 从游客体验角度描述
    "地理特色",  # 强调地理和自然特色
]

def generate_spot_description(
    client: OpenAI,
    spot: Dict[str, Any],
    city: str,
    style: str = "简洁实用",
    model: str = "gpt-3.5-turbo"
) -> str:
    """
    使用ChatGPT生成景点描述
    
    Args:
        client: OpenAI客户端
        spot: 景点信息字典
        city: 城市名称
        style: 描述风格
        model: 使用的模型
    
    Returns:
        生成的描述文本
    """
    name = spot.get('name', '')
    category = spot.get('category', 'sightseeing')
    lat = spot.get('lat', 0)
    lon = spot.get('lon', 0)
    duration = spot.get('duration_minutes', 120)
    
    # 类别中文映射
    category_cn = {
        'museum': '博物馆',
        'history': '历史遗迹',
        'outdoor': '户外自然',
        'sightseeing': '观光景点',
        'shopping': '购物',
        'food': '美食',
        'entertainment': '娱乐'
    }.get(category, '景点')
    
    # 构建提示词
    prompt = f"""请为以下景点生成一个生动、准确、有吸引力的中文描述（80-150字）：

景点名称：{name}
所在城市：{city}
景点类别：{category_cn}
建议游览时间：{duration}分钟

要求：
1. 风格：{style}
2. 突出景点的独特性和特色
3. 描述要自然流畅，避免模板化
4. 包含实用信息（如适合的游客类型、最佳游览时间等）
5. 语言生动有趣，但不夸张
6. 不要使用"这是..."、"位于..."等开头
7. 直接描述景点本身的特点

请只返回描述文本，不要有其他内容。"""

    try:
        # 调用ChatGPT API
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "你是一个专业的旅游文案写作专家，擅长撰写生动、准确、有吸引力的景点描述。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.8,  # 增加创造性
            max_tokens=300
        )
        
        description = response.choices[0].message.content.strip()
        return description
        
    except Exception as e:
        print(f"  ⚠️ 生成描述失败: {e}")
        return spot.get('description', '')

def process_city_spots(
    city: str,
    max_spots: Optional[int] = None,
    style: str = "随机",
    model: str = "gpt-3.5-turbo",
    dry_run: bool = False,
    start_from: int = 0
) -> int:
    """
    处理城市的所有景点
    
    Args:
        city: 城市代码
        max_spots: 最多处理的景点数量
        style: 描述风格（"随机"表示随机选择）
        model: 使用的模型
        dry_run: 是否仅预览不保存
        start_from: 从第几个景点开始（用于断点续传）
    
    Returns:
        处理的景点数量
    """
    input_path = Path(f'data/spots_{city}.json')
    
    if not input_path.exists():
        print(f"❌ 文件不存在: {input_path}")
        return 0
    
    # 城市中文名称映射
    city_cn_map = {
        'beijing': '北京', 'shanghai': '上海', 'shenzhen': '深圳',
        'guangzhou': '广州', 'chengdu': '成都', 'hangzhou': '杭州',
        'suzhou': '苏州', 'nanjing': '南京', 'qingdao': '青岛',
        'xiamen': '厦门', 'wuhan': '武汉', 'xian': '西安',
        'kunming': '昆明', 'fuzhou': '福州', 'changchun': '长春',
        'harbin': '哈尔滨', 'shenyang': '沈阳', 'taiyuan': '太原',
        'lanzhou': '兰州', 'xining': '西宁', 'urumqi': '乌鲁木齐',
        'guiyang': '贵阳', 'nanning': '南宁', 'jinan': '济南',
        'zhengzhou': '郑州', 'hefei': '合肥', 'ningbo': '宁波',
        'shijiazhuang': '石家庄', 'foshan': '佛山',
        'hongkong': '香港', 'tokyo': '东京', 'kyoto': '京都',
        'paris': '巴黎', 'london': '伦敦', 'newyork': '纽约',
        'sydney': '悉尼', 'barcelona': '巴塞罗那', 'berlin': '柏林'
    }
    
    city_cn = city_cn_map.get(city, city.title())
    
    print(f"\n{'='*70}")
    print(f"🏙️  处理城市: {city_cn} ({city})")
    print(f"{'='*70}")
    
    # 读取数据
    with open(input_path, 'r', encoding='utf-8') as f:
        spots = json.load(f)
    
    total_spots = len(spots)
    print(f"📊 总景点数: {total_spots}")
    
    if max_spots:
        spots = spots[:max_spots]
        print(f"🔢 本次处理: {len(spots)} 个景点")
    
    if start_from > 0:
        spots = spots[start_from:]
        print(f"⏩ 从第 {start_from + 1} 个景点开始")
    
    # 初始化OpenAI客户端
    client = get_openai_client()
    
    # 处理每个景点
    processed_count = 0
    import random
    
    for i, spot in enumerate(spots, start=start_from):
        spot_name = spot.get('name', 'Unknown')
        print(f"\n[{i+1}/{total_spots}] 处理: {spot_name}")
        
        # 选择风格
        current_style = style
        if style == "随机":
            current_style = random.choice(DESCRIPTION_STYLES)
            print(f"  风格: {current_style}")
        
        # 生成新描述
        old_description = spot.get('description', '')
        new_description = generate_spot_description(
            client, spot, city_cn, current_style, model
        )
        
        if new_description and new_description != old_description:
            print(f"  ✅ 生成成功")
            print(f"  旧: {old_description[:50]}...")
            print(f"  新: {new_description[:100]}...")
            
            if not dry_run:
                spot['description'] = new_description
                processed_count += 1
            else:
                processed_count += 1
        else:
            print(f"  ⚠️ 未生成新描述")
        
        # 避免API速率限制
        if i < len(spots) - 1:
            time.sleep(1)  # 每个请求间隔1秒
    
    # 保存
    if not dry_run and processed_count > 0:
        # 读取完整数据（因为可能只处理了部分）
        with open(input_path, 'r', encoding='utf-8') as f:
            all_spots = json.load(f)
        
        # 更新处理过的景点
        for i, spot in enumerate(spots, start=start_from):
            all_spots[i] = spot
        
        with open(input_path, 'w', encoding='utf-8') as f:
            json.dump(all_spots, f, ensure_ascii=False, indent=2)
        print(f"\n✅ 已保存到 {input_path}")
    elif dry_run:
        print(f"\n🔍 预览模式：未保存更改")
    
    return processed_count

def main():
    """主函数"""
    print("="*70)
    print("🤖 ChatGPT景点描述生成器")
    print("="*70)
    print("\n此工具将使用OpenAI API为景点生成多样化的描述")
    print("注意：使用API会产生费用，请确保已设置API密钥\n")
    
    # 获取所有景点文件
    data_dir = Path('data')
    spot_files = sorted(data_dir.glob('spots_*.json'))
    
    if not spot_files:
        print("❌ 未找到景点数据文件")
        return
    
    cities = [f.stem.replace('spots_', '') for f in spot_files]
    
    print(f"找到 {len(cities)} 个城市的景点数据\n")
    
    # 选择城市
    print("请输入要处理的城市代码（逗号分隔，或输入'all'处理所有）:")
    print(f"可用城市: {', '.join(cities[:10])}...")
    city_input = input("城市: ").strip().lower()
    
    if city_input == 'all':
        cities_to_process = cities
    else:
        cities_to_process = [c.strip() for c in city_input.split(',')]
    
    # 选择数量
    max_spots_input = input("\n每个城市最多处理多少个景点？(留空=全部): ").strip()
    max_spots = int(max_spots_input) if max_spots_input else None
    
    # 选择风格
    print("\n描述风格:")
    for i, s in enumerate(DESCRIPTION_STYLES, 1):
        print(f"  {i}. {s}")
    print(f"  {len(DESCRIPTION_STYLES)+1}. 随机（推荐）")
    
    style_input = input("选择风格 (1-6): ").strip()
    try:
        style_idx = int(style_input) - 1
        if style_idx == len(DESCRIPTION_STYLES):
            style = "随机"
        else:
            style = DESCRIPTION_STYLES[style_idx]
    except:
        style = "随机"
    
    # 选择模型
    print("\n选择模型:")
    print("  1. gpt-3.5-turbo (便宜，快速)")
    print("  2. gpt-4 (质量更高，较贵)")
    print("  3. gpt-4-turbo (平衡选择)")
    
    model_input = input("选择模型 (1-3, 默认1): ").strip()
    models = {
        '1': 'gpt-3.5-turbo',
        '2': 'gpt-4',
        '3': 'gpt-4-turbo-preview'
    }
    model = models.get(model_input, 'gpt-3.5-turbo')
    
    # 预览模式
    dry_run_input = input("\n预览模式？(y/n, 默认n): ").strip().lower()
    dry_run = dry_run_input == 'y'
    
    # 确认
    print("\n" + "="*70)
    print("📋 处理配置:")
    print(f"  城市: {', '.join(cities_to_process)}")
    print(f"  数量: {'全部' if not max_spots else f'每城市{max_spots}个'}")
    print(f"  风格: {style}")
    print(f"  模型: {model}")
    print(f"  模式: {'预览（不保存）' if dry_run else '正式（保存）'}")
    print("="*70)
    
    confirm = input("\n确认开始处理？(y/n): ").strip().lower()
    if confirm != 'y':
        print("已取消")
        return
    
    # 处理
    total_processed = 0
    for city in cities_to_process:
        if city in cities:
            count = process_city_spots(
                city, 
                max_spots=max_spots,
                style=style,
                model=model,
                dry_run=dry_run
            )
            total_processed += count
        else:
            print(f"⚠️ 城市 {city} 未找到")
    
    print("\n" + "="*70)
    print(f"✅ 完成！共处理 {total_processed} 个景点描述")
    print("="*70)

if __name__ == '__main__':
    main()
