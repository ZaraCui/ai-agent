from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
from agent.planner import plan_itinerary_soft_constraints
from agent.geometry import TransportMode
from agent.geometry import travel_cost_minutes, distance as geo_distance
from agent.constraints import ScoreConfig
from agent.models import Spot
from agent.explainer import weather_advice
from agent.cache import cache, cache_key_for_spots, cache_key_for_cities, cache_key_for_plan
from agent.rate_limiter import rate_limit
from agent.logging_config import setup_logging, log_request, log_error, log_performance
from agent.itinerary_storage import ItineraryStorage
from agent.auth import AuthService
from agent.user_profile import UserProfileService
from agent.places_api import PlacesApiService
import jwt
from functools import wraps
from datetime import date
import json
import os
import requests
import traceback
from typing import Dict, List, Any, Optional, Tuple
from dotenv import load_dotenv
from flask_cors import CORS

# Load environment variables
load_dotenv()

# Setup logging
logger = setup_logging(
    "travel-agent",
    log_level=os.environ.get('LOG_LEVEL', 'INFO'),
    log_file=os.environ.get('LOG_FILE', 'logs/app.log') if os.environ.get('LOG_FILE') != 'None' else None
)

# Initialize itinerary storage
storage = ItineraryStorage()
auth_service = AuthService()
user_profile_service = UserProfileService()
places_api_service = PlacesApiService()

app = Flask(__name__)
app.logger = logger  # Replace Flask's default logger
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Enable CORS for cross-origin requests from the static frontend.
# You can set `CORS_ORIGINS` env var to a comma-separated list of allowed origins
# e.g. CORS_ORIGINS=https://your-frontend.vercel.app
allowed_origins = os.environ.get('CORS_ORIGINS', '*').split(',')
CORS(app, resources={r"/*": {"origins": allowed_origins}})

# Initialize SocketIO with CORS support
socketio = SocketIO(
    app, 
    cors_allowed_origins=allowed_origins,
    async_mode='eventlet',
    logger=True,
    engineio_logger=True
)

# Request logging middleware
@app.before_request
def before_request():
    """Log incoming requests"""
    request.start_time = __import__('time').time()

@app.after_request
def after_request(response):
    """Log request completion with duration"""
    if hasattr(request, 'start_time'):
        duration = __import__('time').time() - request.start_time
        log_request(logger, request, response, duration)
    return response

@app.teardown_request
def teardown_request(error=None):
    """Log request errors"""
    if error:
        log_error(logger, error, {
            'path': request.path,
            'method': request.method,
            'ip': request.remote_addr
        })

# ===== Unified response helper =====
def success_response(data, message="Success"):
    """Return a successful response with status and data."""
    return jsonify({
        "status": "success",
        "message": message,
        "data": data
    }), 200


def error_response(reason, status_code=400, message="Error"):
    """Return an error response with status and reason."""
    logger.warning(f"Error response: {message} - {reason}", extra={'status_code': status_code})
    return jsonify({
        "status": "error",
        "code": status_code,
        "message": message,
        "reason": reason
    }), status_code

