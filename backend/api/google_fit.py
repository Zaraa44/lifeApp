import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from pathlib import Path
import json

from flask import Blueprint, redirect, request, session, jsonify, current_app
from google_auth_oauthlib.flow import Flow
import requests

google_fit = Blueprint("google_fit", __name__)

SCOPES = [
    "https://www.googleapis.com/auth/fitness.activity.read"
]


BASE_DIR = Path(__file__).parent.parent / "data"
PROFILE_FILE = BASE_DIR / "profile.json"
WEIGHT_FILE = BASE_DIR / "weight.json"
KCAL_FILE = BASE_DIR / "kcal_today.json"


def read_json(path, default):
    if not path.exists():
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def calculate_step_activity(steps, height_m, weight_kg, pace="average"):
    """
    Calories burned by steps using stride + pace + MET
    """

    PACES = {
        "slow": {
            "speed": 0.9,
            "met": 2.8
        },
        "average": {
            "speed": 1.34,
            "met": 3.5
        },
        "fast": {
            "speed": 1.79,
            "met": 5.0
        }
    }

    cfg = PACES[pace]

    stride = height_m * 0.414
    distance = stride * steps
    time_sec = distance / cfg["speed"]

    kcal = time_sec * cfg["met"] * 3.5 * weight_kg / (200 * 60)

    return {
        "type": "steps",
        "steps": steps,
        "pace": pace,
        "speed_m_s": cfg["speed"],
        "met": cfg["met"],
        "distance_km": round(distance / 1000, 2),
        "duration_min": round(time_sec / 60, 1),
        "kcal": round(kcal)
    }



def update_kcal_today(step_activity):
    today = datetime.now().date().isoformat()

    data = read_json(KCAL_FILE, {})

    if "date" not in data:
        data["date"] = today

    if "activities" not in data or not isinstance(data["activities"], dict):
        data["activities"] = {}

    if "workouts" not in data["activities"]:
        data["activities"]["workouts"] = []

    data["activities"]["steps"] = step_activity

    total = 0

    steps_activity = data["activities"].get("steps")
    if steps_activity:
        total += steps_activity.get("kcal", 0)

    for w in data["activities"]["workouts"]:
        total += w.get("kcal", 0)

    data["total_kcal"] = total
    data["date"] = today

    write_json(KCAL_FILE, data)

STEPS_HIST_FILE = BASE_DIR / "steps_hist.json"


def append_steps_history(date_str, steps):
    history = read_json(STEPS_HIST_FILE, [])

    if any(entry["date"] == date_str for entry in history):
        return

    history.append({
        "date": date_str,
        "steps": steps
    })

    history.sort(key=lambda x: x["date"])

    write_json(STEPS_HIST_FILE, history)

def fetch_steps_for_day(headers, tz, day):
    start = day.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=1)

    response = requests.post(
        "https://www.googleapis.com/fitness/v1/users/me/dataset:aggregate",
        headers=headers,
        json={
            "aggregateBy": [{
                "dataTypeName": "com.google.step_count.delta"
            }],
            "bucketByTime": {
                "durationMillis": 86400000
            },
            "startTimeMillis": int(start.timestamp() * 1000),
            "endTimeMillis": int(end.timestamp() * 1000)
        },
        timeout=10
    )

    response.raise_for_status()
    data = response.json()

    total = 0
    for bucket in data.get("bucket", []):
        for dataset in bucket.get("dataset", []):
            for point in dataset.get("point", []):
                value = point.get("value", [])
                if value:
                    total += value[0].get("intVal", 0)

    return total


def get_flow():
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
    redirect_uri = os.getenv("GOOGLE_REDIRECT_URI")

    if not client_id:
        raise RuntimeError("GOOGLE_CLIENT_ID ontbreekt")
    if not redirect_uri:
        raise RuntimeError("GOOGLE_REDIRECT_URI ontbreekt")

    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": client_id,
                "client_secret": client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [redirect_uri],
            }
        },
        scopes=SCOPES,
    )

    flow.redirect_uri = redirect_uri

    return flow

@google_fit.route("/api/google/status")
def google_status():
    return {
        "connected": "google_token" in session
    }


@google_fit.route("/auth/login")
def login():
    flow = get_flow()
    auth_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent"
    )
    session["state"] = state
    return redirect(auth_url)


@google_fit.route("/auth/callback")
def callback():
    flow = get_flow()
    flow.fetch_token(authorization_response=request.url)

    creds = flow.credentials

    session["google_token"] = {
        "access_token": creds.token,
        "refresh_token": creds.refresh_token,
        "expires_at": creds.expiry.timestamp()
    }

    return redirect("/")


@google_fit.route("/api/steps")
def get_steps():
    token_data = session.get("google_token")
    if not token_data:
        return redirect("/auth/login")

    headers = {
        "Authorization": f"Bearer {token_data['access_token']}"
    }

    tz = ZoneInfo("Europe/Amsterdam")
    now = datetime.now(tz)

    yesterday = now - timedelta(days=1)
    yesterday_date = yesterday.date().isoformat()

    steps_yesterday = fetch_steps_for_day(
        headers=headers,
        tz=tz,
        day=yesterday
    )

    append_steps_history(
        date_str=yesterday_date,
        steps=steps_yesterday
    )

    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + timedelta(days=1)

    start_ms = int(start_of_day.timestamp() * 1000)
    end_ms = int(end_of_day.timestamp() * 1000)

    response = requests.post(
        "https://www.googleapis.com/fitness/v1/users/me/dataset:aggregate",
        headers=headers,
        json={
            "aggregateBy": [
                {
                    "dataTypeName": "com.google.step_count.delta"
                }
            ],
            "bucketByTime": {
                "durationMillis": 86400000
            },
            "startTimeMillis": start_ms,
            "endTimeMillis": end_ms
        },
        timeout=10
    )

    response.raise_for_status()
    raw = response.json()

    total_steps = 0

    for bucket in raw.get("bucket", []):
        for dataset in bucket.get("dataset", []):
            for point in dataset.get("point", []):
                value = point.get("value", [])
                if value:
                    total_steps += value[0].get("intVal", 0)
    profile = read_json(PROFILE_FILE, {})
    weights = read_json(WEIGHT_FILE, [])

    if profile and weights:
        height_cm = profile.get("height_cm")
        weight_kg = weights[-1]["weight"]

        if height_cm and weight_kg:
            step_activity = calculate_step_activity(
                steps=total_steps,
                height_m=height_cm / 100,
                weight_kg=weight_kg,
                pace="average"
            )
            update_kcal_today(step_activity)

    return jsonify({
        "date": start_of_day.date().isoformat(),
        "steps": total_steps,
        "timezone": str(tz),
        "source": "google_fit"
    })


@google_fit.route("/api/kcal/today", methods=["GET"])
def get_kcal_today():
    from pathlib import Path
    import json

    path = Path(__file__).parent.parent / "data" / "kcal_today.json"

    if not path.exists():
        return jsonify({
            "total_kcal": 0,
            "activities": {}
        })

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return jsonify(data)



@google_fit.route("/api/steps/history")
def steps_history():
    return jsonify(read_json(STEPS_HIST_FILE, []))
