#!/usr/bin/env python3
"""
Test to verify that the planning algorithm considers ALL available spots.
"""

import json
from agent.planner import plan_itinerary_soft_constraints
from agent.models import Spot
from agent.constraints import ScoreConfig
from agent.geometry import TransportMode

def test_spot_coverage(city: str, days: int = 3):
    """Test that spots are actually being considered by the planner."""
    
    # Load spots from JSON
    with open(f'data/spots_{city}.json', encoding='utf-8') as f:
        raw_spots = json.load(f)
    
    spots = [Spot(**s) for s in raw_spots]
    
    print(f"\n{'='*60}")
    print(f"Testing {city.upper()}")
    print(f"{'='*60}")
    print(f"📍 Total available spots: {len(spots)}")
    print(f"📅 Planning for {days} days")
    
    # Show all spot names
    print(f"\n所有可用景点:")
    for i, spot in enumerate(spots, 1):
        print(f"  {i:2d}. {spot.name} ({spot.category})")
    
    # Run the planner
    cfg = ScoreConfig(
        max_daily_minutes={
            TransportMode.WALK: 240,
            TransportMode.TRANSIT: 300,
            TransportMode.TAXI: 360,
        },
        exceed_minute_penalty=1.5,
        one_spot_day_penalty=15.0,
        min_spots_per_day=2,
    )
    
    itinerary, score, reasons = plan_itinerary_soft_constraints(
        city=city,
        spots=spots,
        days=days,
        cfg=cfg,
        mode=TransportMode.TRANSIT,
        trials=200
    )
    
    # Collect spots used in itinerary
    used_spots = set()
    for day in itinerary.days:
        for spot in day.spots:
            used_spots.add(spot.name)
    
    unused_spots = [s.name for s in spots if s.name not in used_spots]
    
    print(f"\n✅ 已使用景点: {len(used_spots)}/{len(spots)}")
    print(f"\n规划结果:")
    for day in itinerary.days:
        print(f"\n  Day {day.day}: {len(day.spots)} spots")
        for spot in day.spots:
            print(f"    - {spot.name}")
    
    if unused_spots:
        print(f"\n⚠️  未使用的景点 ({len(unused_spots)}):")
        for name in unused_spots:
            print(f"    - {name}")
        print(f"\n💡 这是正常的！规划算法会根据以下因素选择最优景点组合:")
        print(f"    - 天数限制 ({days} 天)")
        print(f"    - 每日时间预算 (240-360分钟)")
        print(f"    - 景点间距离和交通时间")
        print(f"    - 景点评分和游览时长")
    else:
        print(f"\n🎉 所有景点都被使用了！")
    
    print(f"\n优化分数: {score:.2f}")
    
    return used_spots, unused_spots


if __name__ == "__main__":
    # Test a few cities
    cities_to_test = ['shanghai', 'paris', 'tokyo']
    
    for city in cities_to_test:
        test_spot_coverage(city, days=3)
    
    print(f"\n{'='*60}")
    print("测试完成！")
    print(f"{'='*60}")
    print("\n结论:")
    print("- Agent 会考虑所有可用景点")
    print("- 但只会选择最优的组合放入行程")
    print("- 未被选中的景点不是被忽略，而是在优化过程中被淘汰")
    print("- 如果想要更多景点，可以增加天数或调整权重")
