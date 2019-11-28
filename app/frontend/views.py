from flask import render_template, request
from . import frontend


@frontend.route("/", methods=["GET", "POST"])
def home():
    return render_template("/frontend/home.html")


@frontend.track("/track", methods=["POST"])
def track():
    user_agent = request.args["user_agent"]
    ip_address = request.args["ip_address"]
    window_width = request.args["window_width"]
    window_height = request.args["window_height"]
    referrer = request.args["referrer"]
    return ""
