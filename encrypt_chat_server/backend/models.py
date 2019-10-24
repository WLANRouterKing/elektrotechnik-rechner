from datetime import datetime

from ..models import Database, Encryption


class BeUser(Database):

    def __init__(self):
        super().__init__()
        self.table_name = "be_user"
        self.encryption = Encryption()

    def load(self):
        super().load()
        for key, value in self.arrData:
            print(key)
            print(value)

    def generate_activation_token(self):
        return self.encryption.bin_2_hex(self.encryption.create_random_token(32)).decode()

    def hash_password(self, password):
        return self.encryption.hash_password(password)

    def validate_login(self, password):
        stored_password = self.get("password")
        if self.encryption.validate_hash(bytes(stored_password), bytes(password.encode())):
            now = datetime.now()
            self.set("last_login", datetime.timestamp(now))
            self.save()
            return True

        return False
