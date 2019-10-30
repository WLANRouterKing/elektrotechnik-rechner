from flask import render_template
from . import frontend


@frontend.route("/", methods=["GET", "POST"])
def home():
    return render_template("/frontend/home.html")
