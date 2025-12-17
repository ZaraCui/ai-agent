from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from agent.planner import plan_itinerary_soft_constraints
from agent.geometry import TransportMode
from agent.geometry import travel_cost_minutes, distance as geo_distance
from agent.constraints import ScoreConfig
from agent.models import Spot
from agent.explainer import weather_advice
from datetime import date
import json
import os
import traceback
from typing import Dict, List, Tuple
from dotenv import load_dotenv
from flask_cors import CORS

# Load environment variables
load_dotenv()

app = Flask(__name__)
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
    return jsonify({
        "status": "error",
        "code": status_code,
        "message": message,
        "reason": reason
    }), status_code

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

@app.route('/plan_itinerary', methods=['POST'])
def plan_itinerary():
    try:
        # 获取用户提交的数据
        data = request.json
        if not data:
            return error_response("Request body must be JSON", 400, "Invalid request")

        city = data.get('city')
        start_date = data.get('start_date')
        session_id = data.get('session_id')  # Get session ID from request

        # 验证必需参数
        if not city:
            return error_response("Missing required parameter: 'city'", 400, "Validation error")
        if not start_date:
            return error_response("Missing required parameter: 'start_date'", 400, "Validation error")

        # 加载 spots 数据
        def load_spots(city: str):
            path = f"data/spots_{city}.json"
            if not os.path.exists(path):
                raise FileNotFoundError(f"No spot data found for city: {city}")
            with open(path, encoding="utf-8") as f:
                raw = json.load(f)

            # default durations by category (minutes)
            default_durations = {
                'outdoor': 60,
                'indoor': 90,
                'temple': 45,
                'shopping': 60,
                'museum': 90,
                'food': 60,
            }

            # default ratings by category (0-5)
            default_ratings = {
                'outdoor': 4.2,
                'indoor': 4.3,
                'temple': 4.1,
                'shopping': 3.9,
                'museum': 4.5,
                'food': 4.0,
            }

            # short explanation templates by category
            explanation_templates = {
                'outdoor': 'Popular outdoor attraction with scenic views and good photo opportunities.',
                'indoor': 'Well-curated indoor spot; expect exhibits or sheltered activities.',
                'temple': 'Historic or religious site, usually quiet and culturally significant.',
                'shopping': 'Shopping area with stores and local vendors; good for browsing.',
                'museum': 'High-quality museum with notable collections; allow more time.',
                'food': 'Recommended local food spot; good for meals and tasting local cuisine.',
            }

            spots = []
            for s in raw:
                spot = Spot(**s)
                if getattr(spot, 'duration_minutes', None) is None:
                    spot.duration_minutes = default_durations.get(spot.category, 60)
                if getattr(spot, 'rating', None) is None:
                    spot.rating = default_ratings.get(spot.category, 4.0)
                # provide a concise description that also explains the rating
                if not getattr(spot, 'description', None):
                    base_expl = explanation_templates.get(spot.category, 'Popular attraction')
                    spot.description = f"{base_expl} Typical visit ~{spot.duration_minutes} minutes. Rating based on typical visitor feedback." 
                spots.append(spot)

            return spots

        try:
            spots = load_spots(city)
        except FileNotFoundError as e:
            return error_response(str(e), 404, "City not found")
        except json.JSONDecodeError as e:
            return error_response(f"Corrupted city data: {str(e)}", 500, "Data loading error")

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
                            spots=[Spot(**spot) for spot in day_data['spots']]
                        )
                        for day_data in comparison_data['recommended_data']['itinerary']
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


# ===== Error handlers =====
@app.errorhandler(400)
def bad_request(e):
    return error_response(str(e.description) if hasattr(e, 'description') else "Bad request", 400, "Bad request")


@app.errorhandler(404)
def not_found(e):
    return error_response("Endpoint not found", 404, "Not found")


@app.errorhandler(405)
def method_not_allowed(e):
    return error_response("Method not allowed for this endpoint", 405, "Method not allowed")


@app.errorhandler(500)
def internal_error(e):
    app.logger.error(f"Internal server error: {traceback.format_exc()}")
    return error_response("Internal server error occurred", 500, "Internal server error")


