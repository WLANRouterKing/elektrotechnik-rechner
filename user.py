from datetime import datetime
import nacl.pwhash
from flask_login import UserMixin

from database import Database


class User(Database, UserMixin):

    def __init__(self):
        super().__init__()
        self.table_name = "user"

    def get_user_id_by_name(self, name):
        connection = self.get_connection()
        table = self.table_name
        sql = """SELECT id FROM {0} WHERE username = %s AND ctrl_active = 1""".format(table)
        cursor = connection.cursor(prepared=True)
        cursor.execute(sql, [name])
        result = []
        columns = tuple([str(d[0]) for d in cursor.description])
        for row in cursor:
            for v in row:
                try:
                    v.decode("utf-8")
                except:
                    pass
            result.append(dict(zip(columns, row)))
        cursor.close()
        connection.close()
        if len(result) > 0:
            return int(result[0]["id"])
        return 0

    def create_instance_by_user_id(self, id):
        connection = self.get_connection()
        table = self.table_name
        sql = """SELECT * FROM {0} WHERE id = %s""".format(table)
        cursor = connection.cursor(prepared=True)
        cursor.execute(sql, [id])
        result = []
        columns = tuple([str(d[0]) for d in cursor.description])
        for row in cursor:
            for v in row:
                try:
                    v.decode("utf-8")
                except:
                    pass
            result.append(dict(zip(columns, row)))
        cursor.close()
        connection.close()
        if len(result) > 0:
            self.arrData = result[0]
            return True
        return False

    def validate_login(self, password):
        stored_password = self.get("password")

        if nacl.pwhash.verify(bytes(stored_password), bytes(password.encode())):
            print("passwort ist richtig")
            self.set("last_login", datetime.now().strftime("%d.%m.%Y"))
            self.set("last_online", datetime.now().strftime("%d.%m.%Y"))
            print(self.arrData)
            self.save()
            return True

        return False
