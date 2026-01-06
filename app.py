import os
from flask import Flask, jsonify, redirect, request, session, render_template

app = Flask(__name__)

app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret")

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.environ.get("GOOGLE_REDIRECT_URI")

@app.route("/")
def dashboard():
    return render_template("index.html")

@app.route("/steps")
def steps_page():
    return render_template("steps.html")

@app.route("/profile")
def profile_page():
    return render_template("profile.html")

@app.route("/api/health")
def health():
    return jsonify({"status": "ok"})

@app.route("/auth/login")
def login():
    return "Google login komt hier"

@app.route("/auth/callback")
def callback():
    return redirect("/")

