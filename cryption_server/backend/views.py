from flask import render_template, request, flash, redirect, url_for, escape, abort
from validate_email import validate_email
from . import backend
from .models import BeUser, FailedLoginRecord
from .forms import LoginForm, AddUserForm, EditUserForm, EditAccountForm
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
    nav.Item('System', '', items=[
        nav.Item("Fehlgeschlagene Login Versuche", 'backend.failed_login_records'),
        nav.Item("System Mails", 'backend.system_mails'),
        nav.Item('Reports', 'backend.reports')
    ]),
    nav.Item('Account', '', items=[
        nav.Item("Account bearbeiten", 'backend.account_edit'),
        nav.Item("Account Einstellungen", 'backend.account_settings'),
        nav.Item('Logout', 'backend.logout')
    ])
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
                return redirect(url_for("backend.dashboard"))
            else:
                failed_login_record = FailedLoginRecord()
                failed_login_record.set("user_id", be_user.get_id())
                failed_login_record.set("username", be_user.get("username"))
                failed_login_record.set("ip_address", be_user.ip_address)
                failed_login_record.save()
        else:
            form.get_error_messages()
    return render_template("/backend/login.html", form=form)


"""
account editieren
"""


@backend.route("/account/settings", methods=["GET", "POST"])
@login_required
def account_settings():
    user = current_user
    form = EditAccountForm(request.form)
    if user.get_id():
        form.init_user_values(user)
    if request.method == "POST":
        if form.validate_on_submit():
            user.temp_password = escape(request.form["user_password"])
            if user.encryption.validate_hash(user.get("password"), user.temp_password):
                user.prepare_form_input(request.form)
                if user.save():
                    new_user = BeUser()
                    new_user.set("id", user.get_id())
                    new_user.load()
                    logout_user()
                    login_user(new_user)
                    flash("Accountdaten erfolgreich aktualisiert", "success")
                    return redirect(url_for("backend.account_edit"))
                else:
                    flash("Accountdaten konnten nicht aktualisiert werden")
    return render_template("/backend/account_edit.html", form=form)


"""
account editieren
"""


@backend.route("/account/edit", methods=["GET", "POST"])
@login_required
def account_edit():
    user = current_user
    form = EditAccountForm(request.form)
    if user.get_id():
        form.init_user_values(user)
    if request.method == "POST":
        if form.validate_on_submit():
            user.temp_password = escape(request.form["user_password"])
            if user.encryption.validate_hash(user.get("password"), user.temp_password):
                user.prepare_form_input(request.form)
                if user.save():
                    new_user = BeUser()
                    new_user.set("id", user.get_id())
                    new_user.load()
                    logout_user()
                    login_user(new_user)
                    flash("Accountdaten erfolgreich aktualisiert", "success")
                    return redirect(url_for("backend.account_edit"))
                else:
                    flash("Accountdaten konnten nicht aktualisiert werden")
    return render_template("/backend/account_edit.html", form=form)


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
            form.init_user_values(user)
        if request.method == "POST":
            if form.validate_on_submit():
                be_user.temp_password = escape(request.form["user_password"])
                if be_user.encryption.validate_hash(be_user.get("password"), be_user.temp_password):
                    if user.save():
                        flash("Der Benutzer wurde erfolgreich aktualisiert", 'success')
                    else:
                        flash("Der Benutzer konnte nicht aktualisiert werden", 'danger')
                else:
                    flash("Sie haben ein falsches Passwort eingegeben", 'danger')
            else:
                flash("Form konnte nicht validiert werden", 'danger')
                form.get_error_messages()
        return render_template("backend/edit_user.html", form=form, user=user)
    else:
        return redirect(url_for("backend.dashboard"))


"""
benutzer hinzufügen
"""


@backend.route("/be_user/add_user", methods=["GET", "POST"])
@login_required
def be_user_add():
    form = AddUserForm(request.form)
    user = current_user
    if user.is_admin:
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
            if validate_email(be_user.get("email"), verify=True):
                if be_user.register():
                    flash("Der Benutzer wurde erfolgreich hinzugefügt", 'success')
                else:
                    flash("Der Benutzer konnte nicht erstellt werden", 'danger')
            flash("Diese E-Mail Adresse scheint nicht zu existieren")
        if form.username.errors:
            flash(form.username.errors, 'danger')
        if form.password.errors:
            flash(form.password.errors, 'danger')
        if form.email.errors:
            flash(form.email.errors, 'danger')
        return render_template("backend/add_user.html", form=form)
    else:
        flash("Du hast nicht die benötigten Rechte", 'danger')
    return redirect(url_for("backend.dashboard"))


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
