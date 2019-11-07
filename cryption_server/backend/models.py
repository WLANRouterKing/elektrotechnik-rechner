#!/usr/bin/python
# -*- coding: utf-8 -*-
from datetime import datetime
from flask import flash, escape
from flask_login import UserMixin

from ..models import Database, SystemMail


class FailedLoginRecord(Database):

    def __init__(self):
        super().__init__()
        self.class_label = "Fehlgeschlagener Loginversuch"
        self.table_name = "failed_login_record"
        self.exclude_from_encryption.pop(1)


class SessionUser(UserMixin):
    username = ""
    last_login = ""
    admin = False
    moderator = False
    user = False
    active = False
    authenticated = False
    anonymous = False
    locked = False
    activation_token = False
    id = 0

    def get_id(self):
        return self.id

    @property
    def is_locked(self):
        return self.locked

    @property
    def is_admin(self):
        return self.admin

    @property
    def is_moderator(self):
        return self.moderator

    @property
    def is_user(self):
        return self.user

    @property
    def has_activation_token(self):
        return self.activation_token

    @property
    def is_active(self):
        return self.active

    @property
    def is_authenticated(self):
        return self.authenticated

    @property
    def is_anonymous(self):
        return self.anonymous

    def init_values(self, be_user):
        id = be_user.get_as_int("id")
        ctrl_access_level = be_user.get_as_int("ctrl_access_level")
        ctrl_active = be_user.get_as_int("ctrl_active")
        ctrl_authenticated = be_user.get_as_int("ctrl_authenticated")
        ctrl_locked = be_user.get_as_int("ctrl_locked")
        activation_token = be_user.get("activation_token")
        username = be_user.get("username")
        last_login = be_user.get("ctrl_last_login")

        self.last_login = last_login
        self.username = username
        self.id = id

        if len(activation_token) == 64:
            self.activation_token = True

        if ctrl_access_level == 10:
            self.admin = True
        elif ctrl_access_level == 5:
            self.moderator = True
        else:
            self.user = True

        if ctrl_active == 1:
            self.active = True

        if ctrl_authenticated == 1:
            self.authenticated = True

        if ctrl_locked == 1:
            self.locked = True


class BeUser(Database):

    def __init__(self):
        super().__init__()
        self.table_name = "be_user"
        self.temp_password = ""
        self.ip_address = ""
        self.exists = False
        self.settings = None

    def prepare_form_input(self, form_request):
        for key in form_request:
            for admin_column in self.column_admin_rights:
                if key not in self.filter_from_form_prepare:
                    data = escape(form_request[key])
                    if data == 'y':
                        data = 1
                    if key == admin_column:
                        if self.is_admin:
                            self.set(key, data)
                    else:
                        self.set(key, data)

    def get_username(self):
        return self.get("username")

    def get_password(self):
        return self.get("password")

    @property
    def is_locked(self):
        return bool(self.get("ctrl_locked"))

    @property
    def is_admin(self):
        return int(self.get("ctrl_access_level")) == 10

    @property
    def is_moderator(self):
        return int(self.get("ctrl_access_level")) == 5

    @property
    def is_user(self):
        return int(self.get("ctrl_access_level")) == 1

    @property
    def has_activation_token(self):
        return bool(self.get("activation_token"))

    @property
    def is_active(self):
        return bool(self.get("ctrl_active"))

    @property
    def is_authenticated(self):
        return bool(self.get("ctrl_authenticated"))

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return super().get_id()
        except AttributeError:
            raise NotImplementedError('No `id` attribute - override `get_id`')

    def generate_activation_token(self):
        return self.encryption.bin_2_hex(self.encryption.create_random_token(32))

    def hash_password(self, password):
        return self.encryption.hash_password(password)

    """
    login validieren
    erst wird überprüft ob der gegebene benutzername in der datenbank existiert
    danach wird das passwort geprüft
    wenn das passwort nicht korrekt ist ctrl_failed_login hochzählen
    wenn ctrl_failed_login > 3 ist -> account sperren für eine stunde und mail versenden
    """

    def validate_login(self):
        system_mail = SystemMail()
        datetime_now = datetime.now()
        password = self.temp_password
        if self.create_instance_by("username"):
            self.exists = True
        if self.is_locked:
            if self.get("ctrl_lockout_time") is not None:
                lockout_time = self.get("ctrl_lockout_time")
                difference = lockout_time.timestamp() - datetime_now.timestamp()
                if difference > 0:
                    flash("Ihr Account ist gesperrt", 'danger')
                else:
                    self.set("ctrl_locked", 0)
                    self.set("ctrl_lockout_time", None)
                    self.set("ctrl_failed_logins", 0)
        if self.exists:
            stored_password = self.get("password")
            print(stored_password)
            if self.encryption.validate_hash(stored_password, password):
                self.set("ctrl_last_login", datetime_now)
                self.set("ctrl_authenticated", 1)
                self.set("ip_address", self.ip_address)
                self.save()
                if True:
                    system_mail.send_be_user_login_message(self)
                return True
            else:
                failed_logins = self.get_as_int("ctrl_failed_logins")
                failed_logins = failed_logins + 1
                self.set("ctrl_failed_logins", failed_logins)
                if failed_logins >= 3:
                    # lockout time beträgt 1 stunde
                    time = datetime_now.timestamp()
                    timestamp = time + 3600
                    date = datetime.fromtimestamp(timestamp)
                    self.set("ctrl_locked", 1)
                    self.set("ctrl_failed_logins", 3)
                    self.set("ctrl_lockout_time", date)
                    self.set("ctrl_authenticated", False)
                    if True:
                        system_mail.send_be_user_lockout_message(self)
                self.save()
        flash("Login nicht erfolgreich", 'danger')
        return False

    def create_session_user(self):
        session_user = SessionUser()
        session_user.init_values(self)
        return session_user

    def register(self):
        system_mail = SystemMail()
        user_id = int(self.save())
        if user_id > 0:
            self.set("id", user_id)
            system_mail.send_be_user_activation_mail(self)
            return True
        return False
