#!/usr/bin/env python3
"""
为中国城市的景点添加英文名称
"""
import json
import os
from pathlib import Path

# 中国城市列表
CHINA_CITIES = [
    "beijing", "changchun", "chengdu", "dongguang", "foshan", 
    "fuzhou", "guangzhou", "guiyang", "hangzhou", "harbin",
    "hefei", "hongkong", "kunming", "lanzhou", "nanjing",
    "ningbo", "qingdao", "shenyang", "shenzhen", "shijiazhuang",
    "suzhou", "taiyuan", "urumqi", "xiamen"
]

# 常见景点类型的英文翻译（按长度排序，长的优先匹配）
CATEGORY_TRANSLATIONS = {
    "科学技术博物馆": "Science & Technology Museum",
    "自然博物馆": "Natural History Museum",
    "历史博物馆": "History Museum",
    "革命历史纪念馆": "Revolutionary History Memorial",
    "植物园": "Botanical Garden",
    "动物园": "Zoo",
    "游乐园": "Amusement Park",
    "水族馆": "Aquarium",
    "会展中心": "Convention Center",
    "纪念馆": "Memorial Hall",
    "博物馆": "Museum",
    "美术馆": "Art Gallery",
    "艺术馆": "Art Museum",
    "科技馆": "Science Museum",
    "展览馆": "Exhibition Hall",
    "文化馆": "Cultural Center",
    "图书馆": "Library",
    "体育馆": "Stadium",
    "文化中心": "Cultural Center",
    "体育中心": "Sports Center",
    "购物中心": "Shopping Center",
    "商业中心": "Commercial Center",
    "中心": "Center",
    "公园": "Park",
    "广场": "Square",
    "寺庙": "Temple",
    "寺": "Temple",
    "庙": "Temple",
    "塔": "Pagoda",
    "楼": "Tower",
    "阁": "Pavilion",
    "宫殿": "Palace",
    "宫": "Palace",
    "府": "Mansion",
    "陵墓": "Mausoleum",
    "陵": "Mausoleum",
    "墓": "Tomb",
    "故居": "Former Residence",
    "旧居": "Former Residence",
    "遗址": "Site",
    "古迹": "Historical Site",
    "名胜古迹": "Historic Site",
    "城墙": "City Wall",
    "长城": "Great Wall",
    "山": "Mountain",
    "湖": "Lake",
    "河": "River",
    "江": "River",
    "海": "Sea",
    "岛": "Island",
    "步行街": "Walking Street",
    "商业街": "Commercial Street",
    "街": "Street",
    "路": "Road",
    "桥": "Bridge",
    "门": "Gate",
    "市场": "Market",
    "商场": "Mall",
    "大厦": "Building",
    "村": "Village",
    "镇": "Town",
    "区": "District",
    "园林": "Garden",
    "园": "Garden",
    "苑": "Garden",
    "森林": "Forest",
    "林": "Forest",
    "影城": "Cinema",
    "剧院": "Theater",
    "音乐厅": "Concert Hall",
    "火车站": "Railway Station",
    "汽车站": "Bus Station",
    "站": "Station",
    "机场": "Airport",
    "码头": "Wharf",
    "港": "Port",
    "古城": "Ancient Town",
    "古镇": "Ancient Town",
    "老街": "Old Street",
    "风景区": "Scenic Area",
    "景区": "Scenic Area",
    "旅游区": "Tourist Area",
    "度假区": "Resort",
    "摩崖石刻": "Cliff Inscription",
    "石刻": "Stone Carving",
    "碑": "Monument",
    "石窟": "Grotto",
    "洞": "Cave",
    "瀑布": "Waterfall",
    "温泉": "Hot Spring",
    "海滩": "Beach",
    "沙滩": "Beach",
    "公馆": "Mansion",
    "会馆": "Guild Hall",
    "书院": "Academy",
    "学校": "School",
    "大学": "University",
    "教堂": "Church",
    "清真寺": "Mosque",
}

