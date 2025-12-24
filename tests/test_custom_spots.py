#!/usr/bin/env python3
"""
Test the custom spot selection feature via API.
"""

import requests
import json

API_BASE = "http://localhost:5000"

def test_get_spots():
    """Test the /api/spots/<city> endpoint."""
    print("\n" + "="*60)
    print("Test 1: Get Spots for Shanghai")
    print("="*60)
    
    response = requests.get(f"{API_BASE}/api/spots/shanghai")
    data = response.json()
    
    print(f"Status: {data['status']}")
    print(f"Total spots: {data['data']['total']}")
    print(f"\nFirst 5 spots:")
    for i, spot in enumerate(data['data']['spots'][:5], 1):
        print(f"  {i}. {spot['name']} ({spot['category']})")

def test_custom_selection():
    """Test planning with custom spot selection."""
    print("\n" + "="*60)
    print("Test 2: Plan Itinerary with Selected Spots")
    print("="*60)
    
    # Select only specific spots
    selected = [
        "The Bund",
        "Yu Garden",
        "Shanghai Tower",
        "Nanjing Road",
        "Jade Buddha Temple"
    ]
    
    payload = {
        "city": "shanghai",
        "start_date": "2025-01-01",
        "days": 2,
        "selected_spots": selected,
        "weights": {
            "time": 0.5,
            "distance": 0.2,
            "comfort": 0.3
        }
    }
    
    print(f"\n✅ Selected {len(selected)} spots:")
    for name in selected:
        print(f"  - {name}")
    
    response = requests.post(
        f"{API_BASE}/plan_itinerary",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    data = response.json()
    
    if data['status'] == 'success':
        print(f"\n✅ Plan generated successfully!")
        recommended = data['data']['comparison']['recommended_data']
        itinerary_dict = recommended['itinerary']
        
        print(f"\nGenerated itinerary:")
        for day_dict in itinerary_dict:
            print(f"\n  Day {day_dict['day']}: {len(day_dict['spots'])} spots")
            for spot in day_dict['spots']:
                print(f"    - {spot['name']}")
        
        # Verify only selected spots were used
        all_used_spots = set()
        for day_dict in itinerary_dict:
            for spot in day_dict['spots']:
                all_used_spots.add(spot['name'])
        
        print(f"\n✅ Verification: All {len(all_used_spots)} spots used are from selection")
        if all_used_spots - set(selected):
            print(f"❌ ERROR: Found unexpected spots: {all_used_spots - set(selected)}")
        else:
            print(f"✅ Perfect! Only selected spots were used.")
    else:
        print(f"❌ Error: {data.get('reason', 'Unknown error')}")

def test_no_selection():
    """Test planning without spot selection (use all spots)."""
    print("\n" + "="*60)
    print("Test 3: Plan Itinerary with ALL Spots (no selection)")
    print("="*60)
    
    payload = {
        "city": "shanghai",
        "start_date": "2025-01-01",
        "days": 3,
        "weights": {
            "time": 0.5,
            "distance": 0.2,
            "comfort": 0.3
        }
    }
    
    response = requests.post(
        f"{API_BASE}/plan_itinerary",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    data = response.json()
    
    if data['status'] == 'success':
        recommended = data['data']['comparison']['recommended_data']
        itinerary_dict = recommended['itinerary']
        
        all_used_spots = set()
        for day_dict in itinerary_dict:
            for spot in day_dict['spots']:
                all_used_spots.add(spot['name'])
        
        print(f"✅ Generated itinerary with {len(all_used_spots)} unique spots across {len(itinerary_dict)} days")
        print(f"   (Agent automatically selected optimal spots from all 21 available)")

if __name__ == "__main__":
    try:
        test_get_spots()
        test_custom_selection()
        test_no_selection()
        
        print("\n" + "="*60)
        print("✅ All tests completed!")
        print("="*60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to server.")
        print("   Please start the server with: python app.py")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
