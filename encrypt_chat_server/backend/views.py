from flask import render_template, request, flash
from encrypt_chat_server.models import Encryption
from . import backend
from .forms import LoginForm


@backend.route("/login", methods=["GET", "POST"])
def login():
    encryption = Encryption()
    print(encryption.get_sym_key())
    form = LoginForm()
    if request.method == "POST":
        flash("Login nicht erfolgreich")
    return render_template("/backend/login.html", form=form)
