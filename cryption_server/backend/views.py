#!/usr/bin/python
# -*- coding: utf-8 -*-
import os

from flask import render_template, request, flash, redirect, url_for, escape, abort, make_response, current_app
from validate_email import validate_email
from werkzeug.utils import secure_filename

from cryption_server.models import SystemMail, Session, News
from . import backend
from .models import BeUser, FailedLoginRecord
from .forms import LoginForm, AddUserForm, EditUserForm, EditAccountForm, NewsEditorForm
from flask_login import login_user, current_user, login_required, logout_user
from cryption_server import login_manager, my_logger
from .nav import create_nav


@backend.route("/login", methods=["GET", "POST"])
def login():
    """
    Login Endpunkt

    Returns:
        Rendert das Login Template oder leitet an das Dashboard weiter nach erfolgreichem Login

    """
    form = LoginForm()
    if request.method == "POST":
        if form.validate_on_submit():
            be_user = BeUser()
            be_user.set("username", escape(request.form["username"]))
            be_user.temp_password = escape(request.form["password"])
            if be_user.validate_login():
                be_user.load()
                session = Session()
                session.set_user_id(be_user.get_id())
                if session.session_exists():
                    session.delete()
                    session = Session()
                    session.set_user_id(be_user.get_id())

                ip_address = escape(request.remote_addr)
                user_agent = escape(request.user_agent)
                token = session.encryption.create_random_token(32)

                session.set_ip_address(ip_address)
                session.set_user_agent(user_agent)
                session.set_token(token)
                session.set_timestamp(be_user.get_ctrl_last_login())

                if session.save() is not False:
                    session_user = be_user.create_session_user()
                    if login_user(session_user):
                        my_logger.log(10, "User mit der ID {0} eingeloggt".format(session_user.get_id()))
                        return redirect(url_for("backend.dashboard"))
            else:
                failed_login_record = FailedLoginRecord()
                failed_login_record.set_user_id(be_user.get_id())
                failed_login_record.set_username(be_user.get_username())
                failed_login_record.set_ip_address(request.remote_addr)
                failed_login_record.set_user_agent(request.user_agent)
                failed_login_record.save()
    return render_template("login.html", form=form)


@backend.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    """
     hauptnavigation

    """
    # erstellt die navigation in bezug auf die benutzerrechte
    create_nav()
    return render_template("dashboard.html")


"""
account editieren
"""


@backend.route("/account/edit", methods=["GET", "POST"])
@login_required
def account_edit():
    user_id = current_user.get_id()
    be_user = BeUser()
    be_user.set_id(user_id)
    be_user.load()
    form = EditAccountForm(request.form)
    if request.method == "GET":
        form.init_values(be_user)
    if request.method == "POST":
        if form.validate_on_submit():
            be_user.temp_password = escape(request.form["user_password"])
            if be_user.encryption.validate_hash(be_user.get_password(), be_user.temp_password):
                be_user.prepare_form_input(request.form)
                be_user.save()
            else:
                flash("Sie haben ein falsches Passwort eingegeben", "danger")
        else:
            form.get_error_messages()
    return render_template("account/edit_account.html", form=form)


@backend.route("/be_user/be_user_edit/<int:user_id>", methods=["GET", "POST"])
@login_required
def be_user_edit(user_id):
    """

    Args:
        user_id:

    Returns:

    """
    form = EditUserForm()
    user = BeUser()
    if user_id > 0:
        user.set("id", user_id)
        user.load()
    if request.method == "GET":
        if current_user.is_admin:
            form.init_values(user)
    if request.method == "POST":
        if form.validate_on_submit():
            be_user = BeUser()
            be_user.set_id(current_user.get_id())
            be_user.load()
            be_user.temp_password = escape(request.form["user_password"])
            if be_user.encryption.validate_hash(be_user.get_password(), be_user.temp_password):
                user.prepare_form_input(request.form)
                user.save()
            else:
                flash("Sie haben ein falsches Passwort eingegeben", 'danger')
        else:
            form.get_error_messages()
    return render_template("be_user/edit_be_user.html", form=form, user=user)


@backend.route("/be_user", methods=["GET"])
@login_required
def be_user():
    """

    Returns:

    """
    be_user = BeUser()
    be_users = be_user.object_list(be_user)
    return render_template("be_user/be_user.html", users=be_users)


@backend.route("/be_user/add_be_user", methods=["GET", "POST"])
@login_required
def be_user_add():
    """

    Returns:

    """
    form = AddUserForm(request.form)
    if current_user.is_admin:
        if request.method == "POST" and form.validate_on_submit():
            be_user = BeUser()
            username = escape(request.form["username"])
            password = escape(request.form["password"])
            email = escape(request.form["email"])
            token = be_user.generate_activation_token()
            password = be_user.hash_password(password)
            ctrl_access_level = int(request.form["ctrl_access_level"])
            be_user.set_username(username)
            be_user.set_password(password)
            be_user.set_email(email)
            be_user.set_activation_token(token)
            be_user.set_ctrl_access_level(ctrl_access_level)
            if validate_email(be_user.get_email(), verify=True):
                if be_user.register():
                    flash("Der Benutzer wurde erfolgreich hinzugefügt", 'success')
                else:
                    flash("Der Benutzer konnte nicht erstellt werden", 'danger')
            else:
                flash("Diese E-Mail Adresse scheint nicht zu existieren")
        return render_template("be_user/add_be_user.html", form=form)
    flash("Du hast nicht die benötigten Rechte", 'danger')
    return redirect(url_for("backend.dashboard"))


