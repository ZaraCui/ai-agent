#!/usr/bin/env python3
"""
全面的景点数据质量检查脚本
检查问题：
1. 重复景点（基于名称相似度和坐标距离）
2. 坐标重复
3. 描述相似度
4. 缺失字段
5. 无效数据
"""
import json
from pathlib import Path
from collections import defaultdict
import math
from difflib import SequenceMatcher

def calculate_distance(lat1, lon1, lat2, lon2):
    """计算两个坐标点之间的距离（米）"""
    R = 6371000  # 地球半径（米）
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    
    a = math.sin(delta_phi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c

def name_similarity(name1, name2):
    """计算两个名称的相似度（0-1）"""
    # 移除常见的前缀/后缀
    clean1 = name1.replace('北京', '').replace('故宫博物院-', '').replace('天坛公园-', '').strip()
    clean2 = name2.replace('北京', '').replace('故宫博物院-', '').replace('天坛公园-', '').strip()
    
    # 使用SequenceMatcher计算相似度
    return SequenceMatcher(None, clean1, clean2).ratio()

def check_duplicate_spots(spots, city_name, threshold_name=0.8, threshold_distance=100):
    """
    检查重复景点
    threshold_name: 名称相似度阈值（0-1）
    threshold_distance: 距离阈值（米）
    """
    duplicates = []
    
    for i in range(len(spots)):
        for j in range(i + 1, len(spots)):
            spot1 = spots[i]
            spot2 = spots[j]
            
            name1 = spot1.get('name', '')
            name2 = spot2.get('name', '')
            
            # 检查名称相似度
            similarity = name_similarity(name1, name2)
            
            # 检查坐标距离
            lat1, lon1 = spot1.get('lat'), spot1.get('lon')
            lat2, lon2 = spot2.get('lat'), spot2.get('lon')
            
            distance = None
            if all([lat1, lon1, lat2, lon2]):
                distance = calculate_distance(lat1, lon1, lat2, lon2)
            
            # 判断是否重复
            is_duplicate = False
            reason = []
            
            if similarity >= threshold_name:
                is_duplicate = True
                reason.append(f"名称相似度 {similarity:.2%}")
            
            if distance is not None and distance <= threshold_distance:
                is_duplicate = True
                reason.append(f"距离 {distance:.0f}米")
            
            if is_duplicate:
                duplicates.append({
                    'spot1': name1,
                    'spot2': name2,
                    'similarity': similarity,
                    'distance': distance,
                    'reason': ', '.join(reason),
                    'index1': i,
                    'index2': j
                })
    
    return duplicates

def check_description_quality(spots, city_name):
    """检查描述质量"""
    issues = []
    
    for i, spot in enumerate(spots):
        name = spot.get('name', '')
        desc = spot.get('description', '')
        
        # 检查空描述
        if not desc or len(desc.strip()) == 0:
            issues.append({
                'type': '空描述',
                'spot': name,
                'index': i
            })
            continue
        
        # 检查过短描述
        if len(desc) < 50:
            issues.append({
                'type': '描述过短',
                'spot': name,
                'index': i,
                'length': len(desc)
            })
        
        # 检查重复的描述开头（可能是模板）
        if desc.startswith('在北京') and desc.count('在北京') > 1:
            issues.append({
                'type': '描述可能有重复文本',
                'spot': name,
                'index': i
            })
    
    return issues

def check_missing_info(spots, city_name):
    """检查缺失的重要信息"""
    issues = []
    
    for i, spot in enumerate(spots):
        name = spot.get('name', '')
        
        # 检查必填字段
        required_fields = ['name', 'category', 'duration_minutes', 'rating', 'lat', 'lon', 'description', 'city']
        missing = [f for f in required_fields if f not in spot or spot[f] is None]
        
        if missing:
            issues.append({
                'spot': name,
                'missing_fields': missing,
                'index': i
            })
    
    return issues

def check_data_anomalies(spots, city_name):
    """检查数据异常（如异常评分、时长等）"""
    issues = []
    
    for i, spot in enumerate(spots):
        name = spot.get('name', '')
        
        # 检查评分
        rating = spot.get('rating')
        if rating is not None:
            if not (1 <= rating <= 5):
                issues.append({
                    'type': '评分越界',
                    'spot': name,
                    'value': rating,
                    'index': i
                })
            elif rating == 4.0:  # 检查是否所有评分都是4.0（可能是默认值）
                pass  # 我们会在另一个检查中统计
        
        # 检查持续时间
        duration = spot.get('duration_minutes')
        if duration is not None:
            if duration <= 0:
                issues.append({
                    'type': '持续时间无效',
                    'spot': name,
                    'value': duration,
                    'index': i
                })
            elif duration > 480:  # 超过8小时
                issues.append({
                    'type': '持续时间异常长',
                    'spot': name,
                    'value': duration,
                    'index': i
                })
        
        # 检查类别
        valid_categories = ['sightseeing', 'museum', 'outdoor', 'history', 'food', 'shopping', 'entertainment']
        category = spot.get('category')
        if category and category not in valid_categories:
            issues.append({
                'type': '未知类别',
                'spot': name,
                'value': category,
                'index': i
            })
    
    return issues

def analyze_data_quality():
    """分析所有城市的数据质量"""
    data_dir = Path('data')
    
    print("=" * 80)
    print("🔍 景点数据质量检查报告")
    print("=" * 80)
    
    all_issues = defaultdict(list)
    total_spots = 0
    total_cities = 0
    
    for json_file in sorted(data_dir.glob('spots_*.json')):
        city = json_file.stem.replace('spots_', '')
        total_cities += 1
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                spots = json.load(f)
        except json.JSONDecodeError as e:
            print(f"\n❌ {city}: JSON 解析错误 - {e}")
            continue
        
        total_spots += len(spots)
        
        print(f"\n{'='*80}")
        print(f"📍 城市: {city} ({len(spots)} 个景点)")
        print(f"{'='*80}")
        
        # 1. 检查重复景点
        print(f"\n🔎 检查重复景点...")
        duplicates = check_duplicate_spots(spots, city)
        if duplicates:
            print(f"  ❌ 发现 {len(duplicates)} 组疑似重复景点:")
            for dup in duplicates[:10]:  # 只显示前10个
                print(f"    • {dup['spot1']} ⟷ {dup['spot2']}")
                print(f"      原因: {dup['reason']}")
            if len(duplicates) > 10:
                print(f"    ... 还有 {len(duplicates) - 10} 组重复")
            all_issues[f'{city}_duplicates'].extend(duplicates)
        else:
            print(f"  ✅ 未发现重复景点")
        
        # 2. 检查缺失信息
        print(f"\n📝 检查缺失字段...")
        missing = check_missing_info(spots, city)
        if missing:
            print(f"  ❌ 发现 {len(missing)} 个景点缺少字段:")
            for issue in missing[:5]:
                print(f"    • {issue['spot']}: 缺少 {', '.join(issue['missing_fields'])}")
            if len(missing) > 5:
                print(f"    ... 还有 {len(missing) - 5} 个")
            all_issues[f'{city}_missing'].extend(missing)
        else:
            print(f"  ✅ 所有景点字段完整")
        
        # 3. 检查描述质量
        print(f"\n📖 检查描述质量...")
        desc_issues = check_description_quality(spots, city)
        if desc_issues:
            print(f"  ⚠️ 发现 {len(desc_issues)} 个描述质量问题:")
            type_counts = defaultdict(int)
            for issue in desc_issues:
                type_counts[issue['type']] += 1
            for issue_type, count in type_counts.items():
                print(f"    • {issue_type}: {count} 个")
            all_issues[f'{city}_descriptions'].extend(desc_issues)
        else:
            print(f"  ✅ 描述质量良好")
        
        # 4. 检查数据异常
        print(f"\n⚡ 检查数据异常...")
        anomalies = check_data_anomalies(spots, city)
        if anomalies:
            print(f"  ⚠️ 发现 {len(anomalies)} 个数据异常:")
            type_counts = defaultdict(int)
            for issue in anomalies:
                type_counts[issue['type']] += 1
            for issue_type, count in type_counts.items():
                print(f"    • {issue_type}: {count} 个")
            all_issues[f'{city}_anomalies'].extend(anomalies)
        else:
            print(f"  ✅ 数据格式正常")
        
        # 5. 统计评分分布（检查是否所有评分都一样）
        ratings = [s.get('rating') for s in spots if s.get('rating') is not None]
        if ratings:
            unique_ratings = set(ratings)
            if len(unique_ratings) == 1:
                print(f"  ⚠️ 所有景点评分都是 {ratings[0]}（可能需要更新）")
            else:
                print(f"  ℹ️ 评分分布: {dict(sorted([(r, ratings.count(r)) for r in unique_ratings]))}")
    
    # 总结报告
    print(f"\n{'='*80}")
    print(f"📊 总体统计")
    print(f"{'='*80}")
    print(f"  总城市数: {total_cities}")
    print(f"  总景点数: {total_spots}")
    print(f"  平均每城市: {total_spots / total_cities:.1f} 个景点")
    
    # 计算总问题数
    total_issues = sum(len(issues) for issues in all_issues.values())
    print(f"  发现问题总数: {total_issues}")
    
    # 建议
    print(f"\n{'='*80}")
    print(f"💡 数据质量改进建议")
    print(f"{'='*80}")
    print(f"  1. 处理重复景点：检查上述重复景点，决定保留、合并或删除")
    print(f"  2. 完善缺失字段：为缺少字段的景点补充信息")
    print(f"  3. 优化描述：改进过短或重复的描述")
    print(f"  4. 多样化评分：考虑使用更真实的评分数据")
    print(f"  5. 验证坐标：确保所有坐标准确无误")
    
    return all_issues

def generate_duplicate_report(city_name=None):
    """生成重复景点的详细报告"""
    data_dir = Path('data')
    
    if city_name:
        files = [data_dir / f'spots_{city_name}.json']
    else:
        files = sorted(data_dir.glob('spots_*.json'))
    
    print("=" * 80)
    print("🔍 重复景点详细报告")
    print("=" * 80)
    
    for json_file in files:
        city = json_file.stem.replace('spots_', '')
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                spots = json.load(f)
        except:
            continue
        
        duplicates = check_duplicate_spots(spots, city)
        
        if duplicates:
            print(f"\n📍 城市: {city}")
            print(f"   发现 {len(duplicates)} 组疑似重复景点\n")
            
            for i, dup in enumerate(duplicates, 1):
                print(f"   {i}. 景点对比:")
                print(f"      景点A: {dup['spot1']} (索引: {dup['index1']})")
                print(f"      景点B: {dup['spot2']} (索引: {dup['index2']})")
                print(f"      名称相似度: {dup['similarity']:.2%}")
                if dup['distance']:
                    print(f"      距离: {dup['distance']:.0f} 米")
                print(f"      判断依据: {dup['reason']}")
                print()

def generate_cleanup_suggestions(city_name):
    """为特定城市生成清理建议"""
    data_dir = Path('data')
    json_file = data_dir / f'spots_{city_name}.json'
    
    if not json_file.exists():
        print(f"❌ 未找到城市数据文件: {json_file}")
        return
    
    with open(json_file, 'r', encoding='utf-8') as f:
        spots = json.load(f)
    
    print("=" * 80)
    print(f"🛠️ {city_name} 数据清理建议")
    print("=" * 80)
    
    # 重复景点建议
    duplicates = check_duplicate_spots(spots, city_name)
    if duplicates:
        print(f"\n1️⃣ 重复景点处理建议 ({len(duplicates)} 组):")
        print("-" * 80)
        
        for i, dup in enumerate(duplicates, 1):
            spot1 = spots[dup['index1']]
            spot2 = spots[dup['index2']]
            
            print(f"\n  组 {i}:")
            print(f"    景点A [{dup['index1']}]: {dup['spot1']}")
            print(f"      类别: {spot1.get('category')}, 评分: {spot1.get('rating')}")
            print(f"      描述长度: {len(spot1.get('description', ''))} 字符")
            
            print(f"    景点B [{dup['index2']}]: {dup['spot2']}")
            print(f"      类别: {spot2.get('category')}, 评分: {spot2.get('rating')}")
            print(f"      描述长度: {len(spot2.get('description', ''))} 字符")
            
            print(f"    建议: ", end='')
            if dup['similarity'] > 0.9 and (dup['distance'] is None or dup['distance'] < 50):
                print("很可能是重复，建议删除其中一个")
            elif dup['similarity'] > 0.8:
                print("疑似重复，需要人工确认")
            elif dup['distance'] and dup['distance'] < 100:
                print("位置非常接近，检查是否为同一景点的不同名称")
            else:
                print("需要进一步确认")
    
    # 其他质量问题
    desc_issues = check_description_quality(spots, city_name)
    if desc_issues:
        print(f"\n2️⃣ 描述质量问题 ({len(desc_issues)} 个):")
        print("-" * 80)
        type_counts = defaultdict(list)
        for issue in desc_issues:
            type_counts[issue['type']].append(issue)
        
        for issue_type, items in type_counts.items():
            print(f"\n  {issue_type} ({len(items)} 个):")
            for item in items[:5]:
                print(f"    • [{item['index']}] {item['spot']}")
            if len(items) > 5:
                print(f"    ... 还有 {len(items) - 5} 个")

def export_duplicates_json(output_file='output/duplicates_report.json'):
    """导出重复景点报告为JSON"""
    data_dir = Path('data')
    output_path = Path(output_file)
    output_path.parent.mkdir(exist_ok=True)
    
    report = {}
    
    for json_file in sorted(data_dir.glob('spots_*.json')):
        city = json_file.stem.replace('spots_', '')
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                spots = json.load(f)
        except:
            continue
        
        duplicates = check_duplicate_spots(spots, city)
        
        if duplicates:
            report[city] = {
                'total_spots': len(spots),
                'duplicate_groups': len(duplicates),
                'duplicates': [{
                    'spot1': dup['spot1'],
                    'spot2': dup['spot2'],
                    'index1': dup['index1'],
                    'index2': dup['index2'],
                    'similarity': round(dup['similarity'], 3),
                    'distance_meters': round(dup['distance'], 1) if dup['distance'] else None,
                    'reason': dup['reason']
                } for dup in duplicates]
            }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 重复景点报告已导出到: {output_path}")
    return report

def interactive_cleanup_duplicates(city_name):
    """
    交互式清理重复景点（不会影响任何已有功能）
    """
    data_dir = Path('data')
    json_file = data_dir / f'spots_{city_name}.json'

    if not json_file.exists():
        print(f"❌ 未找到城市数据文件: {json_file}")
        return

    with open(json_file, 'r', encoding='utf-8') as f:
        spots = json.load(f)

    duplicates = check_duplicate_spots(spots, city_name)

    if not duplicates:
        print("✅ 未发现重复景点，无需清理")
        return

    print("=" * 80)
    print(f"🧹 交互式重复景点清理：{city_name}")
    print("=" * 80)

    to_delete = set()

    for idx, dup in enumerate(duplicates, 1):
        i, j = dup['index1'], dup['index2']

        # 如果已被删除，跳过
        if i in to_delete or j in to_delete:
            continue

        spot_a = spots[i]
        spot_b = spots[j]

        print(f"\n[{idx}] 疑似重复景点")
        print("-" * 80)
        print(f"A [{i}] {spot_a.get('name')}")
        print(f"   rating={spot_a.get('rating')}  desc_len={len(spot_a.get('description',''))}")
        print(f"B [{j}] {spot_b.get('name')}")
        print(f"   rating={spot_b.get('rating')}  desc_len={len(spot_b.get('description',''))}")
        print(f"判断依据: {dup['reason']}")

        choice = input("操作 ([1]删A / [2]删B / [s]跳过 / [q]退出): ").strip().lower()

        if choice == '1':
            to_delete.add(i)
            print("🗑️ 已标记删除 A")
        elif choice == '2':
            to_delete.add(j)
            print("🗑️ 已标记删除 B")
        elif choice == 'q':
            print("⛔ 已退出清理流程")
            break
        else:
            print("⏭️ 跳过该组")

    if not to_delete:
        print("⚠️ 未选择删除任何景点")
        return

    # 备份
    backup = json_file.with_suffix('.json.bak')
    json_file.replace(backup)
    print(f"\n📦 原文件已备份为: {backup.name}")

    # 反向删除，保证索引安全
    for index in sorted(to_delete, reverse=True):
        del spots[index]

    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(spots, f, ensure_ascii=False, indent=2)

    print(f"✅ 清理完成，共删除 {len(to_delete)} 个景点")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'analyze':
            # 全面分析所有城市
            analyze_data_quality()
        
        elif command == 'duplicates':
            # 只显示重复景点报告
            city = sys.argv[2] if len(sys.argv) > 2 else None
            generate_duplicate_report(city)
        
        elif command == 'cleanup':
            # 为特定城市生成清理建议
            if len(sys.argv) < 3:
                print("请指定城市名称，例如: python check_data_quality.py cleanup beijing")
            else:
                city = sys.argv[2]
                generate_cleanup_suggestions(city)
        
        elif command == 'export':
            # 导出报告为JSON
            export_duplicates_json()
        
        elif command == 'interactive-clean':
            if len(sys.argv) < 3:
                print("请指定城市名称，例如: python check_data_quality.py interactive-clean beijing")
            else:
                city = sys.argv[2]
                interactive_cleanup_duplicates(city)

        
        else:
            print("未知命令。可用命令:")
            print("  analyze    - 全面分析所有城市数据质量")
            print("  duplicates [city] - 显示重复景点报告")
            print("  cleanup <city> - 为特定城市生成清理建议")
            print("  export     - 导出重复景点报告为JSON")
    else:
        # 默认执行全面分析
        analyze_data_quality()
