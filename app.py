from flask import Flask, render_template, request, jsonify
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

app = Flask(__name__)

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

def compare_transport_modes(city: str, spots: List[Spot], cfg: ScoreConfig) -> Dict:
    """
    Calculate itineraries for all transport modes and return comparison data.
    Returns structured data with all modes and recommendation.
    """
    modes = [TransportMode.WALK, TransportMode.TRANSIT, TransportMode.TAXI]
    results = {}

    best_mode = None
    best_score = float('inf')
    best_data = None

    for mode in modes:
        try:
            itinerary, score, reasons = plan_itinerary_soft_constraints(
                city=city,
                spots=spots,
                days=3,
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

    return {
        "modes": results,
        "recommended_mode": best_mode.value if best_mode else None,
        "recommended_data": best_data
    }

@app.route('/')
def index():
    # 返回首页，前端页面
    return render_template('index.html')

@app.route('/plan_itinerary', methods=['POST'])
def plan_itinerary():
    try:
        # 获取用户提交的数据
        data = request.json
        if not data:
            return error_response("Request body must be JSON", 400, "Invalid request")

        city = data.get('city')
        start_date = data.get('start_date')

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

        # 计算所有模式的比较数据
        try:
            comparison_data = compare_transport_modes(city, spots, cfg)
        except Exception as e:
            return error_response(
                f"Failed to compare transport modes: {str(e)}",
                500,
                "Planning error"
            )

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


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
