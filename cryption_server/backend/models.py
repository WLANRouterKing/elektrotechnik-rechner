from datetime import datetime
from re import search

from flask import flash, escape
from ..models import Database, SystemMail


class FailedLoginRecord(Database):

    def __init__(self):
        super().__init__()
        self.table_name = "failed_login_record"
        self.exclude_from_encryption.pop(1)


class BeUserSettings(Database):

    def __int__(self):
        super().__init__()
        self.table_name = "be_user_settings"

    @property
    def send_lockout_notification(self):
        return bool(self.get("ctrl_send_lockout_notification"))

    @property
    def send_login_notification(self):
        return bool(self.get("ctrl_send_login_notification"))

    @property
    def send_failed_login_notification(self):
        return bool(self.get("ctrl_send_failed_login_notification"))


class BeUser(Database):

    def __init__(self):
        super().__init__()
        self.table_name = "be_user"
        self.temp_password = ""
        self.ip_address = ""
        self.exists = False
        self.settings = None

    def load(self):
        super().load()
        self.settings = BeUserSettings()
        # buggt wenn klasse innerhalb einer klasse erstellt wird
        self.settings.table_name = "be_user_settings"
        self.settings.set("user_id", self.get_id())
        self.settings.load()

    def prepare_form_input(self, form_request):
        for key in form_request:
            for admin_column in self.column_admin_rights:
                if key not in self.filter_from_form_prepare:
                    data = escape(form_request[key])
                    if data == 'y':
                        data = 1
                    print(key)
                    print(data)
                    if key == admin_column:
                        if self.is_admin:
                            self.set(key, data)
                    else:
                        self.set(key, data)

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

    def list(self):
        list_id = super().list()
        final_list = list()
        for id in list_id:
            be_user = BeUser()
            be_user.set("id", id)
            be_user.load()
            final_list.append(be_user)
        return final_list

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
                if self.settings.send_login_notification:
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
                    self.set("ctrl_failed_logins", 0)
                    self.set("ctrl_lockout_time", date)
                    self.set("ctrl_authenticated", False)
                    if self.settings.send_lockout_notification:
                        system_mail.send_be_user_lockout_message(self)
                self.save()
        flash("Login nicht erfolgreich", 'danger')
        return False

    def register(self):
        system_mail = SystemMail()
        user_id = int(self.save())
        if user_id > 0:
            self.set("id", user_id)
            system_mail.send_be_user_activation_mail(self)
            return True
        return False
