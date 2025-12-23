#!/usr/bin/env python3
"""
批量为中国主要城市的景点补充周围美食和商铺数据
不需要交互式选择，直接处理指定城市
"""

import sys
sys.path.insert(0, '/workspaces/ai-agent')

from scripts.enrich_spots_nearby import enrich_spots_with_nearby_data
import time

def main():
    """为主要中国城市补充周围数据"""
    
    # 主要城市列表（按重要程度排序）
    main_cities = [
        'beijing',      # 北京
        'shanghai',     # 上海
        'shenzhen',     # 深圳
        'guangzhou',    # 广州
        'chengdu',      # 成都
        'hangzhou',     # 杭州
        'suzhou',       # 苏州
        'nanjing',      # 南京
        'qingdao',      # 青岛
        'xiamen',       # 厦门
        'wuhan',        # 武汉
        'xian',         # 西安
        'kunming',      # 昆明
    ]
    
    print("=" * 70)
    print("🍜 为中国主要城市景点补充周围美食和商铺数据")
    print("=" * 70)
    print(f"\n将处理 {len(main_cities)} 个城市...")
    
    total = len(main_cities)
    successful = 0
    failed = []
    
    for idx, city in enumerate(main_cities, 1):
        print(f"\n[{idx}/{total}] 处理 {city}...")
        try:
            enrich_spots_with_nearby_data(city)
            successful += 1
        except KeyboardInterrupt:
            print("\n\n⚠️ 用户中断")
            break
        except Exception as e:
            print(f"❌ {city} 处理失败: {e}")
            failed.append(city)
        
        # 城市间隔，避免过度限流
        if idx < total:
            time.sleep(2)
    
    print("\n" + "=" * 70)
    print(f"📊 处理完成！")
    print(f"  ✅ 成功: {successful}/{total}")
    if failed:
        print(f"  ❌ 失败: {', '.join(failed)}")
    print("=" * 70)

if __name__ == '__main__':
    main()