# ===== Directions proxy (server-side) =====
def _decode_polyline(polyline_str):
    # Decodes a Google encoded polyline into list of (lat, lng)
    index, lat, lng = 0, 0, 0
    coordinates = []
    length = len(polyline_str)

    while index < length:
        result, shift = 0, 0
        while True:
            b = ord(polyline_str[index]) - 63
            index += 1
            result |= (b & 0x1f) << shift
            shift += 5
            if b < 0x20:
                break
        dlat = ~(result >> 1) if (result & 1) else (result >> 1)
        lat += dlat

        result, shift = 0, 0
        while True:
            b = ord(polyline_str[index]) - 63
            index += 1
            result |= (b & 0x1f) << shift
            shift += 5
            if b < 0x20:
                break
        dlng = ~(result >> 1) if (result & 1) else (result >> 1)
        lng += dlng

        coordinates.append([lat / 1e5, lng / 1e5])

    return coordinates


@app.route('/api/directions', methods=['POST'])
def directions_proxy():
    try:
        data = request.json
        if not data:
            return error_response('Request body must be JSON', 400, 'Invalid request')

        google_key = os.environ.get('GOOGLE_MAPS_API_KEY')
        if not google_key:
            return error_response('Server missing GOOGLE_MAPS_API_KEY', 500, 'Configuration error')

        itinerary = data.get('itinerary', [])
        mode = data.get('mode', 'driving')
        allowed = {'driving', 'walking', 'bicycling', 'transit'}
        if mode not in allowed:
            mode = 'driving'

        results = []
        for day in itinerary:
            day_idx = day.get('day')
            spots = day.get('spots', [])
            # normalize spot lat/lng keys
            coords = []
            for s in spots:
                lat = s.get('lat') if isinstance(s, dict) else getattr(s, 'lat', None)
                lon = s.get('lon') if isinstance(s, dict) else getattr(s, 'lon', None)
                if lat is None:
                    lat = s.get('latitude') if isinstance(s, dict) else None
                if lon is None:
                    lon = s.get('lng') if isinstance(s, dict) else None
                if lat is not None and lon is not None:
                    coords.append((float(lat), float(lon)))

            if len(coords) < 2:
                results.append({'day': day_idx, 'coords': []})
                continue

            origin = f"{coords[0][0]},{coords[0][1]}"
            destination = f"{coords[-1][0]},{coords[-1][1]}"
            waypoints = []
            if len(coords) > 2:
                # build intermediate waypoints (avoid too many waypoints)
                mid = coords[1:-1]
                waypoints = [f"{p[0]},{p[1]}" for p in mid[:23]]

            params = {
                'origin': origin,
                'destination': destination,
                'key': google_key,
                'mode': mode,
                'units': 'metric',
            }
            if waypoints:
                params['waypoints'] = '|'.join(waypoints)

            resp = requests.get('https://maps.googleapis.com/maps/api/directions/json', params=params, timeout=10)
            payload = resp.json()
            if payload.get('status') != 'OK' or not payload.get('routes'):
                results.append({'day': day_idx, 'coords': []})
                continue

            over = payload['routes'][0].get('overview_polyline', {}).get('points')
            if not over:
                results.append({'day': day_idx, 'coords': []})
                continue

            decoded = _decode_polyline(over)
            results.append({'day': day_idx, 'coords': decoded})

        return success_response({'routes': results}, 'Directions fetched')

    except Exception as e:
        app.logger.error(f"Directions proxy failed: {traceback.format_exc()}")
        return error_response(f"Directions proxy failed: {str(e)}", 500, 'Directions error')

# ===== WebSocket event handlers =====
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print(f'Client connected: {request.sid}')

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print(f'Client disconnected: {request.sid}')

@socketio.on('join_session')
def handle_join_session(data):
    """Allow client to join a specific session room"""
    session_id = data.get('session_id')
    if session_id:
        from flask_socketio import join_room
        join_room(session_id)
        emit('session_joined', {'session_id': session_id})
        print(f'Client {request.sid} joined session {session_id}')

# ===== Application entry point =====
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    # Use socketio.run instead of app.run
    socketio.run(
        app, 
        host='0.0.0.0', 
        port=port, 
        debug=os.environ.get('FLASK_DEBUG', 'False') == 'True',
        allow_unsafe_werkzeug=True
    )


if __name__ == "__main__":
    # For production deployment
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)
