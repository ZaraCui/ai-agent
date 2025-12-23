#!/usr/bin/env python3
"""
快速测试：为北京的前 3 个景点补充周围数据
"""

import sys
sys.path.insert(0, '/workspaces/ai-agent')

from scripts.enrich_spots_nearby import fetch_nearby_foods, fetch_nearby_shops
import json

def test_enrich():
    """测试美食和商铺获取"""
    print("=" * 70)
    print("🧪 测试：为北京景点补充周围美食和商铺")
    print("=" * 70)
    
    # 读取北京数据
    with open('data/spots_beijing.json', 'r', encoding='utf-8') as f:
        spots = json.load(f)
    
    # 仅处理前 3 个景点用于测试
    test_spots = spots[:3]
    
    print(f"\n正在为 {len(test_spots)} 个景点获取周围数据...\n")
    
    for i, spot in enumerate(test_spots, 1):
        name = spot.get('name', 'Unknown')
        lat = spot.get('lat', 0)
        lon = spot.get('lon', 0)
        
        print(f"{i}. {name}")
        print(f"   坐标: ({lat}, {lon})")
        
        # 获取周围美食
        print(f"   🍜 获取周围美食...", end=' ', flush=True)
        foods = fetch_nearby_foods(lat, lon, limit=3)
        if foods:
            print(f"找到 {len(foods)} 个美食")
            for food in foods:
                print(f"      • {food['name']} ({food['distance']:.0f}m)")
        else:
            print("无数据")
        
        # 获取周围商铺
        print(f"   🛒 获取周围商铺...", end=' ', flush=True)
        shops = fetch_nearby_shops(lat, lon, limit=3)
        if shops:
            print(f"找到 {len(shops)} 个商铺")
            for shop in shops:
                print(f"      • {shop['name']} ({shop['distance']:.0f}m)")
        else:
            print("无数据")
        
        print()
    
    print("=" * 70)
    print("✅ 测试完成！")
    print("\n如果上面显示了美食和商铺数据，说明集成成功！")
    print("\n运行完整脚本：python scripts/enrich_spots_nearby.py")
    print("=" * 70)

if __name__ == '__main__':
    test_enrich()
