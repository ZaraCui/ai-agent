#!/usr/bin/env python3
"""
高德地图 POI 搜索 - 获取景点周围美食和商铺
使用高德地图 周边搜索 API 获取景点附近的餐厅、咖啡厅等
"""

import requests
import json
import time
import os
from pathlib import Path
from typing import List, Dict, Optional
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 从环境变量获取 API Key
GAODE_API_KEY = os.getenv('GAODE_API_KEY')
if not GAODE_API_KEY:
    print("❌ 错误: GAODE_API_KEY 环境变量未设置")
    exit(1)

# 高德地图 API 端点
NEARBY_API_URL = "https://restapi.amap.com/v3/place/around"

# 搜索类型配置
SEARCH_TYPES = {
    'foods': {
        'keywords': ['餐厅', '咖啡厅', '奶茶店', '面包房', '日本料理', '烤肉', '火锅'],
        'types': '050201|050202|050203',  # 高德地图的食物分类代码
    },
    'shops': {
        'keywords': ['超市', '购物', '商场', '便利店'],
        'types': '050301|050302|050303',  # 商店分类代码
    }
}

def fetch_nearby_pois(lat: float, lon: float, keywords: str, radius: int = 1000, page_size: int = 20) -> Optional[List[Dict]]:
    """
    使用高德地图周边搜索 API 获取周围 POI
    
    Args:
        lat: 纬度
        lon: 经度
        keywords: 搜索关键词
        radius: 搜索半径（米，默认1000米）
        page_size: 每页数量（最多20）
    
    Returns:
        POI 列表或 None
    """
    params = {
        'key': GAODE_API_KEY,
        'location': f"{lon},{lat}",  # 注意：高德地图格式是 lon,lat
        'keywords': keywords,
        'radius': radius,
        'pagesize': page_size,
        'output': 'json',
        'extensions': 'all'  # 获取详细信息
    }
    
    try:
        response = requests.get(NEARBY_API_URL, params=params, timeout=10)
        response.encoding = 'utf-8'
        data = response.json()
        
        if data.get('status') == '1':
            return data.get('pois', [])
        else:
            return None
    except Exception as e:
        print(f"    ❌ 获取周边 POI 失败: {e}")
        return None

def convert_poi_to_food_dict(poi: Dict) -> Dict:
    """将高德 POI 转换为美食信息格式"""
    # 计算距离（如果有坐标）
    distance = 0.0
    try:
        distance = float(poi.get('distance', 0))
    except:
        pass
    
    return {
        'name': poi.get('name', ''),
        'category': poi.get('type', ''),
        'distance': distance,
        'phone': poi.get('tel', ''),
        'address': poi.get('address', ''),
        'rating': poi.get('rating'),  # 如果有的话
    }

def convert_poi_to_shop_dict(poi: Dict) -> Dict:
    """将高德 POI 转换为商铺信息格式"""
    distance = 0.0
    try:
        distance = float(poi.get('distance', 0))
    except:
        pass
    
    return {
        'name': poi.get('name', ''),
        'category': poi.get('type', ''),
        'distance': distance,
        'phone': poi.get('tel', ''),
        'address': poi.get('address', ''),
    }

def fetch_nearby_foods(lat: float, lon: float, limit: int = 10) -> List[Dict]:
    """
    获取景点周围的美食
    
    Args:
        lat: 纬度
        lon: 经度
        limit: 返回数量限制
    
    Returns:
        美食列表
    """
    all_foods = []
    
    # 尝试多个搜索词
    for keyword in SEARCH_TYPES['foods']['keywords']:
        if len(all_foods) >= limit:
            break
        
        pois = fetch_nearby_pois(lat, lon, keyword, radius=1500, page_size=20)
        
        if pois:
            for poi in pois:
                if len(all_foods) >= limit:
                    break
                food = convert_poi_to_food_dict(poi)
                # 避免重复
                if not any(f['name'] == food['name'] for f in all_foods):
                    all_foods.append(food)
        
        time.sleep(0.2)  # 避免限流
    
    # 按距离排序
    all_foods.sort(key=lambda x: x['distance'])
    return all_foods[:limit]

