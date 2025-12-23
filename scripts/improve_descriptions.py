#!/usr/bin/env python3
"""
改进景点描述 - 从地址、电话等信息生成更好的描述
"""

import json
from pathlib import Path
from typing import Dict, Any

# 景点类型关键词及对应的描述模板
CATEGORY_TEMPLATES = {
    'museum': {
        'keywords': ['博物馆', '美术馆', '纪念馆'],
        'intro': '这是一座{city}的{name}，{description}',
    },
    'history': {
        'keywords': ['古城', '古迹', '遗址', '宫', '庙', '塔', '桥', '陵'],
        'intro': '这是一个历史悠久的景点{name}，{description}',
    },
    'outdoor': {
        'keywords': ['公园', '山', '湖', '江', '海', '森林', '瀑布', '峡谷'],
        'intro': '这是{city}的一个自然景点{name}，{description}',
    },
    'sightseeing': {
        'keywords': ['街', '广场', '建筑', '景区'],
        'intro': '这是{city}的热门景点{name}，{description}',
    },
}

def improve_description(spot: Dict[str, Any], city: str) -> Dict[str, Any]:
    """
    改进景点描述
    
    Args:
        spot: 景点字典
        city: 城市名称
    
    Returns:
        改进后的景点字典
    """
    name = spot.get('name', '')
    old_desc = spot.get('description', '')
    category = spot.get('category', 'sightseeing')
    
    # 构建改进的描述
    desc_parts = []
    
    # 第一部分：简短介绍
    category_intro = CATEGORY_TEMPLATES.get(category, {}).get('intro', '')
    if category_intro:
        intro = category_intro.format(name=name, city=city, description='是一个著名景点')
        desc_parts.append(intro)
    else:
        desc_parts.append(f"{name}是{city}的一个景点。")
    
    # 第二部分：提取原始描述中有用的信息
    useful_info = []
    
    # 提取电话
    if '电话:' in old_desc:
        try:
            phone_part = old_desc.split('电话:')[1].split('|')[0].strip()
            if phone_part and phone_part != '无':
                useful_info.append(f"联系电话：{phone_part}")
        except:
            pass
    
    # 提取地址
    if '地址:' in old_desc:
        try:
            addr_part = old_desc.split('地址:')[1].split('|')[0].strip()
            if addr_part and len(addr_part) > 2:
                # 只取前 50 个字符以避免过长
                addr = addr_part[:50]
                useful_info.append(f"位于：{addr}")
        except:
            pass
    
    # 提取类型信息
    if '类别:' in old_desc:
        try:
            type_part = old_desc.split('类别:')[1].strip()
            if type_part and type_part != '无':
                # 提取第一个分类
                type_info = type_part.split(';')[0].split('|')[0].strip()
                if type_info and len(type_info) < 30:
                    useful_info.append(f"景点类型：{type_info}")
        except:
            pass
    
    # 组合有用信息
    if useful_info:
        desc_parts.extend(useful_info)
    
    # 添加建议访问时间
    duration = spot.get('duration_minutes', 120)
    if duration:
        hours = duration // 60
        minutes = duration % 60
        if hours > 0:
            if minutes > 0:
                desc_parts.append(f"建议游览时间：{hours}小时{minutes}分钟")
            else:
                desc_parts.append(f"建议游览时间：{hours}小时")
        else:
            desc_parts.append(f"建议游览时间：{minutes}分钟")
    
    # 最终描述：用换行符分隔
    final_description = " | ".join(desc_parts)
    
    # 更新景点描述
    spot['description'] = final_description
    
    return spot

def improve_city_descriptions(city: str, dry_run: bool = False) -> int:
    """
    改进城市的所有景点描述
    
    Args:
        city: 城市代码（如 'beijing'）
        dry_run: 是否仅预览不保存
    
    Returns:
        改进的景点数量
    """
    input_path = Path(f'data/spots_{city}.json')
    
    if not input_path.exists():
        print(f"❌ 文件不存在: {input_path}")
        return 0
    
    # 获取城市的中文名称（从文件内容推测）
    city_cn_map = {
        'beijing': '北京',
        'shanghai': '上海',
        'shenzhen': '深圳',
        'guangzhou': '广州',
        'chengdu': '成都',
        'hangzhou': '杭州',
        'suzhou': '苏州',
        'nanjing': '南京',
        'qingdao': '青岛',
        'xiamen': '厦门',
        'wuhan': '武汉',
        'xian': '西安',
        'kunming': '昆明',
        'fuzhou': '福州',
        'changchun': '长春',
        'harbin': '哈尔滨',
        'shenyang': '沈阳',
        'taiyuan': '太原',
        'lanzhou': '兰州',
        'xining': '西宁',
        'urumqi': '乌鲁木齐',
        'guiyang': '贵阳',
        'nanning': '南宁',
        'jinan': '济南',
        'zhengzhou': '郑州',
        'hefei': '合肥',
    }
    
    city_cn = city_cn_map.get(city, city.title())
    
    print(f"正在改进 {city_cn} 的景点描述...")
    
    # 读取数据
    with open(input_path, 'r', encoding='utf-8') as f:
        spots = json.load(f)
    
    print(f"  共有 {len(spots)} 个景点")
    
    # 改进每个景点的描述
    improved_count = 0
    for i, spot in enumerate(spots):
        try:
            improve_description(spot, city_cn)
            improved_count += 1
        except Exception as e:
            print(f"  ⚠️ 景点 {spot.get('name', 'Unknown')} 处理失败: {e}")
    
    # 保存
    if not dry_run:
        with open(input_path, 'w', encoding='utf-8') as f:
            json.dump(spots, f, ensure_ascii=False, indent=2)
        print(f"✅ 已保存改进后的数据到 {input_path}")
    else:
        print(f"🔍 预览模式：未保存更改")
    
    return improved_count

def main():
    """主函数"""
    print("=" * 70)
    print("📝 改进景点描述")
    print("=" * 70)
    
    # 获取所有景点文件
    data_dir = Path('data')
    spot_files = sorted(data_dir.glob('spots_*.json'))
    
    if not spot_files:
        print("❌ 未找到景点数据文件")
        return
    
    cities = [f.stem.replace('spots_', '') for f in spot_files]
    
    print(f"\n找到 {len(cities)} 个城市的景点数据")
    print("选择处理方式:")
    print("1. 改进所有城市")
    print("2. 仅改进主要城市")
    print("3. 输入城市代码（逗号分隔）")
    
    choice = input("请选择 (1/2/3): ").strip()
    
    cities_to_process = []
    
    if choice == '1':
        cities_to_process = cities
    elif choice == '2':
        cities_to_process = [
            'beijing', 'shanghai', 'shenzhen', 'guangzhou', 'chengdu',
            'hangzhou', 'suzhou', 'nanjing', 'qingdao', 'xiamen',
            'wuhan', 'xian', 'kunming'
        ]
    elif choice == '3':
        cities_input = input("输入城市代码: ").strip()
        cities_to_process = [c.strip() for c in cities_input.split(',')]
    else:
        print("❌ 无效选择")
        return
    
    # 处理
    total_improved = 0
    for city in cities_to_process:
        if city in cities:
            count = improve_city_descriptions(city)
            total_improved += count
        else:
            print(f"⚠️ 城市 {city} 未找到")
    
    print("\n" + "=" * 70)
    print(f"✅ 完成！共改进 {total_improved} 个景点描述")
    print("=" * 70)

if __name__ == '__main__':
    main()
