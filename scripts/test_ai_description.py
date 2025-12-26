#!/usr/bin/env python3
"""
测试AI描述生成功能
Quick test script for AI description generation
"""

import json
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_api_key():
    """测试API密钥是否配置"""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key or api_key == 'your_openai_api_key_here':
        print("❌ OpenAI API密钥未配置")
        print("   请在.env文件中设置: OPENAI_API_KEY=sk-your-key")
        return False
    print("✅ API密钥已配置")
    return True

def test_openai_import():
    """测试OpenAI库是否安装"""
    try:
        from openai import OpenAI
        print("✅ OpenAI库已安装")
        return True
    except ImportError:
        print("❌ OpenAI库未安装")
        print("   请运行: pip install openai")
        return False

def test_data_files():
    """测试数据文件是否存在"""
    data_dir = Path('data')
    spot_files = list(data_dir.glob('spots_*.json'))
    
    if not spot_files:
        print("❌ 未找到景点数据文件")
        return False
    
    print(f"✅ 找到 {len(spot_files)} 个城市的数据文件")
    
    # 显示前5个城市
    cities = [f.stem.replace('spots_', '') for f in spot_files[:5]]
    print(f"   示例城市: {', '.join(cities)}...")
    
    return True

def show_sample_spot():
    """显示一个示例景点"""
    try:
        sample_file = Path('data/spots_kunming.json')
        if not sample_file.exists():
            sample_file = list(Path('data').glob('spots_*.json'))[0]
        
        with open(sample_file, 'r', encoding='utf-8') as f:
            spots = json.load(f)
        
        if spots:
            spot = spots[0]
            city = sample_file.stem.replace('spots_', '')
            print(f"\n📍 示例景点 ({city}):")
            print(f"   名称: {spot['name']}")
            print(f"   类别: {spot['category']}")
            print(f"   当前描述: {spot['description'][:80]}...")
            return True
    except Exception as e:
        print(f"⚠️ 读取示例景点失败: {e}")
        return False

def main():
    """主测试函数"""
    print("="*70)
    print("🧪 AI描述生成器 - 环境测试")
    print("="*70)
    print()
    
    all_passed = True
    
    # 测试1: API密钥
    print("测试 1/4: 检查OpenAI API密钥...")
    if not test_api_key():
        all_passed = False
    print()
    
    # 测试2: OpenAI库
    print("测试 2/4: 检查OpenAI库安装...")
    if not test_openai_import():
        all_passed = False
    print()
    
    # 测试3: 数据文件
    print("测试 3/4: 检查景点数据文件...")
    if not test_data_files():
        all_passed = False
    print()
    
    # 测试4: 示例景点
    print("测试 4/4: 读取示例景点...")
    if not show_sample_spot():
        all_passed = False
    print()
    
    # 总结
    print("="*70)
    if all_passed:
        print("✅ 所有测试通过！可以开始使用AI描述生成器")
        print()
        print("📝 下一步:")
        print("   1. 确保.env中的OPENAI_API_KEY已正确设置")
        print("   2. 运行: python scripts/generate_ai_descriptions.py")
        print("   3. 先用预览模式测试几个景点")
        print()
        print("📖 详细文档: docs/AI_DESCRIPTION_GENERATOR.md")
    else:
        print("⚠️ 部分测试失败，请先解决上述问题")
    print("="*70)

if __name__ == '__main__':
    main()
