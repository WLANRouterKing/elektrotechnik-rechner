from datetime import datetime
from flask_login import UserMixin
from werkzeug.debug.repr import dump

from ..models import Database, Encryption


class BeUser(Database):

    def __init__(self):
        super().__init__()
        self.table_name = "be_user"
        self.encryption = Encryption()
        self.temp_username = ""
        self.temp_password = ""
        self.name = ""

    def load(self):
        super().load()
        self.name = self.get("username")

    @property
    def is_active(self):
        return bool(self.get("ctrl_active"))

    @property
    def is_authenticated(self):
        print(bool(self.get("ctrl_authenticated")))
        return bool(self.get("ctrl_authenticated"))

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return self.get("id")
        except AttributeError:
            raise NotImplementedError('No `id` attribute - override `get_id`')

    def send_activation_mail(self):
        return ""

    def send_lockout_mail(self):
        return ""

    def generate_activation_token(self):
        return self.encryption.bin_2_hex(self.encryption.create_random_token(32)).decode()

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
        now = datetime.now()
        timestamp_now = datetime.timestamp(now)
        username = self.temp_username
        password = self.temp_password
        id = int(self.username_exists(username))
        if id > 0:
            self.set("id", id)
            self.load()
            stored_password = self.get("password")
            if self.encryption.validate_hash(stored_password, password):
                self.set("ctrl_authenticated", 1)
                self.update()
                self.load()
                return True
        else:
            failed_logins = self.get("ctrl_failed_logins")
            failed_logins += 1
            print("failed_logins " + str(failed_logins))
            if failed_logins > 3:
                # lockout time beträgt 1 stunde
                lockout_time = timestamp_now + 3600
                self.set("ctrl_locked", 1)
                self.set("ctrl_failed_logins", 0)
                self.set("ctrl_lockout_time", lockout_time)
                self.set("ctrl_authenticated", False)
            self.save()
        return False
