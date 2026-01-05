from flask import Blueprint, request, jsonify
from datetime import datetime
import json
from pathlib import Path

weight_api = Blueprint("weight_api", __name__)

DATA_FILE = Path(__file__).parent.parent / "data" / "weight.json"


def read_weights():
    if not DATA_FILE.exists():
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def write_weights(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


@weight_api.route("/api/weight", methods=["GET"])
def get_latest_weight():
    data = read_weights()
    if not data:
        return jsonify(None)
    return jsonify(data[-1])


@weight_api.route("/api/weight", methods=["POST"])
def add_weight():
    payload = request.json
    weight = payload.get("weight")

    if weight is None:
        return {"error": "weight required"}, 400

    entry = {
        "weight": float(weight),
        "timestamp": datetime.now().isoformat(timespec="seconds")
    }

    data = read_weights()
    data.append(entry)
    write_weights(data)

    return jsonify(entry), 201