def fetch_nearby_shops(lat: float, lon: float, limit: int = 10) -> List[Dict]:
    """
    获取景点周围的商铺
    
    Args:
        lat: 纬度
        lon: 经度
        limit: 返回数量限制
    
    Returns:
        商铺列表
    """
    all_shops = []
    
    # 尝试多个搜索词
    for keyword in SEARCH_TYPES['shops']['keywords']:
        if len(all_shops) >= limit:
            break
        
        pois = fetch_nearby_pois(lat, lon, keyword, radius=1500, page_size=20)
        
        if pois:
            for poi in pois:
                if len(all_shops) >= limit:
                    break
                shop = convert_poi_to_shop_dict(poi)
                # 避免重复
                if not any(s['name'] == shop['name'] for s in all_shops):
                    all_shops.append(shop)
        
        time.sleep(0.2)
    
    # 按距离排序
    all_shops.sort(key=lambda x: x['distance'])
    return all_shops[:limit]

def enrich_spots_with_nearby_data(city: str, output_file: Optional[str] = None):
    """
    为景点数据补充周围美食和商铺信息
    
    Args:
        city: 城市名称（如 'beijing'）
        output_file: 输出文件路径（默认覆盖原文件）
    """
    input_path = Path(f'data/spots_{city}.json')
    
    if not input_path.exists():
        print(f"❌ 文件不存在: {input_path}")
        return
    
    print(f"\n正在为 {city} 的景点补充周围数据...")
    
    # 读取景点数据
    with open(input_path, 'r', encoding='utf-8') as f:
        spots = json.load(f)
    
    print(f"📍 共有 {len(spots)} 个景点，开始获取周围数据...")
    
    # 为每个景点添加周围数据
    for i, spot in enumerate(spots, 1):
        if i % 10 == 0:
            print(f"  [{i}/{len(spots)}] 处理中...", flush=True)
        
        lat = spot.get('lat', 0)
        lon = spot.get('lon', 0)
        
        # 跳过坐标无效的景点
        if lat == 0 or lon == 0:
            continue
        
        # 获取周围美食
        try:
            foods = fetch_nearby_foods(lat, lon, limit=5)
            spot['nearby_foods'] = foods
        except Exception as e:
            print(f"    ⚠️ {spot.get('name', 'Unknown')} 获取美食失败: {e}")
            spot['nearby_foods'] = []
        
        # 获取周围商铺
        try:
            shops = fetch_nearby_shops(lat, lon, limit=5)
            spot['nearby_shops'] = shops
        except Exception as e:
            print(f"    ⚠️ {spot.get('name', 'Unknown')} 获取商铺失败: {e}")
            spot['nearby_shops'] = []
        
        # 避免 API 限流
        time.sleep(0.3)
    
    # 保存增强后的数据
    output_path = output_file or input_path
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(spots, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 数据已保存到 {output_path}")

def main():
    """主函数"""
    print("=" * 70)
    print("🍜 高德地图 POI 搜索 - 景点周围美食和商铺补充")
    print("=" * 70)
    
    # 获取所有景点文件
    data_dir = Path('data')
    spot_files = sorted(data_dir.glob('spots_*.json'))
    
    if not spot_files:
        print("❌ 未找到景点数据文件")
        return
    
    print(f"\n找到 {len(spot_files)} 个城市的景点数据")
    
    # 选择性处理城市
    print("\n请选择要处理的城市:")
    print("1. 所有城市")
    print("2. 仅中国主要城市（北京、上海、深圳等）")
    print("3. 输入城市代码（用逗号分隔，如: beijing,shanghai,shenzhen）")
    
    choice = input("请选择 (1/2/3): ").strip()
    
    cities_to_process = []
    
    if choice == '1':
        cities_to_process = [f.stem.replace('spots_', '') for f in spot_files]
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
    
    # 处理选定的城市
    total = len(cities_to_process)
    for idx, city in enumerate(cities_to_process, 1):
        print(f"\n[{idx}/{total}] 处理 {city}")
        try:
            enrich_spots_with_nearby_data(city)
        except KeyboardInterrupt:
            print("\n\n⚠️ 用户中断，程序退出")
            break
        except Exception as e:
            print(f"❌ {city} 处理失败: {e}")
    
    print("\n" + "=" * 70)
    print("✨ 处理完成！")
    print("=" * 70)

if __name__ == '__main__':
    main()
