from flask import render_template, request, flash

from . import backend
from .forms import LoginForm


@backend.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if request.method == "POST":
        flash("Login nicht erfolgreich")
    return render_template("/backend/login.html", form=form)
