from flask import Flask, render_template, request, jsonify
from agent.planner import plan_itinerary_soft_constraints
from agent.geometry import TransportMode
from agent.constraints import ScoreConfig
from agent.models import Spot
import json
import os

app = Flask(__name__)

@app.route('/')
def index():
    # 返回首页，前端页面
    return render_template('index.html')

@app.route('/plan_itinerary', methods=['POST'])
def plan_itinerary():
    # 获取用户提交的数据
    data = request.json
    city = data.get('city')
    preference = data.get('preference')
    start_date = data.get('start_date')

    if not city or not preference or not start_date:
        return jsonify({"error": "Missing required parameters"}), 400

    # 根据偏好设置 transport mode
    preference_to_mode = {
        "walk": TransportMode.WALK,
        "transit": TransportMode.TRANSIT,
        "taxi": TransportMode.TAXI,
    }

    mode = preference_to_mode.get(preference)
    if not mode:
        return jsonify({"error": "Invalid preference value"}), 400

    # 加载 spots 数据
    def load_spots(city: str):
        path = f"data/spots_{city}.json"
        if not os.path.exists(path):
            raise FileNotFoundError(f"No spot data found for city: {city}")
        with open(path, encoding="utf-8") as f:
            return [Spot(**s) for s in json.load(f)]

    try:
        spots = load_spots(city)
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 404

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

    # 获取最佳行程
    itinerary, score, reasons = plan_itinerary_soft_constraints(
        city=city,
        spots=spots,
        days=3,
        cfg=cfg,
        mode=mode,
        trials=200,
    )

    # 将 Spot 对象转换为字典
    itinerary_dict = []
    for day in itinerary.days:
        day_dict = {
            "day": day.day,
            "spots": [spot.to_dict() for spot in day.spots]
        }
        itinerary_dict.append(day_dict)

    # 返回计划结果
    return jsonify({
        'score': score,
        'reasons': reasons,
        'itinerary': itinerary_dict,
    })

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
