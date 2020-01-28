from flask import render_template, request
from . import frontend
from ..models import Page
from .nav import create_nav

@frontend.route("/<string:page_eid>", methods=["GET", "POST"])
def page(page_eid):
    """

    Args:
        page_eid (string):

    Returns:

    """
    create_nav()
    page = Page()
    page.set_eid(page_eid)
    if page.create_instance_by("eid") is not False:
        if page.get_ctrl_template() == "start":
            return render_template("start.html", page=page)
        elif page.get_ctrl_template() == "standard":
            return render_template("standard.html", page=page)
    else:
        return render_template("404.html")


@frontend.route("/track", methods=["POST"])
def track():
    """

    Returns:

    """
    user_agent = request.args["user_agent"]
    ip_address = request.args["ip_address"]
    window_width = request.args["window_width"]
    window_height = request.args["window_height"]
    referer = request.args["referer"]
    return ""