@log_performance(logger, threshold_ms=5000)
def compare_transport_modes(city: str, spots: List[Spot], cfg: ScoreConfig, days: int = 3, weights: dict = None, session_id: str = None) -> Dict:
    """
    Calculate itineraries for all transport modes and return comparison data.
    Returns structured data with all modes and recommendation.
    
    Args:
        session_id: Optional session ID for sending progress updates via WebSocket
    """
    modes = [TransportMode.WALK, TransportMode.TRANSIT, TransportMode.TAXI]
    results = {}

    best_mode = None
    best_score = float('inf')
    best_data = None
    
    total_modes = len(modes)

    for idx, mode in enumerate(modes):
        # Send progress update
        if session_id:
            progress = int((idx / total_modes) * 100)
            socketio.emit('planning_progress', {
                'progress': progress,
                'stage': f'正在计算 {mode.value.upper()} 模式...',
                'current_mode': mode.value,
                'total_modes': total_modes,
                'completed_modes': idx
            }, room=session_id)
        
        try:
            itinerary, score, reasons = plan_itinerary_soft_constraints(
                city=city,
                spots=spots,
                days=days,
                cfg=cfg,
                mode=mode,
                trials=200,
            )

            # Convert itinerary to dict
            itinerary_dict = []
            for day in itinerary.days:
                # compute total travel minutes for the day
                travel_minutes = 0.0
                for i in range(len(day.spots) - 1):
                    try:
                        travel_minutes += travel_cost_minutes(day.spots[i], day.spots[i + 1], mode)
                    except Exception:
                        travel_minutes += 0.0

                # ensure total distance exists (planner finalizes distances)
                total_km = getattr(day, 'total_distance_km', None)

                day_dict = {
                    "day": day.day,
                    "spots": [spot.to_dict() for spot in day.spots],
                    "travel_minutes": round(travel_minutes, 1),
                    "total_distance_km": total_km,
                }
                itinerary_dict.append(day_dict)

            mode_data = {
                "score": round(score, 2),
                "reasons": reasons,
                "itinerary": itinerary_dict
            }

            # If there are no penalty reasons, add friendly summary benefits
            if not mode_data.get('reasons'):
                # summarize total distance and time across days
                total_minutes = 0.0
                total_km = 0.0
                for d in itinerary_dict:
                    total_minutes += d.get('travel_minutes', 0) or 0
                    total_km += d.get('total_distance_km', 0) or 0

                friendly_reasons = []
                friendly_reasons.append(f"Estimated travel time: {round(total_minutes,1)} minutes")
                friendly_reasons.append(f"Estimated travel distance: {round(total_km,2)} km")
                friendly_reasons.append("Meets configured constraints; no penalties applied")
                mode_data['reasons'] = friendly_reasons

            results[mode.value] = mode_data

            # Track best mode (lowest score is better)
            if score < best_score:
                best_score = score
                best_mode = mode
                best_data = mode_data

        except Exception as e:
            app.logger.warning(f"Failed to plan itinerary for mode {mode.value}: {str(e)}")
            results[mode.value] = {
                "error": f"Failed to calculate: {str(e)}"
            }

    # Compute multi-dimensional utility (0-100) based on time, distance, comfort
    metrics = {}
    costs = []
    times = []
    dists = []
    ratings = []

    for m_key, m_data in results.items():
        if m_data.get('error'):
            metrics[m_key] = {
                'cost': None,
                'minutes': None,
                'km': None,
                'avg_rating': None,
            }
            continue

        cost = float(m_data.get('score', 0.0))
        total_minutes = 0.0
        total_km = 0.0
        rating_vals = []
        for d in m_data.get('itinerary', []):
            total_minutes += float(d.get('travel_minutes', 0) or 0)
            total_km += float(d.get('total_distance_km', 0) or 0)
            for s in d.get('spots', []):
                try:
                    if s.get('rating') is not None:
                        rating_vals.append(float(s.get('rating')))
                except Exception:
                    pass

        avg_rating = float(sum(rating_vals) / len(rating_vals)) if rating_vals else 0.0

        metrics[m_key] = {
            'cost': cost,
            'minutes': total_minutes,
            'km': total_km,
            'avg_rating': avg_rating,
        }

        costs.append(cost)
        times.append(total_minutes)
        dists.append(total_km)
        ratings.append(avg_rating)

    def normalize_list(vals, invert=False):
        if not vals:
            return {}
        mn = min(vals)
        mx = max(vals)
        res = {}
        for v in vals:
            if mx == mn:
                norm = 1.0
            else:
                norm = (v - mn) / (mx - mn)
            if invert:
                norm = 1.0 - norm
            res[v] = norm
        return res

    cost_norm = normalize_list(costs, invert=True)
    time_norm = normalize_list(times, invert=True)
    dist_norm = normalize_list(dists, invert=True)
    rating_norm = normalize_list(ratings, invert=False)

    # weights: if provided, normalize; otherwise use defaults
    if not weights:
        w_time = 0.5
        w_dist = 0.2
        w_comf = 0.3
    else:
        try:
            w_time = float(weights.get('time', 0.5))
            w_dist = float(weights.get('distance', 0.2))
            w_comf = float(weights.get('comfort', 0.3))
        except Exception:
            w_time, w_dist, w_comf = 0.5, 0.2, 0.3

    # normalize to sum to 1
    total_w = (w_time + w_dist + w_comf) or 1.0
    w_time /= total_w
    w_dist /= total_w
    w_comf /= total_w

    # attach utility_score to each mode
    for m_key, m_data in results.items():
        mm = metrics.get(m_key)
        if not mm or mm.get('cost') is None:
            m_data['utility_score'] = None
            m_data['utility_explanation'] = 'No data'
            continue

        c = mm['cost']
        t = mm['minutes']
        k = mm['km']
        r = mm['avg_rating']

        nt = time_norm.get(t, 1.0) if times else 1.0
        nd = dist_norm.get(k, 1.0) if dists else 1.0
        nr = rating_norm.get(r, 1.0) if ratings else 1.0

        utility = (nt * w_time + nd * w_dist + nr * w_comf) * 100.0

        m_data['utility_score'] = round(utility, 1)
        m_data['utility_explanation'] = (
            f"Combines time({w_time*100:.0f}%):{nt:.2f}, distance({w_dist*100:.0f}%):{nd:.2f}, "
            f"comfort({w_comf*100:.0f}%):{nr:.2f}. Higher is better. Original cost: {c:.2f}."
        )

    # pick recommended by highest utility (fallback to lowest cost)
    best_mode_util = None
    best_util = -1.0
    for m_key, m_data in results.items():
        util = m_data.get('utility_score')
        if util is None:
            continue
        if util > best_util:
            best_util = util
            best_mode_util = m_key

    recommended_mode = best_mode_util if best_mode_util else (best_mode.value if best_mode else None)
    recommended_data = results.get(recommended_mode) if recommended_mode else best_data

    return {
        "modes": results,
        "recommended_mode": recommended_mode,
        "recommended_data": recommended_data,
    }

