from flask import render_template, request, flash, redirect, url_for, escape, abort
from . import backend
from .models import BeUser, FailedLoginRecord
from .forms import LoginForm, AddUserForm, EditUserForm
from flask_login import login_user, current_user, login_required, logout_user
from cryption_server import login_manager, nav

"""
 hauptnavigation
"""
nav.Bar('main', [
    nav.Item('Dashboard', 'backend.dashboard'),
    nav.Item('Backend Benutzer', '', items=[
        nav.Item('Übersicht', 'backend.be_user'),
        nav.Item('Benutzer hinzufügen', 'backend.be_user_add')
    ]),
    nav.Item('Benutzer', 'backend.user', items=[
        nav.Item('Benutzer hinzufügen', 'backend.user_add')
    ]),
    nav.Item('Logout', 'backend.logout')
])

"""
login endpunkt
"""


@backend.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm(request.form)
    if request.method == "POST":
        if form.validate_on_submit():
            be_user = BeUser()
            be_user.set("username", escape(request.form["username"]))
            be_user.temp_password = escape(request.form["password"])
            be_user.ip_address = escape(request.remote_addr)
            if be_user.validate_login():
                login_user(be_user)
            else:
                failed_login_record = FailedLoginRecord()
                failed_login_record.set("user_id", be_user.get_id())
                failed_login_record.set("username", be_user.get("username"))
                failed_login_record.set("ip_address", be_user.ip_address)
                failed_login_record.save()
            return redirect(url_for("backend.dashboard"))
        if form.username.errors:
            flash(form.username.errors, 'danger')
        if form.password.errors:
            flash(form.password.errors, 'danger')
    return render_template("/backend/login.html", form=form)


"""
benutzer editieren
"""


@backend.route("/be_user/edit_user/<int:user_id>", methods=["GET", "POST"])
@login_required
def be_user_edit(user_id):
    form = EditUserForm(request.form)
    be_user = current_user
    user = BeUser()
    if be_user.is_admin:
        if user_id > 0:
            user.set("id", user_id)
            user.load()
            form.username.data = user.get("username")
            form.password.data = ""
            form.email.data = user.get("email")
            form.ctrl_access_level.data = user.get("ctrl_access_level")
            form.ctrl_last_login.data = user.get("ctrl_last_login")
            form.ctrl_active.data = user.get("ctrl_active")
            form.activation_token.data = user.get("activation_token")
            form.ctrl_failed_logins.data = user.get("ctrl_failed_logins")
            form.ctrl_locked.data = user.get("ctrl_locked")
            form.ctrl_lockout_time.data = user.get("ctrl_lockout_time")
            form.ctrl_authenticated.data = user.get("ctrl_authenticated")
        if request.method == "POST" and form.validate_on_submit():
            be_user.temp_password = escape(request.form["user_password"])
            if be_user.validate_login():
                password = user.hash_password(escape(request.form["password"]))
                user.set("username", escape(request.form["username"]))
                user.set("password", password)
                user.set("email", escape(request.form["email"]))
                user.set("ctrl_access_level", escape(request.form["ctrl_access_level"]))
                user.set("ctrl_last_login", escape(request.form["ctrl_last_login"]))
                user.set("ctrl_active", escape(request.form["ctrl_active"]))
                user.set("activation_token", escape(request.form["activation_token"]))
                user.set("ctrl_failed_logins", escape(request.form["ctrl_failed_logins"]))
                user.set("ctrl_locked", escape(request.form["ctrl_locked"]))
                user.set("ctrl_lockout_time", escape(request.form["ctrl_lockout_time"]))
                user.set("ctrl_authenticated", escape(request.form["ctrl_authenticated"]))
                if user.save():
                    flash("Der Benutzer wurde erfolgreich aktualisiert", 'success')
                else:
                    flash("Der Benutzer konnte nicht aktualisiert werden", 'danger')
            else:
                flash("Sie haben ein falsches Passwort eingegeben", 'danger')
        if form.username.errors:
            flash(form.username.errors, 'danger')
        if form.password.errors:
            flash(form.password.errors, 'danger')
        if form.email.errors:
            flash(form.email.errors, 'danger')
        return render_template("backend/edit_user.html", form=form, user=user)
    return redirect(url_for("backend.dashboard"))


"""
benutzer hinzufügen
"""


@backend.route("/be_user/add_user", methods=["GET", "POST"])
@login_required
def be_user_add():
    form = AddUserForm(request.form)
    if request.method == "POST" and form.validate_on_submit():
        be_user = BeUser()
        username = escape(request.form["username"])
        password = escape(request.form["password"])
        email = escape(request.form["email"])
        token = be_user.generate_activation_token()
        password = be_user.hash_password(password)
        ctrl_access_level = int(request.form["ctrl_access_level"])
        be_user.set("username", username)
        be_user.set("password", password)
        be_user.set("email", email)
        be_user.set("activation_token", token)
        be_user.set("ctrl_access_level", ctrl_access_level)
        if be_user.register():
            flash("Der Benutzer wurde erfolgreich hinzugefügt", 'success')
        else:
            flash("Der Benutzer konnte nicht erstellt werden", 'danger')
    if form.username.errors:
        flash(form.username.errors, 'danger')
    if form.password.errors:
        flash(form.password.errors, 'danger')
    if form.email.errors:
        flash(form.email.errors, 'danger')
    return render_template("backend/add_user.html", form=form)


"""
dashboard ansicht
"""


@backend.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    user = current_user
    return render_template("/backend/dashboard.html", current_user=user)


"""
user loader
hier wird beim aufruf von login.required dekorierten punkten
der in der session gespeicherte benutzer geladen wenn vorhanden
"""


@login_manager.user_loader
def load_user(user_id):
    if user_id != "":
        user = BeUser()
        user.set("id", user_id)
        user.load()
        return user
    else:
        return None


@backend.route("/be_user", methods=["GET"])
@login_required
def be_user():
    user = current_user
    be_user = BeUser()
    be_users = be_user.list()
    return render_template("/backend/be_user.html", current_user=user, users=be_users)


@backend.route("/user", methods=["GET"])
@login_required
def user():
    user = current_user
    return render_template("/backend/dashboard.html", current_user=user)


@backend.route("/user/add_user", methods=["GET", "POST"])
@login_required
def user_add():
    user = current_user
    return render_template("/backend/dashboard.html", current_user=user)


@backend.route("/user/activate/<int:user_id>/<string:activation_token>", methods=["GET"])
def user_activate(user_id, activation_token):
    if user_id <= 0:
        abort(400)

    if len(activation_token) > 64 or len(activation_token) < 64:
        abort(401)

    be_user = BeUser()
    be_user.set("id", user_id)
    be_user.load()

    if not be_user.is_active:
        saved_activation_token = be_user.get("activation_token")
        if len(saved_activation_token) > 64 or len(saved_activation_token) < 64:
            abort(401)
        if saved_activation_token == activation_token:
            be_user.set("ctrl_active", 1)
            be_user.set("activation_token", be_user.generate_activation_token())
            be_user.save()
            flash("Dein Account wurde erfolgreich aktiviert", "success")
            return redirect(url_for("backend.login"))
    return "Aktivierung fehlgeschlagen"


@backend.route("/logout", methods=["GET"])
@login_required
def logout():
    user = current_user
    user.set("ctrl_authenticated", 0)
    user.save()
    if logout_user():
        return redirect(url_for("backend.login"))


@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for("backend.login"))
