from database import Database


class KeyPair(Database):

    def __init__(self):
        super().__init__()
        self.table_name = "keypair"

    def get_private_key(self):
        return self.get("private_key")

    def get_public_key(self):
        return self.get("public_key")

    def set_private_key(self, value):
        self.set("private_key", value)

    def set_public_key(self, value):
        self.set("public_key", value)
