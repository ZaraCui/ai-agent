"""
测试 /api/fetch_spots API 接口
这个脚本演示如何使用 API 接口来获取城市景点数据，而不需要在终端运行 fetch_osm_spots.py
"""

import requests
import json
import sys

# Flask 服务器地址
BASE_URL = "http://localhost:5000"

def fetch_spots_via_api(city_name):
    """
    通过 API 接口获取城市景点数据
    
    Args:
        city_name: 城市名称，例如 "Beijing", "Shanghai", "New York"
    
    Returns:
        dict: API 响应数据
    """
    url = f"{BASE_URL}/api/fetch_spots"
    payload = {
        "city": city_name
    }
    
    print(f"正在请求 API 获取 {city_name} 的景点数据...")
    print(f"URL: {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}\n")
    
    try:
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        
        if result.get('status') == 'success':
            data = result.get('data', {})
            print("✅ 成功!")
            print(f"\n城市: {data.get('city')}")
            print(f"景点数量: {data.get('spots_count')}")
            print(f"保存路径: {data.get('file_path')}")
            
            # 显示分类统计
            categories = data.get('categories', {})
            if categories:
                print(f"\n分类统计:")
                for cat, count in categories.items():
                    print(f"  - {cat}: {count} 个景点")
            
            # 显示前 10 个景点预览
            top_spots = data.get('top_spots', [])
            if top_spots:
                print(f"\n前 10 个景点预览:")
                for i, spot in enumerate(top_spots, 1):
                    print(f"  {i}. {spot.get('name')} ({spot.get('category')})")
            
            return result
        else:
            print(f"❌ 错误: {result.get('message')}")
            print(f"原因: {result.get('reason')}")
            return None
            
    except requests.exceptions.ConnectionError:
        print(f"❌ 连接错误: 无法连接到 {BASE_URL}")
        print("请确保 Flask 服务器正在运行 (python app.py)")
        return None
    except requests.exceptions.Timeout:
        print("❌ 请求超时")
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求失败: {str(e)}")
        return None
    except Exception as e:
        print(f"❌ 未知错误: {str(e)}")
        return None


def test_multiple_cities():
    """测试多个城市"""
    cities = ["Guangzhou", "Shenzhen", "Hangzhou"]
    
    print("=" * 60)
    print("测试多个城市的景点获取")
    print("=" * 60 + "\n")
    
    for city in cities:
        print(f"\n{'=' * 60}")
        fetch_spots_via_api(city)
        print(f"{'=' * 60}\n")
        input("按 Enter 继续下一个城市...")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # 如果提供了城市名称参数
        city = " ".join(sys.argv[1:])
        fetch_spots_via_api(city)
    else:
        # 否则运行测试模式
        print("使用方法:")
        print("  python test_fetch_spots_api.py [城市名]")
        print("\n示例:")
        print("  python test_fetch_spots_api.py Beijing")
        print("  python test_fetch_spots_api.py New York")
        print("  python test_fetch_spots_api.py")
        print("\n如果不提供城市名，将进入测试模式\n")
        
        choice = input("是否进入测试模式测试多个城市? (y/n): ")
        if choice.lower() == 'y':
            test_multiple_cities()
        else:
            city = input("请输入城市名称: ")
            if city:
                fetch_spots_via_api(city)
