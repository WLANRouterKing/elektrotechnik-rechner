from flask import render_template, request
from . import frontend
from ..models import Page
from .nav import create_nav


@frontend.route("/", methods=["GET", "POST"])
def start_page():
    """

    """
    create_nav()

    page = Page()
    start_page = page.get_start_page()
    if start_page is not None:
        return render_template("start.html", page=start_page)
    else:
        return render_template('404.html', title='404'), 404


@frontend.route("/<string:page_eid>", methods=["GET", "POST"])
def page(page_eid):
    """

    Args:
        page_eid (string):

    Returns:

    """
    create_nav()

    page = Page()

    if page_eid != 'favicon.ico':
        page.set_eid(page_eid)
        if page.create_instance_by("eid") is not False:
            if page.get_ctrl_template() == "start":
                return render_template("start.html", page=page)
            elif page.get_ctrl_template() == "standard":
                return render_template("standard.html", page=page)
        elif page.get_start_page() is not None:
            start_page = page.get_start_page()
            print(start_page.arrData)
            return render_template("start.html", page=start_page)
    return render_template('404.html', title='404'), 404


@frontend.errorhandler(404)
def page_not_found(error):
    return render_template('404.html', title='404'), 404


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