@backend.route("/failed_login_records", methods=["GET"])
@login_required
def failed_login_records():
    """

    Returns:

    """
    if current_user.is_moderator or current_user.is_admin:
        failed_login_record = FailedLoginRecord()
        failed_login_records = failed_login_record.object_list(failed_login_record)
        return render_template("system/failed_login_records.html", failed_login_records=failed_login_records)
    flash("Du hast nicht die benötigten Rechte", "danger")
    return redirect(url_for("backend.dashboard"))


@backend.route("/failed_login_records/delete/<int:id>", methods=["GET"])
@login_required
def failed_login_records_delete(id):
    """

    Args:
        id:

    Returns:

    """
    if current_user.is_admin:
        failed_login_record = FailedLoginRecord()
        failed_login_record.set("id", id)
        failed_login_record.delete()
    return redirect(url_for("backend.failed_login_records"))


@backend.route("/reports", methods=["GET"])
@login_required
def reports():
    """

    Returns:

    """
    if current_user.is_moderator or current_user.is_admin:
        return render_template("system/reports.html")
    flash("Du hast nicht die benötigten Rechte", "danger")
    return redirect(url_for("backend.dashboard"))


@backend.route("/system_mails", methods=["GET"])
@login_required
def system_mails():
    """

    Returns:

    """
    if current_user.is_moderator or current_user.is_admin:
        system_mail = SystemMail()
        system_mails = system_mail.object_list(system_mail)
        return render_template("system/system_mails.html", system_mails=system_mails)
    flash("Du hast nicht die benötigten Rechte", "danger")
    return redirect(url_for("backend.dashboard"))


@login_manager.user_loader
def load_user(user_id):
    """
    user loader
    hier wird beim aufruf von login.required dekorierten punkten
    der in der session gespeicherte benutzer geladen wenn vorhanden

    Args:
        user_id:

    Returns:

    """
    if user_id > 0:
        user = BeUser()
        user.set("id", user_id)
        user.load()
        session = Session()
        session.set_user_id(user.get_id())
        if session.load():
            session_user = user.create_session_user()
            session_user.ip_address = request.remote_addr
            session_user.user_agent = request.user_agent
            session_user.token = session.get_token()
            session_user.timestamp = session.get_timestamp()
            hash = session.get_user_hash_string(session_user.id, session_user.user_agent, session_user.ip_address, session_user.token, session_user.timestamp)
            if session.is_valid(session.encryption.get_generic_hash(hash)):
                return session_user
            else:
                session.delete()
    return None


@backend.route("/user", methods=["GET"])
@login_required
def user():
    """

    Returns:

    """
    return render_template("user/user.html")


@backend.route("/user/add_user", methods=["GET", "POST"])
@login_required
def user_add():
    """

    Returns:

    """
    return render_template("dashboard.html")


@backend.route("/user/activate/<int:user_id>/<string:activation_token>", methods=["GET"])
def user_activate(user_id, activation_token):
    """

    Args:
        user_id:
        activation_token:

    Returns:

    """
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
    flash("Aktivierung fehlgeschlagen", 'danger')
    return redirect(url_for("backend.login"))


@backend.route("/content/news", methods=["GET"])
@login_required
def news():
    """

    Returns:

    """
    return render_template("content/news/news.html")


@backend.route("/content/news/add_news/", methods=["GET", "POST"])
@backend.route("/content/news/add_news/<int:id>", methods=["GET", "POST"])
@login_required
def add_news(id=0):
    """

    Returns:

    """

    form = NewsEditorForm()
    news = News()
    news.set_id(id)
    news.load()

    if request.method == "GET":
        form.get_editor_edit_message(news)

    if id <= 0:
        news.init_default()
        news.save()
    else:
        if request.method == "POST" and form.validate_on_submit():
            news.prepare_form_input(request.form)
            news.save()
    return render_template("content/news/add_news.html", form=form, news=news)


@backend.route("/content/news/edit_news/<int:id>", methods=["GET", "POST"])
@login_required
def edit_news(id):
    """

    Returns:

    """
    return render_template("content/news/edit_news.html")


@backend.route("/logout", methods=["GET"])
@login_required
def logout():
    """

    Returns:

    """
    user = current_user
    session = Session()
    session.set_user_id(user.get_id())
    session.load()
    session.delete()
    if logout_user():
        flash("Erfolgreich abgemeldet", "success")
        return redirect(url_for("backend.login"))


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config["ALLOWED_IMAGE_EXTENSIONS"]


@backend.route("/ajax/image_upload", methods=["POST"])
@login_required
def image_upload():
    """

    Returns:

    """

    if "file" in request.files:
        file = request.files["file"]
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            type = escape(request.form["type"])
            module = escape(request.form["module"])
            base_upload_path = current_app.config["ROOT_DIR"] + "static/uploads/"
            final_upload_path = base_upload_path + type + "/" + module + "/"
            print(final_upload_path)
            if not os.path.isdir(final_upload_path):
                os.makedirs(final_upload_path)

            file.save(os.path.join(final_upload_path, filename))
            return filename
    return make_response(500)


@login_manager.unauthorized_handler
def unauthorized():
    """

    Returns:

    """
    return redirect(url_for("backend.login"))
