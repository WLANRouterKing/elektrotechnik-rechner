from re import search
import mysql.connector
import copy
from flask import jsonify, current_app, url_for, flash
import nacl.utils
import nacl.secret
import nacl.encoding
import nacl.pwhash
from flask_login import current_user
from nacl import encoding
from nacl.public import PrivateKey
from cryption_server import Mail
from flask_mail import Message
from cryption_server import my_logger


class Encryption:

    def create_random_token(self, length):
        return nacl.utils.random(length)

    def bin_2_hex(self, value):
        return nacl.encoding.HexEncoder.encode(value).decode('utf-8')

    def hex_2_bin(self, value):
        return nacl.encoding.HexEncoder.decode(value)

    def create_sym_key(self):
        return self.bin_2_hex(self.create_random_token(nacl.secret.SecretBox.KEY_SIZE))

    """
    liefert den schlüssel zum symmetrischen verschlüsseln
    """

    def get_sym_key(self):
        return self.hex_2_bin(current_app.config["SYM_KEY"])

    """
    symmetrische verschlüsselungsmethode
    """

    def encrypt(self, data):
        try:
            box = nacl.secret.SecretBox(self.get_sym_key())
            data_encrypted = box.encrypt(bytes(data, encoding="utf-8"), nonce=None, encoder=encoding.Base64Encoder)
            return data_encrypted.decode('utf-8')
        except Exception as error:
            my_logger.log(10, error)
        return data

    """
    symmetrische entschlüsselungsmethode
    """

    def decrypt(self, data):
        try:
            box = nacl.secret.SecretBox(self.get_sym_key())
            data_decrypted = box.decrypt(bytes(data, encoding="utf-8"), nonce=None, encoder=encoding.Base64Encoder)
            return data_decrypted.decode('utf-8')
        except Exception as error:
            my_logger.log(10, error)
        return data

    """
    liefert einen password hash zurück (argon2id)
    """

    def hash_password(self, password):
        return nacl.pwhash.argon2id.str(password.encode())

    def validate_hash(self, hash_string, string):
        try:
            print(hash_string)
            print(string)
            if nacl.pwhash.verify(bytes(hash_string, encoding="utf8"), bytes(string, encoding="utf8")):
                return True
        except Exception as error:
            my_logger.log(10, error)
            pass
        return False

    def as_base_64(self, data):
        return nacl.encoding.Base64Encoder.encode(data)

    def get_key_pair(self):
        secret_key = PrivateKey.generate()
        public_key = secret_key.public_key
        public_key_encrypted = self.encrypt(public_key.encode(encoder=encoding.RawEncoder))
        private_key_encrypted = self.encrypt(secret_key.encode(encoder=encoding.RawEncoder))
        key_pair = KeyPair()
        key_pair.set_private_key(private_key_encrypted)
        key_pair.set_public_key(public_key_encrypted)
        return key_pair


