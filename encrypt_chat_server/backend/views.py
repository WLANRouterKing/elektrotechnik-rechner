from flask import render_template, request, flash, redirect, url_for
from . import backend
from .models import BeUser
from .forms import LoginForm, RegisterForm
from flask_login import login_user, current_user, login_required
from encrypt_chat_server import login_manager


@backend.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if request.method == "POST":
        if form.validate_on_submit():
            be_user = BeUser()
            be_user.set("username", request.form["username"])
            be_user.set("password", request.form["password"])
            if be_user.validate_login():
                login_user(be_user)
                return redirect(url_for("backend.dashboard"))
            else:
                flash("Login nicht erfolgreich")
        if form.username.errors:
            flash(form.username.errors)
        if form.password.errors:
            flash(form.password.errors)
    return render_template("/backend/login.html", form=form)


@backend.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if request.method == "POST":
        if form.validate_on_submit():
            be_user = BeUser()
            username = request.form["username"]
            password = request.form["password"]
            email = request.form["email"]
            token = be_user.generate_activation_token()
            password = be_user.hash_password(password)
            be_user.set("username", username)
            be_user.set("password", password)
            be_user.set("email", email)
            be_user.set("activation_token", token)
            if be_user.save():
                flash("Registrierung erfolgreich. Bitte überprüfen Sie Ihr E-Mail Postfach.")
            else:
                flash("Registrierung fehlgeschlagen. Bitte erneut versuchen.")
        else:
            if form.username.errors:
                flash(form.username.errors)
            if form.password.errors:
                flash(form.password.errors)
            if form.email.errors:
                flash(form.email.errors)
    return render_template("/backend/register.html", form=form)


@backend.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    user = current_user
    print(user)
    return render_template("/backend/dashboard.html", current_user=user)


@login_manager.user_loader
def load_user(user_id):
    if user_id != "":
        user = BeUser()
        user.set("id", user_id)
        user.load()
        return user
    else:
        return None
