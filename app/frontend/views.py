from flask import render_template, request
from . import frontend


@frontend.route("/<string:page>", methods=["GET", "POST"])
def page(page):
    return render_template(page + ".html")


@frontend.route("/track", methods=["POST"])
def track():
    user_agent = request.args["user_agent"]
    ip_address = request.args["ip_address"]
    window_width = request.args["window_width"]
    window_height = request.args["window_height"]
    referer = request.args["referer"]
    return ""