# 城市名称翻译
CITY_NAMES = {
    "北京": "Beijing",
    "上海": "Shanghai",
    "广州": "Guangzhou",
    "深圳": "Shenzhen",
    "杭州": "Hangzhou",
    "成都": "Chengdu",
    "南京": "Nanjing",
    "西安": "Xi'an",
    "苏州": "Suzhou",
    "武汉": "Wuhan",
    "重庆": "Chongqing",
    "天津": "Tianjin",
    "青岛": "Qingdao",
    "厦门": "Xiamen",
    "大连": "Dalian",
    "宁波": "Ningbo",
    "沈阳": "Shenyang",
    "哈尔滨": "Harbin",
    "长春": "Changchun",
    "福州": "Fuzhou",
    "贵阳": "Guiyang",
    "昆明": "Kunming",
    "兰州": "Lanzhou",
    "太原": "Taiyuan",
    "乌鲁木齐": "Urumqi",
    "合肥": "Hefei",
    "石家庄": "Shijiazhuang",
    "佛山": "Foshan",
    "东莞": "Dongguang",
    "香港": "Hong Kong",
}

def translate_spot_name(chinese_name):
    """
    将中文景点名称翻译成英文
    使用简单的规则匹配和替换
    """
    # 如果已经是英文，直接返回
    if not any('\u4e00' <= c <= '\u9fff' for c in chinese_name):
        return chinese_name
    
    # 移除引号
    name = chinese_name.strip('"「」『』""''')
    original_name = name
    
    # 如果名称主要是数字，保留原样
    if name[0].isdigit():
        return original_name
    
    # 尝试匹配城市名称
    city_prefix = ""
    for cn_city, en_city in CITY_NAMES.items():
        if name.startswith(cn_city):
            city_prefix = en_city
            name = name[len(cn_city):]
            break
    
    # 移除"市"、"省"等行政单位
    name = name.replace("市", " ").replace("省", " ").replace("县", " ").replace("区", " ")
    
    # 尝试匹配景点类型（从长到短匹配，避免部分匹配问题）
    sorted_categories = sorted(CATEGORY_TRANSLATIONS.items(), key=lambda x: -len(x[0]))
    translations = []
    remaining = name
    
    for cn_type, en_type in sorted_categories:
        if cn_type in remaining:
            parts = remaining.split(cn_type)
            if len(parts) > 1:
                # 保存翻译的部分
                translations.append((parts[0].strip(), cn_type, en_type))
                remaining = cn_type.join(parts[1:])
    
    # 重新构建翻译
    if translations:
        # 取第一个主要翻译
        prefix, cn_type, en_type = translations[0]
        if prefix:
            # 保留前缀（如果是中文则保留原样，可能是专有名词）
            english_name = f"{prefix} {en_type}" if prefix else en_type
        else:
            english_name = en_type
    else:
        english_name = name
    
    # 组合城市前缀和景点名称
    if city_prefix and english_name:
        english_name = f"{city_prefix} {english_name}".strip()
    elif city_prefix:
        english_name = city_prefix
    
    # 清理多余空格
    english_name = " ".join(english_name.split())
    
    # 如果翻译后的名称太短或主要还是中文，返回原名
    chinese_char_count = sum(1 for c in english_name if '\u4e00' <= c <= '\u9fff')
    total_chars = len(english_name.replace(" ", ""))
    
    # 如果翻译结果超过70%是中文，或者长度太短，返回原名
    if total_chars == 0 or (total_chars > 0 and chinese_char_count / total_chars > 0.7):
        return original_name
    
    if len(english_name.strip()) < 2:
        return original_name
    
    return english_name.strip()

def add_english_names_to_file(filepath, force_update=False):
    """
    为指定的景点文件添加英文名称
    """
    print(f"Processing {filepath}...")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        spots = json.load(f)
    
    updated_count = 0
    for spot in spots:
        # 如果已经有 name_en 字段且不强制更新，跳过
        if 'name_en' in spot and not force_update:
            continue
        
        # 生成英文名称
        chinese_name = spot['name']
        english_name = translate_spot_name(chinese_name)
        
        # 添加或更新英文名称字段
        spot['name_en'] = english_name
        updated_count += 1
    
    # 保存更新后的文件
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(spots, f, ensure_ascii=False, indent=2)
    
    print(f"  Updated {updated_count} spots in {os.path.basename(filepath)}")
    return updated_count

def main():
    """
    主函数：为所有中国城市的景点文件添加英文名称
    """
    import sys
    force_update = '--force' in sys.argv
    
    data_dir = Path(__file__).parent.parent / "data"
    total_updated = 0
    
    for city in CHINA_CITIES:
        filepath = data_dir / f"spots_{city}.json"
        if filepath.exists():
            count = add_english_names_to_file(filepath, force_update)
            total_updated += count
        else:
            print(f"File not found: {filepath}")
    
    print(f"\nTotal spots updated: {total_updated}")
    print("Done!")

if __name__ == "__main__":
    main()
