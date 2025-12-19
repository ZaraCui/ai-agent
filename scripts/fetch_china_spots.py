"""
获取中国景点数据脚本
支持两种模式：
1. 获取整个中国的景点数据（可能数据量很大）
2. 批量获取中国主要城市的景点数据
"""

import requests
import json
import sys
import os
import time
from datetime import datetime

def get_china_area_id():
    """获取中国的 OSM 区域 ID"""
    # 中国的 OSM relation ID 是 270056
    # area ID = relation ID + 3600000000
    return 3600000000 + 270056

def fetch_china_all_spots(timeout=60):
    """
    获取整个中国的景点数据
    注意：数据量可能非常大，建议使用批量城市模式
    """
    print(f"\n{'='*70}")
    print(f"正在获取整个中国的景点数据...")
    print(f"⚠️  警告: 这可能需要较长时间，且数据量巨大")
    print(f"{'='*70}")
    
    area_id = get_china_area_id()
    
    print(f"\n[1/3] 使用中国区域 ID: {area_id}")
    
    # 第二步：查询景点数据
    print(f"\n[2/3] 从 OpenStreetMap 获取景点数据...")
    print(f"      ⏳ 这可能需要 {timeout} 秒或更长时间...")
    
    overpass_url = "http://overpass-api.de/api/interpreter"
    overpass_query = f"""
    [out:json][timeout:{timeout}];
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
        response = requests.get(overpass_url, params={'data': overpass_query}, timeout=timeout+10)
        data = response.json()
        print(f"✓ API 请求成功")
    except requests.exceptions.Timeout:
        print(f"❌ 请求超时（超过 {timeout} 秒）")
        print("建议：使用批量城市模式代替")
        return []
    except Exception as e:
        print(f"❌ Overpass API 查询失败: {e}")
        return []
    
    # 第三步：处理数据
    print(f"\n[3/3] 处理景点数据...")
    spots = []
    seen_names = set()
    categories_count = {}
    city_count = {}
    
    elements = data.get('elements', [])
    total_elements = len(elements)
    
    print(f"      共收到 {total_elements} 个原始数据点")
    
    for idx, element in enumerate(elements, 1):
        if idx % 500 == 0:
            print(f"      处理进度: {idx}/{total_elements} ({idx*100//total_elements}%)")
            
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
        
        # 获取城市/地区信息（如果有）
        city = tags.get('addr:city') or tags.get('addr:province') or 'unknown'
        city_count[city] = city_count.get(city, 0) + 1
            
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
        
        categories_count[category] = categories_count.get(category, 0) + 1
            
        spot = {
            "name": name,
            "category": category,
            "duration_minutes": 60,
            "rating": 4.0,
            "lat": lat,
            "lon": lon,
            "city": city,
            "description": tags.get('description:en') or tags.get('description') or f"A popular {category} spot in China."
        }
        spots.append(spot)
    
    spots.sort(key=lambda x: x['name'])
    
    # 显示统计信息
    print(f"\n{'='*70}")
    print(f"✅ 成功获取 {len(spots)} 个景点")
    print(f"{'='*70}")
    
    if categories_count:
        print(f"\n📊 分类统计:")
        for cat, count in sorted(categories_count.items(), key=lambda x: x[1], reverse=True):
            print(f"  • {cat:15s} : {count:4d} 个景点")
    
    if city_count:
        print(f"\n🏙️  城市分布 (前20):")
        sorted_cities = sorted(city_count.items(), key=lambda x: x[1], reverse=True)[:20]
        for city, count in sorted_cities:
            print(f"  • {city:20s} : {count:4d} 个景点")
    
    return spots

def fetch_major_cities_batch():
    """批量获取中国主要城市的景点数据"""
    
    major_cities = [
        # 一线城市
        "Beijing", "Shanghai", "Guangzhou", "Shenzhen",
        # 新一线城市
        "Chengdu", "Hangzhou", "Chongqing", "Wuhan", "Xi'an",
        "Suzhou", "Zhengzhou", "Nanjing", "Tianjin", "Changsha",
        "Dongguan", "Ningbo", "Foshan", "Qingdao", "Shenyang",
        # 其他重要城市
        "Kunming", "Xiamen", "Dalian", "Jinan", "Harbin",
        "Fuzhou", "Changchun", "Shijiazhuang", "Hefei", "Nanchang",
        "Guiyang", "Taiyuan", "Nanning", "Urumqi", "Lanzhou"
    ]
    
    print(f"\n{'='*70}")
    print(f"批量获取中国 {len(major_cities)} 个主要城市的景点数据")
    print(f"{'='*70}")
    
    all_spots = []
    failed_cities = []
    city_stats = {}
    
    for idx, city in enumerate(major_cities, 1):
        print(f"\n[{idx}/{len(major_cities)}] 正在处理: {city}")
        print("-" * 70)
        
        try:
            spots = fetch_city_spots(city, show_preview=False)
            if spots:
                city_stats[city] = len(spots)
                # 为每个景点添加城市标记
                for spot in spots:
                    spot['city'] = city
                all_spots.extend(spots)
                print(f"✓ {city}: 获取 {len(spots)} 个景点")
            else:
                failed_cities.append(city)
                print(f"✗ {city}: 未找到景点")
            
            # 避免请求过快
            if idx < len(major_cities):
                time.sleep(1)
                
        except Exception as e:
            failed_cities.append(city)
            print(f"✗ {city}: 失败 - {str(e)}")
    
    # 汇总统计
    print(f"\n{'='*70}")
    print(f"批量获取完成！")
    print(f"{'='*70}")
    print(f"\n✅ 成功: {len(city_stats)} 个城市")
    print(f"❌ 失败: {len(failed_cities)} 个城市")
    print(f"📊 总景点数: {len(all_spots)} 个")
    
    if city_stats:
        print(f"\n🏙️  各城市景点数量 (前20):")
        sorted_stats = sorted(city_stats.items(), key=lambda x: x[1], reverse=True)[:20]
        for city, count in sorted_stats:
            print(f"  • {city:20s} : {count:4d} 个景点")
    
    if failed_cities:
        print(f"\n⚠️  失败的城市: {', '.join(failed_cities)}")
    
    return all_spots

def fetch_city_spots(city_name, show_preview=True):
    """获取单个城市的景点（简化版）"""
    from fetch_osm_spots_clean import get_city_area_id
    
    area_id = get_city_area_id(city_name)
    if not area_id:
        return []
    
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
    except Exception:
        return []
    
    spots = []
    seen_names = set()
    
    for element in data.get('elements', []):
        tags = element.get('tags', {})
        name = tags.get('name') or tags.get('name:en')
        
        if not name or name in seen_names:
            continue
        seen_names.add(name)
        
        lat = element.get('lat') or element.get('center', {}).get('lat')
        lon = element.get('lon') or element.get('center', {}).get('lon')
        
        if lat is None or lon is None:
            continue
        
        category = 'sightseeing'
        tourism = tags.get('tourism')
        historic = tags.get('historic')
        
        if tourism == 'museum' or tags.get('museum'):
            category = 'museum'
        elif tourism in ['zoo', 'theme_park', 'viewpoint']:
            category = 'outdoor'
        elif historic:
            category = 'history'
        
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
    
    spots.sort(key=lambda x: x['name'])
    return spots

def main():
    """主函数"""
    print("=" * 70)
    print("中国景点数据获取工具")
    print("=" * 70)
    
    if len(sys.argv) > 1 and sys.argv[1] == '--all':
        # 模式1：获取整个中国
        print("\n⚠️  模式: 获取整个中国的景点数据")
        print("这可能会获取数万个景点，需要较长时间")
        
        confirm = input("\n确认继续? (y/n): ")
        if confirm.lower() != 'y':
            print("已取消")
            return
        
        spots = fetch_china_all_spots(timeout=90)
        filename_suffix = "china_all"
        
    elif len(sys.argv) > 1 and sys.argv[1] == '--cities':
        # 模式2：批量获取主要城市
        print("\n📍 模式: 批量获取中国主要城市")
        print("将获取约35个主要城市的景点数据")
        
        confirm = input("\n确认继续? (y/n): ")
        if confirm.lower() != 'y':
            print("已取消")
            return
        
        spots = fetch_major_cities_batch()
        filename_suffix = "china_cities"
        
    else:
        # 显示使用说明
        print("\n使用方法:")
        print("  python fetch_china_spots.py --all      # 获取整个中国（数据量大，不推荐）")
        print("  python fetch_china_spots.py --cities   # 获取主要城市（推荐）✅")
        print("\n推荐使用 --cities 模式，更快且数据质量更好！")
        return
    
    if spots:
        # 保存数据
        os.makedirs('data', exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data/spots_{filename_suffix}_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(spots, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 数据已保存到: {filename}")
        print(f"📊 文件大小: {os.path.getsize(filename) / 1024 / 1024:.2f} MB")
        
        # 同时保存一份不带时间戳的版本
        simple_filename = f"data/spots_{filename_suffix}.json"
        with open(simple_filename, 'w', encoding='utf-8') as f:
            json.dump(spots, f, indent=2, ensure_ascii=False)
        print(f"💾 同时保存到: {simple_filename}")
        
        print(f"\n✨ 完成！")
    else:
        print(f"\n❌ 未获取到数据")

if __name__ == "__main__":
    main()