class Database:
    """
    init funktion setzt tabellen namen, system objekt, arrData und initialisiert die datenbankverbindung
    """

    def __init__(self):
        self.encryption = Encryption()
        self.class_label = ""
        self.table_name = ""
        self.arrData = dict()
        self.put_into_trash = True
        self.exclude_from_encryption = ["id", "username", "user_id", "ctrl"]
        self.column_admin_rights = ["ctrl_access_level"]
        self.filter_from_form_prepare = ["password", "csrf_token", "user_password", "submit"]

    """
    generische get funktion -> muss zur sicherheit noch ergänzt werden
    """

    def get(self, key):
        if key in self.arrData:
            return self.arrData[key]
        else:
            return ""

    """
    generische set funktion -> muss zur sicherheit noch ergänzt werden
    """

    def set(self, key, value):
        self.arrData[key] = value

    def get_id(self):
        id = self.get("id")
        if id == "":
            id = 0
        return int(id)

    def get_user_id(self):
        user_id = self.get("user_id")
        if user_id == "":
            user_id = 0
        return int(user_id)

    def get_as_int(self, key):
        string = self.get(key)
        if string != "":
            integer = int(string)
            return integer
        return 0

    """
    gibt ein MySQLConnection Objekt zurück
    """

    def get_connection(self):
        host = current_app.config["DATABASE_HOST"]
        name = current_app.config["DATABASE_NAME"]
        user = current_app.config["DATABASE_USER"]
        password = current_app.config["DATABASE_PASSWORD"]
        return mysql.connector.connect(host=host, database=name, user=user,
                                       password=password)

    """
    lädt einen datensatz anhand der id oder user_id aus der datenbank
    ist keine id angegeben wird die komplette tabelle geladen
    """

    def load(self):
        connection = self.get_connection()
        cursor = connection.cursor()
        table = self.table_name
        id = 0
        sql = ""
        if self.get_id() > 0:
            id = self.get_id()
            sql = """SELECT * FROM {0} WHERE id = %s""".format(table)
        elif self.get_user_id() > 0:
            id = self.get_user_id()
            sql = """SELECT * FROM {0} WHERE user_id = %s""".format(table)
        try:
            if id > 0:
                cursor = connection.cursor(prepared=True)
                cursor.execute(sql, [id])
                result = dict()
                columns = tuple([str(d[0]) for d in cursor.description])
                for row in cursor:
                    result = dict(zip(columns, row))
                self.arrData = result
                for key in self.arrData:
                    try:
                        if isinstance(self.get(key), bytearray):
                            self.set(key, self.get(key).decode('utf-8'))
                    except Exception as error:
                        my_logger.log(10, error)
                        pass
                self.decrypt_data()
                return True
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

        return False

    """
    generische update funktion
    verarbeitet die key,value pairs aus arrData in ein prepared statement mit platzhaltern
    und führt danach die query aus
    """

    def update(self):
        connection = self.get_connection()
        cursor = connection.cursor(prepared=True)
        try:
            table = self.table_name
            id = self.get("id")
            data = self.encrypt_data()
            for key in data:
                try:
                    if isinstance(data[key], bytearray):
                        data[key] = data[key].decode('utf-8')
                except Exception as error:
                    my_logger.log(10, error)
                    pass
            update_string = ""
            columns = data.keys()
            max_keys = len(data.keys())
            i = 1
            for column in columns:
                update_string += column
                update_string += " = "
                update_string += " %s"
                if i < max_keys:
                    update_string += ", "
                i += 1
            data["last_id"] = id
            values = list(data.values())
            sql = """UPDATE {0} SET {1} WHERE id = %s """.format(table, update_string)
            cursor.execute(sql, values)
            rows = cursor.rowcount
            connection.commit()
            if rows > 0:
                return True
        except Exception as error:
            my_logger.log(10, error)
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

        return False

    """
    generische insert methode
    verarbeitet die key,value pairs aus arrData in ein prepared statement mit platzhaltern
    und führt danach die query aus
    """

    def insert(self):
        connection = self.get_connection()
        cursor = connection.cursor(prepared=True)
        try:
            table = self.table_name
            data = self.encrypt_data()
            columns = ','.join(data.keys())
            placeholders = ','.join(['%s'] * len(data))
            values = list(data.values())
            sql = """INSERT INTO {0} ({1}) VALUES ({2});""".format(table, columns, placeholders)
            cursor.execute(sql, values)
            row = cursor.lastrowid
            connection.commit()
            if row > 0:
                return row
        except Exception as error:
            my_logger.log(10, error)
        finally:
            if connection.is_connected:
                cursor.close()
                connection.close()
        return False

    def delete(self):
        connection = self.get_connection()
        cursor = connection.cursor(prepared=True)
        success = False
        table = self.table_name
        id = self.get_id()
        if id > 0:
            try:
                if self.put_into_trash:
                    sql = """UPDATE {0} SET ctrl_deleted = 1 WHERE id = %s;""".format(table)
                    trash = Trash()
                    trash.set("item_id", id)
                    trash.set("item_table", table)
                    trash.set("user_id", current_user.get_id())
                    if trash.save():
                        flash("""{0} mit der ID {1} erfolgreich in den Papierkorb verschoben""".format(self.class_label, id), "success")
                    else:
                        flash("""{0} mit der ID {1} konnte nicht in den Papierkorb verschoben werden""".format(self.class_label, id), "danger")
                else:
                    sql = """DELETE FROM {0} WHERE id = %s;""".format(table)
                cursor.execute(sql, [id])
                connection.commit()
                row = cursor.lastrowid

                if row > 0 and not self.put_into_trash:
                    flash("""{0} mit der ID {1} erfolgreich gelöscht""".format(self.class_label, id), "success")
                elif row <= 0 and not self.put_into_trash:
                    flash("""{0} mit der ID {1} konnte nicht gelöscht werden""".format(self.class_label, id), "danger")
                if row > 0:
                    success = True
            except Exception as error:
                my_logger.log(10, error)
            finally:
                if connection.is_connected():
                    cursor.close()
                    connection.close()
        return success

    def id_list(self, sql_where):
        connection = self.get_connection()
        cursor = connection.cursor()
        self.list = list()
        try:
            table = self.table_name
            if len(sql_where) > 0:
                sql = """SELECT id FROM {0} WHERE %s""".format(table)
                if self.put_into_trash:
                    sql += " AND ctrl_deleted = 0 "
                cursor.execute(sql, [sql_where])
            else:
                sql = """SELECT id FROM {0} """.format(table)
                if self.put_into_trash:
                    sql += " WHERE ctrl_deleted = 0 "
                cursor.execute(sql)
            rows = cursor.fetchall()
            for row in rows:
                if row[0]:
                    self.list.append(row[0])
        except Exception as error:
            my_logger.log(10, error)
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
        return self.list

    def object_list(self, object=None, sql_where=""):
        list_id = self.id_list(sql_where)
        final_list = list()
        for id in list_id:
            # objekt kopieren
            single_object = copy.copy(object)
            single_object.set("id", id)
            single_object.load()
            final_list.append(single_object)
        return final_list

    def encrypt_data(self):
        data = dict()
        for key in self.arrData:
            value = self.arrData[key]
            key_encryptable = True
            for exclude in self.exclude_from_encryption:
                if search(exclude, key) is not None:
                    key_encryptable = False
            if key_encryptable:
                data[key] = self.encryption.encrypt(value)
            else:
                data[key] = value
        return data

    def decrypt_data(self):
        for key in self.arrData:
            key_decryptable = True
            for exclude in self.exclude_from_encryption:
                if search(exclude, key) is not None:
                    key_decryptable = False
            if key_decryptable:
                self.set(key, self.encryption.decrypt(self.get(key)))

    """
    generische speicher methode anhand der id wird überprüft ob der datensatz aus der Datenbank
    geladen wurde. Wenn dem so ist sollte die id > 0 sein und somit wird ein update() ausgeführt
    andernfalls wird insert() aufgerufen
    """

    def save(self):
        if self.get_id() > 0:
            return self.update()
        else:
            return self.insert()

    def get_json_response(self):
        return jsonify(self.arrData)

    def create_instance_by_id(self, id):
        if id <= 0:
            return False
        self.set("id", id)
        self.load()
        return True

    def create_instance_by(self, key="username"):
        connection = self.get_connection()
        cursor = connection.cursor(prepared=True)
        rows = None
        try:
            value = self.get(key)
            if value == "":
                return False
            table = self.table_name
            sql = """SELECT id FROM {0} WHERE {1} = %s""".format(table, key)
            cursor.execute(sql, [value])
            rows = cursor.fetchone()
        except Exception as error:
            my_logger.log(10, error)
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
        if rows is not None:
            id = rows[0]
            if id > 0:
                self.set("id", id)
                self.load()
                return True
        return False

    def username_exists(self, name):
        connection = self.get_connection()
        cursor = connection.cursor(prepared=True)
        rows = None
        try:
            table = self.table_name
            sql = """SELECT id FROM {0} WHERE username = %s""".format(table)
            cursor.execute(sql, [name])
            rows = cursor.fetchone()
        except Exception as error:
            my_logger.log(10, error)
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
        if rows is not None:
            return rows[0]
        return 0


