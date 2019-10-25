from datetime import datetime

from ..models import Database, Encryption


class BeUser(Database):

    def __init__(self):
        super().__init__()
        self.table_name = "be_user"
        self.encryption = Encryption()

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

    def validate_login(self, username, password):
        now = datetime.now()
        timestamp_now = datetime.timestamp(now)
        id = int(self.username_exists(username))
        if id > 0:
            self.set("id", id)
            self.load()
            stored_password = self.get("password")
            print(password)
            if self.encryption.validate_hash(stored_password, password):
                print("valid")
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
            print(self.arrData)
            self.save()
        return False
