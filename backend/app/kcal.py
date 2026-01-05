from flask import Blueprint, request, jsonify
from pathlib import Path
import json

kcal_api = Blueprint("kcal_api", __name__)


@kcal_api.route("/api/kcal/today", methods=["GET"])
def get_kcal_today():
    from pathlib import Path
    import json

    path = Path(__file__).parent.parent / "data" / "kcal_today.json"

    if not path.exists():
        return jsonify({"total_kcal": 0})

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return jsonify({
        "date": data.get("date"),
        "total_kcal": data.get("total_kcal", 0)
    })