@app.route('/')
def index():
    # 返回首页，前端页面
    # Inject Google Maps API key from environment into the rendered template
    google_maps_key = os.environ.get('GOOGLE_MAPS_API_KEY', '')
    return render_template('index.html', google_maps_api_key=google_maps_key)

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files (especially config.js)"""
    return send_from_directory('static', filename)

@app.route('/api/cities', methods=['GET'])
@rate_limit(limit=60, window=60)  # 60 requests per minute
def get_cities():
    """
    API endpoint to get a list of available cities based on data files.
    Uses Redis cache to improve performance.
    """
    try:
        # Try to get from cache first
        cache_key = cache_key_for_cities()
        from agent.cache import get
        cached_cities = get(cache_key)
        
        if cached_cities is not None:
            logger.debug(f"Cities loaded from cache, count={len(cached_cities)}")
            return success_response(cached_cities, f"Found {len(cached_cities)} cities (cached)")
        
        # Use absolute path compatible with Vercel deployment
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(base_dir, 'data')
        cities = []
        
        if os.path.exists(data_dir):
            for filename in os.listdir(data_dir):
                if filename.startswith('spots_') and filename.endswith('.json'):
                    city_key = filename[6:-5]
                    display_name = city_key.replace('_', ' ').title()
                    cities.append({"value": city_key, "label": display_name})
        else:
            # This path should now be found on Vercel
            return error_response(f"Data directory not found: {data_dir}", 500, "Configuration error")
        
        if not cities:
            return error_response(f"No cities available in {data_dir}", 500, "No data found")
        
        # Sort cities alphabetically
        cities.sort(key=lambda x: x['label'])
        
        # Cache the result for 24 hours (cities list doesn't change often)
        from agent.cache import set
        set(cache_key, cities, ttl=86400)
        
        return success_response(cities, f"Found {len(cities)} cities")
    except Exception as e:
        import traceback
        traceback.print_exc()
        return error_response(str(e), 500, "Failed to list cities")

# Helper to map Google Places types to our internal categories
PLACE_TYPE_TO_CATEGORY = {
    "museum": "museum", "art_gallery": "museum",
    "church": "temple", "mosque": "temple", "synagogue": "temple", "hindu_temple": "temple",
    "park": "outdoor", "zoo": "outdoor", "amusement_park": "outdoor",
    "shopping_mall": "shopping", "store": "shopping",
    "restaurant": "food", "cafe": "food", "bakery": "food",
    "tourist_attraction": "sightseeing", "point_of_interest": "sightseeing",
    "aquarium": "indoor", "library": "indoor",
}

def _convert_place_to_spot(place_details: Dict[str, Any], city: str) -> Optional[Spot]:
    """Converts Google Place details into a Spot object."""
    if not place_details or not place_details.get('name'):
        return None

    name = place_details.get('name', '')
    lat = place_details['geometry']['location']['lat']
    lon = place_details['geometry']['location']['lng']

    # Determine category
    category = "sightseeing"  # Default category
    if 'types' in place_details:
        for place_type in place_details['types']:
            if place_type in PLACE_TYPE_TO_CATEGORY:
                category = PLACE_TYPE_TO_CATEGORY[place_type]
                break

    # Extract rating and photo
    rating = place_details.get('rating')
    user_ratings_total = place_details.get('user_ratings_total', 0)
    photo_url = None
    if place_details.get('photos'):
        # Take the first photo reference and get its URL
        photo_reference = place_details['photos'][0]['photo_reference']
        photo_url = places_api_service.get_place_photo_url(photo_reference)

    # Default values for duration and description (can be improved with more sophisticated logic)
    default_durations = {
        'outdoor': 60, 'indoor': 90, 'temple': 45,
        'shopping': 60, 'museum': 90, 'food': 60,
        'sightseeing': 90
    }
    duration_minutes = default_durations.get(category, 60)
    
    # Generate a simple description if not available, incorporating rating
    description = place_details.get('formatted_address', '')
    if rating:
        description = f"{description}. Rating: {rating} ({user_ratings_total} reviews)."

    return Spot(
        name=name,
        name_en=name, # Using name as English name for simplicity
        city_id=city, # Assuming city name can act as city_id
        lat=lat,
        lon=lon,
        category=category,
        rating=rating,
        description=description,
        duration_minutes=duration_minutes,
        image_url=photo_url,
        # Add other fields as needed
    )

def _fetch_spots_from_places_api(city: str, query: str = "points of interest") -> List[Spot]:
    """Fetches spots for a city from Google Places API and converts them to Spot objects."""
    logger.info(f"Fetching spots for {city} from Google Places API...")
    spots_list = []
    
    # Find initial place_id for the city itself, to get its coordinates
    city_place_id = places_api_service.search_place_id(city)
    if not city_place_id:
        logger.warning(f"Could not find place ID for city: {city}")
        return []

    city_details = places_api_service.get_place_details(city_place_id)
    if not city_details or 'geometry' not in city_details:
        logger.warning(f"Could not get details or geometry for city: {city}")
        return []

    city_lat = city_details['geometry']['location']['lat']
    city_lon = city_details['geometry']['location']['lng']


    # Use Text Search to find points of interest within the city. 
    # The Text Search API is suitable for broad searches like "points of interest in London".
    # It returns a list of places. For each place, we then call Place Details.
    params = {
        "query": f"{query} in {city}",
        "location": f"{city_lat},{city_lon}",
        "radius": 50000, # Search within 50km radius
        "type": "tourist_attraction|museum|park|restaurant|shopping_mall" # Broad types
    }
    text_search_response = places_api_service._make_request("textsearch", params)
    
    if text_search_response and text_search_response.get('status') == 'OK':
        for place_summary in text_search_response.get('results', [])[:30]: # Limit to top 30 places
            place_id = place_summary.get('place_id')
            if place_id:
                place_details = places_api_service.get_place_details(place_id)
                if place_details:
                    spot = _convert_place_to_spot(place_details, city)
                    if spot:
                        spots_list.append(spot)
    else:
        logger.warning(f"Google Places Text Search failed for '{city}' with status: {text_search_response.get('status') if text_search_response else 'No response'}")

    return spots_list


@app.route('/api/spots/<city>', methods=['GET'])
@rate_limit(limit=30, window=60)  # 30 requests per minute
def get_spots(city):
    """
    API endpoint to get all available spots for a city.
    Used for populating the spot selection UI.
    Uses Redis cache to improve performance.
    """
    try:
        # Try to get from cache first
        cache_key = cache_key_for_spots(city)
        from agent.cache import get, set
        cached_spots = get(cache_key)
        
        if cached_spots is not None:
            logger.debug(f"Spots for {city} loaded from cache, count={cached_spots.get('total', 0)}")
            
            # Convert cached dicts back to Spot objects
            rehydrated_spots = [Spot(**s) for s in cached_spots['spots']]
            return success_response({"city": city, "spots": [s.to_dict() for s in rehydrated_spots], "total": len(rehydrated_spots)}, f"Loaded {len(rehydrated_spots)} spots for {city} (cached)")
        
        # Fetch from Google Places API
        spots = _fetch_spots_from_places_api(city)

        if not spots:
            return error_response(f"No live spot data found for city: {city}", 404, "City not found")
        
        # Calculate popularity score and sort (similar to old logic for consistent frontend display)
        def calculate_popularity_score(spot: Spot):
            base_rating = float(spot.rating) if spot.rating is not None else 3.0
            # Weights might need adjustment based on Places API data if categories are different
            # Keeping existing weights for now
            category_weights = {
                'sightseeing': 1.2, 'museum': 1.15, 'temple': 1.1,
                'outdoor': 1.05, 'shopping': 1.0, 'food': 0.95, 'indoor': 0.9
            }
            category_weight = category_weights.get(spot.category, 1.0)
            return round(base_rating * category_weight, 2)
        
        for spot in spots:
            spot.popularity_score = calculate_popularity_score(spot) # Add popularity as attribute
        
        spots.sort(key=lambda s: s.popularity_score, reverse=True)
        
        result = {
            "city": city,
            "spots": [s.to_dict() for s in spots], # Convert to dicts for JSON serialization
            "total": len(spots)
        }
        
        # Cache the result for 12 hours
        set(cache_key, result, ttl=43200)
        
        return success_response(result, f"Loaded {len(spots)} spots for {city}")
    
    except Exception as e:
        logger.error(f"Error in get_spots for city {city}: {traceback.format_exc()}")
        return error_response(str(e), 500, "Failed to load spots from Google Places API")

@app.route('/plan_itinerary', methods=['POST'])
@rate_limit(limit=5, window=60)  # 5 requests per minute (expensive operation)
def plan_itinerary():
    try:
        # Get request data
        data = request.json
        if not data:
            return error_response("Request body must be JSON", 400, "Invalid request")

        city = data.get('city')
        start_date = data.get('start_date')
        session_id = data.get('session_id')  # Get session ID from request
        
        logger.info(f"Planning itinerary for {city}, start_date={start_date}, days={data.get('days', 3)}")

        # Test required parameters; return errors if missing
        if not city:
            return error_response("Missing required parameter: 'city'", 400, "Validation error")
        if not start_date:
            return error_response("Missing required parameter: 'start_date'", 400, "Validation error")

        # Load spots for the city, now from Places API
        def load_spots(city: str) -> List[Spot]:
            # This internal load_spots will now call the Places API helper
            return _fetch_spots_from_places_api(city)

        try:
            spots = load_spots(city)

            if not spots:
                raise FileNotFoundError(f"No spot data found for city: {city}")

        except FileNotFoundError as e:
            # Optionally, fallback to static JSON if Places API fails for some spots 
            # For now, just raise the error.
            app.logger.warning(f"Places API did not return spots for {city}. Attempting fallback to static JSON...")
            base_dir = os.path.dirname(os.path.abspath(__file__))
            path = os.path.join(base_dir, f"data/spots_{city}.json")
            if os.path.exists(path):
                with open(path, encoding="utf-8") as f:
                    raw_static_spots = json.load(f)
                logging.warning(f"Loaded {len(raw_static_spots)} spots from static JSON for {city}")

                spots = []
                # Re-apply defaults as in the original load_spots
                default_durations = {
                    'outdoor': 60, 'indoor': 90, 'temple': 45,
                    'shopping': 60, 'museum': 90, 'food': 60, 'sightseeing': 90
                }
                for s_data in raw_static_spots:
                    spot = Spot(**s_data)
                    if getattr(spot, 'duration_minutes', None) is None:
                        spot.duration_minutes = default_durations.get(spot.category, 60)
                    spots.append(spot)

            else:
                return error_response(str(e), 404, "City not found (from Places API and static files)")

        except Exception as e:
            return error_response(f"Corrupted city data or Places API error: {str(e)}", 500, "Data loading error")
        
        # Store total available spots before filtering
        total_available_spots = len(spots)

        # Filter spots if user selected specific ones
        selected_spots = data.get('selected_spots')

        # Check for 'all selected' or 'subset selected'
        is_subset_selected = selected_spots and isinstance(selected_spots, list) and 
                             len(selected_spots) > 0 and len(selected_spots) < total_available_spots

        if is_subset_selected:
            # Case: A subset of spots is selected. Filter the spots list.
            selected_names = set(selected_spots)
            spots = [s for s in spots if s.name in selected_names]
            
            if not spots:
                return error_response(
                    "None of the selected spots were found in the city data", 
                    400, 
                    "Validation error"
                )
        
        # If is_subset_selected is False, it means either:
        # 1. selected_spots is falsy (None/empty list) -> "No spots selected"
        # 2. len(selected_spots) == total_available_spots -> "All spots selected"
        # In both these cases, we apply intelligent filtering if the dataset is large (total_available_spots > 20).
        is_all_or_none_selected = not is_subset_selected

        if is_all_or_none_selected and total_available_spots > 20:
            # No spots or all spots selected - intelligent filtering for large datasets
            # If there are too many spots, the itinerary planner might timeout or struggle.
            # We select top 20 most popular spots based on rating and category weights
            
            def calculate_popularity_score(spot):
                """计算景点受欢迎程度分数：评分 + 类别权重"""
                base_rating = float(spot.rating) if spot.rating is not None else 3.0
                
                # Category weights: some categories are naturally more popular
                category_weights = {
                    'sightseeing': 1.2,  # 观光
                    'museum': 1.15,      # 博物馆
                    'temple': 1.1,       # 寺庙/文化景点
                    'outdoor': 1.05,     # 户外景点
                    'shopping': 1.0,     # 购物
                    'food': 0.95,        # 美食（单独景点权重略低）
                    'indoor': 0.9        # 室内娱乐
                }
                category_weight = category_weights.get(spot.category, 1.0)
                
                return base_rating * category_weight
            
            # 按受欢迎程度排序
            spots.sort(key=calculate_popularity_score, reverse=True)
            spots = spots[:20]
            logger.info(f"Auto-selected top 20 most popular spots from {total_available_spots} available for {city}")
        
        # 配置评分标准
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

        # 计算所有模式的比较数据；支持用户选择天数
        days_param = data.get('days', 3)
        try:
            days_int = int(days_param)
            if days_int < 1 or days_int > 14:
                raise ValueError('days must be between 1 and 14')
        except Exception as e:
            return error_response(str(e), 400, 'Invalid days value')

        # Send initial progress
        if session_id:
            socketio.emit('planning_progress', {
                'progress': 5,
                'stage': '开始规划行程...',
                'message': f'正在为 {city} 加载景点数据'
            }, room=session_id)

        # read optional utility weights
        weights = data.get('weights', None)
        try:
            comparison_data = compare_transport_modes(
                city, spots, cfg, 
                days=days_int, 
                weights=weights,
                session_id=session_id
            )
        except Exception as e:
            return error_response(
                f"Failed to compare transport modes: {str(e)}",
                500,
                "Planning error"
            )
        
        # Send progress for weather calculation
        if session_id:
            socketio.emit('planning_progress', {
                'progress': 90,
                'stage': '获取天气信息...',
                'message': '正在为您准备最终建议'
            }, room=session_id)

        # 计算推荐模式的天气建议
        weather_msg = None
        if comparison_data['recommended_mode'] and comparison_data['recommended_data']:
            try:
                # start_date 可能是字符串，需转为 date
                if isinstance(start_date, str):
                    start_date_obj = date.fromisoformat(start_date)
                else:
                    start_date_obj = start_date

                # Reconstruct itinerary from recommended data for weather advice
                from agent.models import Itinerary, DayPlan
                recommended_itinerary = Itinerary(
                    city=city,
                    days=[
                        DayPlan(
                            day=day_data['day'],
                            spots=[
                                Spot(**spot)
                                for spot in comparison_data['recommended_data']['itinerary']
                            
                            ]
                        ) for day_data in comparison_data['recommended_data']['itinerary']
                    ]
                )
                weather_msg = weather_advice(recommended_itinerary, start_date_obj)
            except ValueError as e:
                return error_response(
                    f"Invalid date format: {str(e)}. Expected YYYY-MM-DD",
                    400,
                    "Date parsing error"
                )
            except Exception as e:
                # 天气建议失败不应该导致整个请求失败，但要记录原因
                weather_msg = None
                app.logger.warning(f"Weather advice generation failed: {str(e)}")

        # Send completion progress
        if session_id:
            socketio.emit('planning_progress', {
                'progress': 100,
                'stage': '完成！',
                'message': '行程规划已生成'
            }, room=session_id)

        # 返回比较结果
        response_data = {
            'comparison': comparison_data,
            'weather_advice': weather_msg,
        }

        return success_response(response_data, "Transport modes compared successfully")

    except Exception as e:
        # Catch-all for unexpected errors
        app.logger.error(f"Unexpected error in plan_itinerary: {traceback.format_exc()}")
        return error_response(
            f"Unexpected server error: {str(e)}",
            500,
            "Internal server error"
        )

+++++++ REPLACE
