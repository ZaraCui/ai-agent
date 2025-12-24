# Custom Spot Selection Feature

## Overview

Users can now select specific spots they want to visit, rather than letting the AI automatically choose from all available spots.

## Feature Description

### 1. **All City Spots Are Considered by the Agent**

- ✅ Agent loads all spot data for the selected city
- ✅ Planning algorithm considers all available spots
- ✅ Optimal spot combinations are selected through optimization

**Why aren't some spots selected?**
- Day limitations (3 days can only fit a limited number of spots)
- Time budget (240-360 minutes per day)
- Distance between spots (remote spots may be eliminated)
- Optimization objectives (minimize travel time and distance)

### 2. **Manual Spot Selection**

New feature gives users complete control over which spots to visit:

**UI Operations:**
1. Select a city (e.g., Shanghai)
2. Spot list automatically loads, displaying all available spots
3. Check the spots you want to visit
4. Click "Compare Transport Modes" to generate itinerary

**Optional Actions:**
- **Select All**: Quickly select all spots
- **Deselect All**: Clear all selections
- **No Selection**: Use all spots (default behavior)

### 3. **API Support**

#### Get City Spot List
```bash
GET /api/spots/<city>
```

Example Response:
```json
{
  "status": "success",
  "data": {
    "city": "shanghai",
    "spots": [
      {
        "name": "The Bund",
        "lat": 31.2401,
        "lon": 121.4897,
        "category": "outdoor",
        "duration_minutes": 60,
        "rating": 4.5
      }
    ],
    "total": 21
  }
}
```

#### Plan Itinerary (with spot selection)
```bash
POST /plan_itinerary
```

Request Body:
```json
{
  "city": "shanghai",
  "start_date": "2025-01-01",
  "days": 3,
  "selected_spots": ["The Bund", "Yu Garden", "Shanghai Tower"],  // Optional
  "weights": {
    "time": 0.5,
    "distance": 0.2,
    "comfort": 0.3
  }
}
```

**Parameter Description:**
- `selected_spots`: Optional array containing spot names
  - If provided: Only use selected spots
  - If empty/null/omitted: Use all spots for that city

## Use Cases

### Case 1: Full Customization
User knows exactly which spots to visit:
```
✅ Select: The Bund, Yu Garden, Shanghai Tower, Nanjing Road
→ Agent plans 2-3 day itinerary using only these 4 spots
```

### Case 2: Exploration Mode
User unsure about which spots, makes no selection:
```
✅ No spot selection (default)
→ Agent automatically selects optimal combination from 21 spots
```

### Case 3: Exclude Unwanted Spots
User doesn't want certain spots, selects the rest:
```
❌ Don't want: Shanghai Disneyland, Shopping malls
✅ Select: Remaining 18 spots
→ Agent optimizes among these 18
```

## Testing & Validation

Run test script to verify functionality:
```bash
python3 test_custom_spots.py
```

Test Coverage:
1. ✅ Get spot list API
2. ✅ Generate 2-day itinerary with 5 selected spots
3. ✅ Use all 21 spots when none selected
4. ✅ Verify only user-selected spots are used

## Technical Implementation

### Frontend (templates/index.html)
- Added Shanghai to city dropdown
- Listen to city change event, call `/api/spots/<city>`
- Render spot checkbox list (with scrolling)
- Collect selected spot names on form submission

### Backend (app.py)
- New `GET /api/spots/<city>` endpoint returns spot list
- Modified `POST /plan_itinerary` to accept `selected_spots` parameter
- Filter spots after loading, keeping only selected ones
- Maintains backward compatibility (no selection = all spots)

## FAQ

**Q: Why doesn't my new spot appear in the itinerary?**
A: Two possible reasons:
1. Optimization algorithm didn't select it (day/time/distance constraints)
2. You didn't check it (if using spot selection feature)

**Q: How can I ensure a specific spot is definitely included?**
A: Use the spot selection feature and only check the spots you want (including the must-visit one)

**Q: What if I want to visit all spots?**
A: Three options:
1. Click "Select All" button
2. Make no selection (default behavior)
3. Increase travel days (e.g., 5-7 days)

**Q: What happens if I select too many spots?**
A: Agent will try to use all of them, but if days are limited:
- Increases spots per day
- Optimizes spot order to reduce travel time
- May skip some spots if they truly don't fit

## Future Enhancements

Possible improvements (refer to PRODUCT_ROADMAP.md):
- [ ] Filter spots by category (museums/temples only)
- [ ] Mark "must-visit" spots (high priority)
- [ ] Display spot preview on map
- [ ] Save user spot preferences
- [ ] Recommend similar spots
