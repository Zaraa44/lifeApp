from flask import Blueprint, render_template

main = Blueprint("main", __name__)

@main.route("/")
def dashboard():
    return render_template("index.html")

@main.route("/profile")
def profile():
    return render_template("profile.html")

@main.route("/kcal")
def kcal_page():
    return render_template("kcal.html")

@main.route("/workout")
def workout_page():
    return render_template("workout.html")

@main.route("/steps")
def steps_page():
    return render_template("steps.html")
