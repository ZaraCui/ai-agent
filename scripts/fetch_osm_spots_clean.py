"""
改进版的 OSM 景点数据获取脚本
- 输出更简洁清晰
- 提供摘要信息而不是打印所有景点
- 自动保存到文件
"""

import requests
import json
import sys
import os
import time

def get_city_area_id(city_name):
    """使用 Nominatim 查找城市的区域 ID"""
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": city_name,
        "format": "json",
        "polygon_geojson": 0,
        "limit": 1
    }
    headers = {'User-Agent': 'TravelPlannerAgent/1.0'}
    
    try:
        response = requests.get(url, params=params, headers=headers)
        data = response.json()
        if not data:
            return None
        
        # OSM ID for area is relation ID + 3600000000
        osm_id = int(data[0]['osm_id'])
        osm_type = data[0]['osm_type']
        
        if osm_type == 'relation':
            return osm_id + 3600000000
        elif osm_type == 'way':
            return osm_id + 2400000000
        return None
    except Exception as e:
        print(f"❌ 获取城市信息失败: {e}")
        return None

def fetch_spots(city_name, verbose=False):
    """
    从 OpenStreetMap 获取城市景点数据
    
    Args:
        city_name: 城市名称
        verbose: 是否显示详细信息
    
    Returns:
        list: 景点列表
    """
    print(f"\n{'='*60}")
    print(f"正在获取 {city_name} 的景点数据...")
    print(f"{'='*60}")
    
    # 第一步：获取城市区域 ID
    print(f"\n[1/3] 查找城市地理信息...")
    area_id = get_city_area_id(city_name)
    if not area_id:
        print(f"❌ 无法找到城市: {city_name}")
        print("提示: 请检查城市名称是否正确（建议使用英文名）")
        return []
    print(f"✓ 找到城市区域 ID: {area_id}")

    # 第二步：查询景点数据
    print(f"\n[2/3] 从 OpenStreetMap 获取景点数据...")
    overpass_url = "http://overpass-api.de/api/interpreter"
    overpass_query = f"""
    [out:json][timeout:25];
    area({area_id})->.searchArea;
    (
      node["tourism"~"attraction|museum|viewpoint|zoo|theme_park|gallery"](area.searchArea);
      way["tourism"~"attraction|museum|viewpoint|zoo|theme_park|gallery"](area.searchArea);
      relation["tourism"~"attraction|museum|viewpoint|zoo|theme_park|gallery"](area.searchArea);
      node["historic"~"monument|memorial|castle|ruins"](area.searchArea);
    );
    out center;
    """
    
    try:
        response = requests.get(overpass_url, params={'data': overpass_query})
        data = response.json()
        print(f"✓ API 请求成功")
    except Exception as e:
        print(f"❌ Overpass API 查询失败: {e}")
        return []
    
    # 第三步：处理数据
    print(f"\n[3/3] 处理景点数据...")
    spots = []
    seen_names = set()
    categories_count = {}
    
    for element in data.get('elements', []):
        tags = element.get('tags', {})
        name = tags.get('name')
        
        if not name:
            name = tags.get('name:en')
        
        if not name or name in seen_names:
            continue
            
        seen_names.add(name)
        
        lat = element.get('lat') or element.get('center', {}).get('lat')
        lon = element.get('lon') or element.get('center', {}).get('lon')
        
        if lat is None or lon is None:
            continue
            
        # 推断分类
        category = 'sightseeing'
        tourism = tags.get('tourism')
        historic = tags.get('historic')
        
        if tourism == 'museum' or tags.get('museum'):
            category = 'museum'
        elif tourism == 'zoo':
            category = 'outdoor'
        elif tourism == 'theme_park':
            category = 'outdoor'
        elif tourism == 'viewpoint':
            category = 'outdoor'
        elif historic:
            category = 'history'
        
        # 统计分类
        categories_count[category] = categories_count.get(category, 0) + 1
            
        # 创建景点对象
        spot = {
            "name": name,
            "category": category,
            "duration_minutes": 60,
            "rating": 4.0,
            "lat": lat,
            "lon": lon,
            "description": tags.get('description:en') or tags.get('description') or f"A popular {category} spot in {city_name}."
        }
        spots.append(spot)
        
        # 显示进度（可选）
        if verbose and len(spots) % 10 == 0:
            print(f"  已处理 {len(spots)} 个景点...")
    
    # 按名称排序
    spots.sort(key=lambda x: x['name'])
    
    # 显示统计信息
    print(f"\n{'='*60}")
    print(f"✅ 成功获取 {len(spots)} 个景点")
    print(f"{'='*60}")
    
    if categories_count:
        print(f"\n📊 分类统计:")
        for cat, count in sorted(categories_count.items(), key=lambda x: x[1], reverse=True):
            print(f"  • {cat:15s} : {count:3d} 个景点")
    
    # 显示前几个景点作为预览
    if spots and len(spots) <= 10:
        print(f"\n📍 景点列表:")
        for i, spot in enumerate(spots, 1):
            print(f"  {i:2d}. {spot['name']} ({spot['category']})")
    elif spots:
        print(f"\n📍 前 10 个景点预览:")
        for i, spot in enumerate(spots[:10], 1):
            print(f"  {i:2d}. {spot['name']} ({spot['category']})")
        print(f"  ... 还有 {len(spots) - 10} 个景点")
    
    return spots

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("=" * 60)
        print("OSM 景点数据获取工具（简洁版）")
        print("=" * 60)
        print("\n使用方法:")
        print("  python fetch_osm_spots_clean.py <城市名> [--verbose]")
        print("\n示例:")
        print("  python fetch_osm_spots_clean.py Beijing")
        print("  python fetch_osm_spots_clean.py Shanghai --verbose")
        print("  python fetch_osm_spots_clean.py \"New York\"")
        print("\n提示:")
        print("  • 使用英文城市名")
        print("  • 多个单词的城市名用引号括起来")
        print("  • 添加 --verbose 参数显示详细进度")
        print("=" * 60)
        sys.exit(1)
    
    # 解析参数
    city = sys.argv[1]
    verbose = '--verbose' in sys.argv or '-v' in sys.argv
    
    # 获取景点数据
    spots = fetch_spots(city, verbose=verbose)
    
    if spots:
        # 创建 data 目录
        os.makedirs('data', exist_ok=True)
        
        # 保存到文件
        filename = f"data/spots_{city.lower().replace(' ', '')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(spots, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 数据已保存到: {filename}")
        print(f"\n✨ 完成！你现在可以在旅行规划系统中使用 {city} 了。")
    else:
        print(f"\n❌ 未找到景点数据")
        print("可能的原因:")
        print("  • 城市名称拼写错误")
        print("  • OpenStreetMap 中该城市数据不完整")
        print("  • 网络连接问题")

if __name__ == "__main__":
    main()
