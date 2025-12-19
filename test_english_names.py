#!/usr/bin/env python3
"""
测试英文名称功能
"""
import json
from pathlib import Path

def test_english_names():
    """测试所有景点文件都包含英文名称"""
    data_dir = Path(__file__).parent / "data"
    
    print("测试景点英文名称...")
    print("=" * 60)
    
    all_passed = True
    total_spots = 0
    total_files = 0
    
    for filepath in sorted(data_dir.glob("spots_*.json")):
        city = filepath.stem.replace("spots_", "")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            spots = json.load(f)
        
        total_files += 1
        total_spots += len(spots)
        
        # 检查每个景点是否有 name_en 字段
        missing_en = []
        for i, spot in enumerate(spots):
            if 'name_en' not in spot or not spot['name_en']:
                missing_en.append(i)
        
        if missing_en:
            print(f"❌ {city}: 缺少 name_en 的景点索引: {missing_en[:5]}...")
            all_passed = False
        else:
            print(f"✅ {city}: {len(spots)} 个景点都有英文名称")
    
    print("=" * 60)
    print(f"总计: {total_files} 个文件, {total_spots} 个景点")
    
    if all_passed:
        print("✅ 所有测试通过！")
        return True
    else:
        print("❌ 有些景点缺少英文名称")
        return False

def test_bilingual_display():
    """测试中英文名称不同时的显示逻辑"""
    print("\n测试双语显示逻辑...")
    print("=" * 60)
    
    # 模拟景点数据
    test_cases = [
        {"name": "故宫", "name_en": "Forbidden City", "expected": "应该显示两个名称"},
        {"name": "The Bund", "name_en": "The Bund", "expected": "名称相同，只显示一次"},
        {"name": "东莞博物馆", "name_en": "Dongguang Museum", "expected": "应该显示两个名称"},
    ]
    
    for i, case in enumerate(test_cases, 1):
        name = case['name']
        name_en = case['name_en']
        expected = case['expected']
        
        # 模拟前端逻辑
        should_show_en = name_en and name_en != name
        
        print(f"{i}. {name}")
        print(f"   英文名: {name_en}")
        print(f"   显示逻辑: {expected}")
        print(f"   实际: {'显示英文名' if should_show_en else '不显示英文名'}")
        print()
    
    print("✅ 双语显示逻辑测试完成")

if __name__ == "__main__":
    success = test_english_names()
    test_bilingual_display()
    
    if success:
        print("\n🎉 所有功能正常！外国用户可以使用本应用了！")
    else:
        print("\n⚠️ 请修复上述问题")
        exit(1)
