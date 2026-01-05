from flask import Blueprint, request, jsonify
from pathlib import Path
import json

profile_api = Blueprint("profile_api", __name__)

DATA_FILE = Path(__file__).parent.parent / "data" / "profile.json"


def read_profile():
    if not DATA_FILE.exists():
        return {}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def write_profile(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


@profile_api.route("/api/profile", methods=["GET"])
def get_profile():
    return jsonify(read_profile())


@profile_api.route("/api/profile", methods=["POST"])
def save_profile():
    data = request.json or {}

    profile = {
        "sex": data.get("sex"),
        "age": int(data.get("age", 0)),
        "height_cm": int(data.get("height_cm", 0))
    }

    write_profile(profile)
    return jsonify(profile)
