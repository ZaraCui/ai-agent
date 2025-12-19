#!/usr/bin/env python3
"""
Split China cities spots JSON file
Split spots_china_cities.json into separate JSON files for each city
"""
import json
import os
from collections import defaultdict

def split_china_spots():
    # Read the merged JSON file
    input_file = 'data/spots_china_cities.json'
    
    print(f"Reading {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        all_spots = json.load(f)
    
    print(f"Total spots loaded: {len(all_spots)}")
    
    # Group spots by city
    spots_by_city = defaultdict(list)
    for spot in all_spots:
        city = spot.get('city', 'Unknown')
        spots_by_city[city].append(spot)
    
    print(f"\nFound {len(spots_by_city)} cities:")
    for city, spots in sorted(spots_by_city.items()):
        print(f"  - {city}: {len(spots)} spots")
    
    # Create separate JSON files for each city
    print("\nCreating individual JSON files...")
    for city, spots in spots_by_city.items():
        # Convert city name to filename (lowercase, handle special characters)
        city_filename_map = {
            'Beijing': 'beijing',
            'Shanghai': 'shanghai',
            'Guangzhou': 'guangzhou',
            'Shenzhen': 'shenzhen',
            'Hangzhou': 'hangzhou',
            'Chengdu': 'chengdu',
            'Chongqing': 'chongqing',
            'Wuhan': 'wuhan',
            'Xi\'an': 'xian',
            'Suzhou': 'suzhou',
            'Tianjin': 'tianjin',
            'Nanjing': 'nanjing',
            'Qingdao': 'qingdao',
            'Dalian': 'dalian',
            'Xiamen': 'xiamen',
            'Shantou': 'shantou',
            'Ningbo': 'ningbo',
            'Kunming': 'kunming',
            'Harbin': 'harbin',
            'Changsha': 'changsha',
            'Hong Kong': 'hongkong',
            'Macau': 'macau',
        }
        
        filename = city_filename_map.get(city, city.lower().replace(' ', '').replace('\'', ''))
        output_file = f'data/spots_{filename}.json'
        
        # Write JSON file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(spots, f, ensure_ascii=False, indent=2)
        
        print(f"  ✓ Created {output_file} ({len(spots)} spots)")
    
    print(f"\nDone! Created JSON files for {len(spots_by_city)} cities")

if __name__ == '__main__':
    split_china_spots()