class SystemMail(Database):

    def __init__(self):
        super().__init__()
        self.table_name = "system_mail"
        self.set_sender(current_app.config["MAIL_DEFAULT_SENDER"])

    def add_line(self, line):
        current_message = self.get_message()
        if current_message is not None:
            new_message = current_message + line
        else:
            new_message = line
        self.set_message(new_message)

    def get_subject(self):
        return self.get("subject")

    def get_receiver(self):
        return self.get("receiver")

    def get_sender(self):
        return self.get("sender")

    def get_message(self):
        return self.get("message")

    def get_time(self):
        return self.get("time")

    def set_sender(self, value):
        self.set("sender", value)

    def set_receiver(self, value):
        self.set("receiver", value)

    def set_message(self, value):
        self.set("message", value)

    def set_time(self, value):
        self.set("time", value)

    def set_subject(self, value):
        self.set("subject", value)

    def send_be_user_activation_mail(self, be_user):
        host_protocol = current_app.config["HOST_PROTOCOL"]
        username = be_user.get("username")
        email = be_user.get("email")
        activation_token = be_user.get("activation_token")
        link = current_app.config["HOST"] + ":" + str(current_app.config["HOST_PORT"]) + url_for("backend.user_activate", user_id=be_user.get_id(), activation_token=activation_token)
        self.set_subject("Du wurdest hinzugefügt")
        self.add_line("""<h2>Hallo {0}</h2></br></br>""".format(username))
        self.add_line("""<p>Du wurdest zum Cryption Backend hinzugefügt<p></br>""")
        self.add_line("""<p>Bitte aktiviere deinen Account über folgenden Link: <a href="{0}{1}">Account aktivieren</a><p></br>""".format(host_protocol, link))
        self.set_receiver(email)
        self.send_message()

    def send_be_user_login_message(self, be_user):
        username = be_user.get("username")
        email = be_user.get("email")
        ip_address = be_user.get("ip_address")
        self.set_subject("Neuer Login")
        self.add_line("""<h2>Hallo {0}</h2></br></br>""".format(username))
        self.add_line("""<p>Es wurde ein neuer Login bei deinem Account festgestellt<p></br>""")
        self.add_line("""<p>IP Adresse: {0}<p></br>""".format(ip_address))
        self.add_line("""<p>Falls du das nicht warst empfehlen wir dir sofort das Passwort zu ändern!</p>""")
        self.set_receiver(email)
        self.send_message()

    def send_be_user_lockout_message(self, be_user):
        username = be_user.get("username")
        email = be_user.get("email")
        ip_address = be_user.get("ip_address")
        self.set_subject("Dein Zugang wurde gesperrt")
        self.add_line("""<h2>Hallo {0}</h2></br></br>""".format(username))
        self.add_line("""<p>Dein Zugang wurde aufgrund von zu vielen falschen Login Versuchen gesperrt<p></br>""")
        self.add_line("""<p>letzte IP Adresse: {0}<p></br>""".format(ip_address))
        self.set_receiver(email)
        self.send_message()

    def send_message(self):
        try:
            mail = Mail()
            mail.connect()
            message = Message(self.get_subject(), recipients=[self.get_receiver()])
            message.html = self.get_message()
            mail.send(message)
            self.save()
        except Exception as error:
            my_logger.log(10, error)

        return False


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


class Trash(Database):

    def __init__(self):
        super().__init__()
        self.table_name = "trash"
        self.put_into_trash = False

    def recover(self):
        connection = self.get_connection()
        cursor = connection.cursor()
        row = 0
        try:
            item_id = self.get("item_id")
            item_table = self.get("item_table")
            sql = """UPDATE {0} SET ctrl_deleted = 0 WHERE id = %s""".format(item_table)
            cursor.execute(sql, item_id)
            connection.commit()
            row = cursor.lastrowid
        except Exception as error:
            my_logger.log(10, error)
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
        if row > 0:
            return self.delete()
        return False

    def delete_final(self):
        connection = self.get_connection()
        cursor = connection.cursor()
        row = 0
        try:
            item_id = self.get("item_id")
            item_table = self.get("item_table")
            sql = """DELETE FROM {0} WHERE id = %s""".format(item_table)
            cursor.execute(sql, item_id)
            connection.commit()
            row = cursor.lastrowid
        except Exception as error:
            my_logger.log(10, error)
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
        if row > 0:
            return self.delete()
        return False
