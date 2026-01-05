
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from flask import Blueprint, redirect, request, session, jsonify, current_app
from google_auth_oauthlib.flow import Flow
import requests

google_fit = Blueprint("google_fit", __name__)

SCOPES = [
    "https://www.googleapis.com/auth/fitness.activity.read"
]


def get_flow():
    return Flow.from_client_config(
        {
            "web": {
                "client_id": current_app.config["GOOGLE_CLIENT_ID"],
                "client_secret": current_app.config["GOOGLE_CLIENT_SECRET"],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [
                    current_app.config["GOOGLE_REDIRECT_URI"]
                ]
            }
        },
        scopes=SCOPES,
        redirect_uri=current_app.config["GOOGLE_REDIRECT_URI"],
    )


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

    return jsonify({
        "date": start_of_day.date().isoformat(),
        "steps": total_steps,
        "timezone": str(tz),
        "source": "google_fit"
    })