#!/usr/bin/env python3
import json
from agent.models import Spot

# Test loading Shanghai data
with open('data/spots_shanghai.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f'✅ Loaded {len(data)} spots from Shanghai')

# Test creating Spot objects
spots = []
errors = []
for s in data:
    try:
        spot = Spot(**s)
        spots.append(spot)
    except Exception as e:
        errors.append(f"Error with spot {s.get('name', 'unknown')}: {e}")

if errors:
    print('\n❌ Errors found:')
    for err in errors:
        print(f'  {err}')
else:
    print(f'✅ Successfully created {len(spots)} Spot objects')
    print(f'\nFirst spot: {spots[0].name}')
    print(f'  Location: ({spots[0].lat}, {spots[0].lon})')
    print(f'  Category: {spots[0].category}')
    print(f'  Rating: {spots[0].rating}')
    print(f'  Duration: {spots[0].duration_minutes} minutes')
    
    print(f'\nCategories found: {sorted(set(s.category for s in spots))}')
    print(f'\nAll spots loaded successfully! 🎉')
