import ipaddress
import datetime
from re import search
import mysql.connector
import copy
from flask import jsonify, current_app, url_for, flash
import nacl.utils
import nacl.secret
import nacl.encoding
import nacl.pwhash
import nacl.signing
import nacl.hash
from nacl import encoding
from nacl.bindings import sodium_memcmp
from nacl.public import PrivateKey
from flask_login import current_user
from app import Mail
from flask_mail import Message
from app import my_logger
from .libs.libs import translate_column


class Encryption:
    """
    Kryptographie
    """

    @staticmethod
    def create_random_token(length):
        """
        Generiert einen Token mit random bytes

        Args:
            length: Die Länge des Tokens

        Returns:
            str: Den generierten Token

        """

        return Encryption.bin_2_hex(nacl.utils.random(length))

    @staticmethod
    def bin_2_hex(value):
        """
        Konvertiert bytes in ihre hexadezimale darstellung

        Args:
            value: Der Byte-String der konvertiert werden soll

        Returns:
            str: Den hexadezimalen String

        """
        return nacl.encoding.HexEncoder.encode(value).decode('utf-8')

    @staticmethod
    def hex_2_bin(value):
        """
        Konvertiert einen hexadezimalen String in einen Byte-String

        Args:
            value: Der hexadezimale String

        Returns:
            str: Den Byte-String

        """
        return nacl.encoding.HexEncoder.decode(value)

    @staticmethod
    def create_sym_key():
        """
        Erstellt einen Schlüssel für die symmetrische Verschlüsselung

        Returns:
            str: Der generierte Schlüssel

        """
        return Encryption.bin_2_hex(Encryption.create_random_token(nacl.secret.SecretBox.KEY_SIZE))

    @staticmethod
    def get_sym_key():
        """
        Liefert den Schlüssel für die Synchrone Verschlüsselung aus der App Config

        Returns:
            str: Den Schlüssel
        """
        return Encryption.hex_2_bin(current_app.config["SYM_KEY"])

    @staticmethod
    def encrypt(data):
        """
        Verschlüsselt den übergebenen String mit dem symmetrischen Schlüssel

        Args:
            data: Der String der verschlüsselt werden soll

        Returns:
            str: Der verschlüsselte String oder der übergebene String wenn die Verschlüsselung fehlgeschlagen ist
        """

        if data == "" or data is None:
            return ""

        try:
            box = nacl.secret.SecretBox(Encryption.get_sym_key())
            data_encrypted = box.encrypt(bytes(data, encoding="utf-8"), nonce=None, encoder=encoding.Base64Encoder)
            return data_encrypted.decode('utf-8')
        except Exception as error:
            my_logger.log(10, error)
        return data

    @staticmethod
    def decrypt(data):
        """
        Entschlüsselt den übergebenen String mit dem symmetrischen Schlüssel

        Args:
            data: Der String der entschlüsselt werden soll

        Returns:
            Den entschlüsselten String insofern die Entschlüsselung erfolgreich war
            Ansonsten wird der übergebene String zurück gegeben

        """

        if data == "" or data is None:
            return ""

        try:
            box = nacl.secret.SecretBox(Encryption.get_sym_key())
            data_decrypted = box.decrypt(bytes(data, encoding="utf-8"), nonce=None, encoder=encoding.Base64Encoder)
            return data_decrypted.decode('utf-8')
        except Exception as error:
            my_logger.log(10, error)
        return data

    @staticmethod
    def sign_message(message):
        """

        Args:
            message:

        Returns:

        """
        signing_key = nacl.signing.SigningKey.generate()
        signed = signing_key.sign(bytes(message))
        verify_key = signing_key.verify_key
        verify_key_hex = verify_key.encode(encoder=nacl.encoding.HexEncoder)
        return signed, verify_key_hex

    @staticmethod
    def hash_password(password):
        """
        Generiert einen sicheren Hash für das Passwort

        Args:
            password: Das Passwort das gehashed werden soll

        Returns:
            str: Den Passwort Hash

        """
        return nacl.pwhash.argon2id.str(password.encode())

    @staticmethod
    def validate_hash(hash_string, string):
        """
        Validiert einen String und Hash

        Args:
            hash_string: Der Hash gegen den die Validierung durchgeführt wird
            string: Das übergebene Klartext Passwort

        Returns:
            bool: True wenn das Passwort mit dem Hash übereinstimmt andernfalls False

        """
        try:
            if nacl.pwhash.verify(bytes(hash_string, encoding="utf8"), bytes(string, encoding="utf8")):
                return True
        except Exception as error:
            my_logger.log(10, error)
        return False

    @staticmethod
    def as_base_64(data):
        """
        Base64 encoded einen String

        Args:
            data: der String der Base64 encoded werden soll

        Returns:
            str: den Base64 String

        """
        return nacl.encoding.Base64Encoder.encode(data)

    @staticmethod
    def get_generic_hash(string):
        hasher = nacl.hash.sha512
        return hasher(bytes(string, encoding="utf-8"), encoder=nacl.encoding.HexEncoder)


class Database:
    """

    Eltern Klasse für alle Datenbankbezogenen Objekte

    """

    def __init__(self):
        """

        Setzt die Default Werte der Klasse

        """
        self.encrypt = False
        self.connection = None
        self.encryption = Encryption()
        self.item_editable = True
        self.class_label = ""
        self.table_name = ""
        self.edit_node = ""
        self.delete_node = ""
        self.arrData = dict()
        self.put_into_trash = True
        self.exclude_from_encryption = ["id", "password", "username", "user_id", "ctrl"]
        self.column_admin_rights = ["ctrl_access_level"]
        self.filter_from_form_prepare = ["csrf_token", "type", "module", "user_password", "submit", "password2"]

    def get(self, key):
        """
        Generische Get-Funktion

        Args:
            key: Der Key in self.arrData der zurück gegeben werden soll

        Returns:
            str: Den gewünschten Wert aus arrData oder ein leerer String

        """
        if key in self.arrData:
            return self.arrData[key]
        else:
            return ""

    def set(self, key, value):
        """
        Generische Set-Funktion

        Args:
            key: Der Index der gesetzt werden soll
            value: Der Wert für den Index

        Returns:

        """
        self.arrData[key] = value

    def get_id(self):
        """
        Gibt die Id des Datenbank-Objekts als Integer zurück

        Returns:
            int: Die Id des Datenbank-Objekts

        """
        id = self.get("id")
        if id == "":
            id = 0
        return int(id)

    def get_user_id(self):
        """
        Gibt die Benutzer-Id des Datenbank-Objekts als Integer zurück

        Returns:
            int: Die Benutzer-Id des Datenbank-Objekts

        """
        user_id = self.get("user_id")
        if user_id == "":
            user_id = 0
        return int(user_id)

    def set_username(self, value):
        self.set("username", value)

    def get_username(self):
        """

        Returns:
            str: Den Benutzernamen
        """
        return self.get("username")

    def get_user_agent(self):
        return self.get("user_agent")

    def get_ctrl_active(self):
        return self.get("ctrl_active")

    def get_ctrl_time(self):
        return self.get("ctrl_time")

    def get_eid(self):
        return self.get("eid")

    def get_custom_eid(self):
        return self.get("custom_eid")

    def get_title(self):
        return self.get("title")

    def get_ctrl_deleted(self):
        return self.get("ctrl_deleted")

    def get_ip_address(self):
        return self.get("ip_address")

    def get_headline(self):
        return self.get("headline")

    def get_ctrl_show(self):
        return self.get("ctrl_show")

    def set_headline(self, value):
        self.set("headline", value)

    def set_id(self, value):
        self.set("id", value)

    def set_user_id(self, value):
        self.set("user_id", value)

    def set_ctrl_time(self, value):
        self.set("ctrl_time", value)

    def set_eid(self, value):
        self.set("eid", value)

    def set_custom_eid(self, value):
        self.set("custom_eid", value)

    def set_title(self, value):
        self.set("title", value)

    def set_ctrl_deleted(self, value):
        self.set("ctrl_deleted", value)

    def set_ctrl_active(self, value):
        self.set("ctrl_active", value)

    def set_ctrl_show(self, value):
        self.set("ctrl_show", value)

    def set_ip_address(self, value):
        self.set("ip_address", value)

    def set_user_agent(self, value):
        self.set("user_agent", value)

    def is_ip_address(self, value):
        try:
            ipaddress.ip_address(value)
            return True
        except Exception as error:
            my_logger.log(10, error)
        finally:
            return False

    def get_as_int(self, key):
        """
        Liefert einen Integer Wert für einen Schlüssel

        Args:
            key: Der Schlüssel der als Integer aus arrData zurück gegeben werden soll

        Returns:
            int: Den Integer Wert für den Schlüssel insofern dieser Konvertiert werden kannn ansonsten 0
        """
        string = self.get(key)
        if string != "":
            integer = int(string)
            return integer
        return 0

    def get_columns(self):
        table = self.table_name
        connection = self.get_connection()
        cursor = connection.cursor(prepared=True)
        columns = list()
        try:
            sql = "SHOW COLUMNS FROM {0}".format(table)
            cursor.execute(sql)
            rows = cursor.fetchall()
            for d in rows:
                column = d[0]
                try:
                    column.decode("utf-8")
                except Exception as error:
                    my_logger.log(10, error)
                columns.append(column)
        except Exception as error:
            my_logger.log(10, error)
        finally:
            self.close_connection(cursor)
        return columns

    def init_default(self):
        for column in self.get_columns():
            if column != "id" and search("ctrl", column) is None:
                self.set(column, "")

    def get_connection(self):
        """
        Erstellt und öffnet anhand der Config eine Datenbankverbindung

        Returns:

        """
        host = current_app.config["DATABASE_HOST"]
        database = current_app.config["DATABASE_NAME"]
        user = current_app.config["DATABASE_USER"]
        password = current_app.config["DATABASE_PASSWORD"]

        if self.connection is None or not self.connection.is_connected():
            self.connection = mysql.connector.connect(host=host, database=database, user=user, password=password)

        return self.connection

    def close_connection(self, cursor):

        """
        Schließt die Datenbankverbindung insofern diese Verbunden ist

        Returns:
            bool: True wenn die Datenbankverbindung geschlossen wurde andernfalls False

        """
        if self.connection is not None:
            cursor.close()
            if self.connection.is_connected():
                self.connection.close()
                return True
        return False

    def prepare_form_input(self, form_request):
        for key in form_request:
            if key not in self.filter_from_form_prepare:
                data = str(form_request[key])
                self.set(key, data)

    def load(self):
        """
        Generische Funktion zum Laden eines Datenbank-Objekts

        Die SQL Query wird anhand der gesetzten Werte in arrData
        automatisch angepasst.

        Returns:
            bool: True wenn das Objekt erfolgreich geladen wurde andernfalls False

        """
        connection = self.get_connection()
        cursor = connection.cursor(prepared=True)
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
                self.decrypt_data()
                return True
        except Exception as error:
            my_logger.log(10, error)
        finally:
            self.close_connection(cursor)

        return False

    def update(self):
        """
        Generische Update Funktion

        Aus arrData werden die Key/Value Paare extrahiert und in einen String, durch Komma getrennt, gespeichert
        Die Platzhalter für das Prepared Statement werden anhand der Länge von arrData erstellt
        Das Tuple mit den Values wird beim ausführen an das Statement gebunden

        Returns:
            bool: True wenn das Update erfolgreich ausgeführt wurde andernfalls False

        """
        connection = self.get_connection()
        cursor = connection.cursor(prepared=True)
        success = False
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
            rowcount = cursor.rowcount
            connection.commit()
            if rowcount > 0:
                success = True

            if rowcount > 0 and self.item_editable:
                flash("{0} mit der ID {1} wurde erfolgreich aktualisiert {2}".format(self.class_label, self.get_id(),
                                                                                     self.table_name), "success")
            elif rowcount <= 0 and self.item_editable:
                flash("{0} mit der ID {1} konnte nicht aktualisiert werden {2}".format(self.class_label, self.get_id(),
                                                                                       self.table_name), "success")

        except Exception as error:
            my_logger.log(10, error)
            success = False
        finally:
            self.close_connection(cursor)
        return success

    def insert(self):
        """
        Generische Insert Funktion

        Aus arrData werden die Key/Value Paare extrahiert und in einen String, durch Komma getrennt, gespeichert
        Die Platzhalter für das Prepared Statement werden anhand der Länge von arrData erstellt
        Das Tuple mit den Values wird beim ausführen an das Statement gebunden

        Returns:
            bool: False wenn das Objekt nicht eingetragen werden konnte
            int: Die Id des Objekts wenn es erfolgreich eingetragen wurde

        """
        connection = self.get_connection()
        cursor = connection.cursor(prepared=True)
        success = False
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
                self.set_id(row)
                success = row

            if row > 0 and self.item_editable:
                flash("{0} mit der ID {1} wurde erfolgreich erstellt".format(self.class_label, self.get_id()),
                      "success")
            elif row <= 0 and self.item_editable:
                flash("{0} mit der ID {1} konnte nicht erstellt werden".format(self.class_label, self.get_id()),
                      "success")

        except Exception as error:
            my_logger.log(10, error)
        finally:
            self.close_connection(cursor)

        return success

    def delete(self):
        """
        Löscht ein Datenbankobjekt

        Wenn self.put_into_trash auf True gesetzt wird, wird das Objekt im Papierkorb
        abgelegt. Andernfalls wird das Objekt direkt gelöscht.

        Returns:
            bool: True wenn das Objekt direkt aus der Datenbank gelöscht wurde andernfalls False

        """
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
                        flash("""{0} mit der ID {1} erfolgreich in den Papierkorb verschoben""".format(self.class_label,
                                                                                                       id), "success")
                    else:
                        flash("""{0} mit der ID {1} konnte nicht in den Papierkorb verschoben werden""".format(
                            self.class_label, id), "danger")
                else:
                    sql = """DELETE FROM {0} WHERE id = %s;""".format(table)
                cursor.execute(sql, [id])
                connection.commit()
                row = cursor.rowcount
                if self.table_name != "session":
                    if row > 0 and not self.put_into_trash:
                        flash("""{0} mit der ID {1} erfolgreich gelöscht""".format(self.class_label, id), "success")
                    elif row <= 0 and not self.put_into_trash:
                        flash("""{0} mit der ID {1} konnte nicht gelöscht werden""".format(self.class_label, id),
                              "danger")

                if row > 0:
                    success = True
            except Exception as error:
                my_logger.log(10, error)
            finally:
                self.close_connection(cursor)

        return success

    def id_list(self, sql_where):
        """
        Liefert eine Id List anhand des Tabellennamens

        Args:
            sql_where: Optional - Ein SQL-Where Statement zum filtern der Liste

        Returns:
            list: Die Id Liste

        """
        connection = self.get_connection()
        cursor = connection.cursor(prepared=True)
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
            self.close_connection(cursor)

        return self.list

    def object_list(self, object=None, sql_where=""):
        list_id = self.id_list(sql_where)
        for id in list_id:
            # objekt kopieren
            single_object = copy.copy(object)
            single_object.set("id", id)
            single_object.load()
            yield single_object

    def get_list_html(self):
        object = self
        columns = self.get_columns()
        html = '<table class="table table-striped table-dark col-lg-12 ">'
        html += '<thead>'
        for column in columns:
            html += '<th scope="col">' + translate_column(column) + '</th>'
        html += '</thead>'
        for item in self.object_list(object):
            html += '<tr>'

            for key in item.arrData:
                if key == 'id' or search('_id', key):
                    html += '<th scope="row">' + str(item.get(key)) + '</th>'
                else:
                    html += '<td>' + str(item.get(key)) + '</td>'

            if current_user.is_admin:
                if self.item_editable:
                    html += '<td class="edit">'
                    url = "backend." + self.edit_node
                    html += '<a href="' + url_for(url,
                                                  id=item.get_id()) + '" class="oi oi-pencil" title="' + self.class_label + ' bearbeiten" aria-hidden="true"></a>'
                    html += '</td>'
                if self.put_into_trash:
                    html += '<td class="remove">'
                    url = "backend." + self.delete_node
                    html += '<a href="' + url_for(url,
                                                  id=item.get_id()) + '" class="oi oi-trash" title="' + self.class_label + ' löschen" aria-hidden="true"></a>'
                    html += '</td>'
            html += '</tr>'

        html += '</table>'
        return html

    def encrypt_data(self):
        data = dict()
        for key in self.arrData:
            value = self.arrData[key]
            key_encryptable = True
            for exclude in self.exclude_from_encryption:
                if search(exclude, key) is not None:
                    key_encryptable = False
            if key_encryptable and self.encrypt:
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
            if key_decryptable and self.encrypt:
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
            id = self.insert()
            if id > 0:
                return True
            return False

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
            self.close_connection(cursor)

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
            self.close_connection(cursor)
        if rows is not None:
            return rows[0]
        return 0


class SystemSettings(Database):
    def __init__(self):
        super().__init__()
        self.item_editable = True
        self.table_name = "system_settings"
        self.put_into_trash = False


class Session(Database):

    def __init__(self):
        super().__init__()
        self.item_editable = False
        self.table_name = "session"
        self.put_into_trash = False

    def get_token(self):
        return self.get("token")

    def get_timestamp(self):
        return self.get("timestamp")

    def get_signed(self):
        return self.get("signed")

    def get_is_authenticated(self):
        return self.get("ctrl_authenticated")

    def set_is_authenticated(self, value):
        self.set("ctrl_authenticated", value)

    def set_token(self, value):
        self.set("token", value)

    def set_timestamp(self, value):
        self.set("timestamp", value)

    def set_signed(self, value):
        self.set("signed", value)

    def session_exists(self):
        return self.load()

    def is_authenticated(self):
        return bool(self.get_is_authenticated())

    def get_session_hash_string(self):
        token = self.get_token()
        timestamp = self.get_timestamp()
        user_id = self.get_user_id()
        user_agent = self.get_user_agent()
        ip_address = self.get_ip_address()
        return "{0}{1}{2}{3}{4}".format(token, timestamp, user_id, user_agent, ip_address)

    def get_user_hash_string(self, user_id, user_agent, ip_address, token, timestamp):
        return "{0}{1}{2}{3}{4}".format(token, timestamp, user_id, user_agent, ip_address)

    def is_valid(self, user_hash):
        datetime_now = datetime.datetime.now()
        session_time = self.get_timestamp()
        difference_minute = 9999999
        if isinstance(session_time, datetime.datetime):
            difference = datetime_now.timestamp() - session_time.timestamp()
            difference_minute = difference / 60
        if difference_minute <= 30:
            my_logger.log(10, """Session mit der User ID {0} ist noch nicht abgelaufen""".format(self.get_user_id()))
            hash_session = self.encryption.get_generic_hash(self.get_session_hash_string())
            if sodium_memcmp(hash_session, user_hash):
                my_logger.log(10, """Session mit der User ID {0} ist valid""".format(self.get_user_id()))
                return True
        my_logger.log(10,
                      """Session abgelaufen. User mit der ID {0} muss ausgeloggt werden.""".format(self.get_user_id()))
        return False


class SystemMail(Database):

    def __init__(self):
        super().__init__()
        self.item_editable = False
        self.put_into_trash = False
        self.table_name = "system_mail"
        self.set_sender(current_app.config["MAIL_FROM_EMAIL"])

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
        link = current_app.config["HOST"] + ":" + str(current_app.config["HOST_PORT"]) + url_for(
            "backend.be_user_activate", user_id=be_user.get_id(), activation_token=activation_token)
        self.set_subject("Du wurdest hinzugefügt")
        self.add_line("""<h2>Hallo {0}</h2></br></br>""".format(username))
        self.add_line("""<p>Du wurdest zum Cryption Backend hinzugefügt<p></br>""")
        self.add_line(
            """<p>Bitte aktiviere deinen Account über folgenden Link: <a href="{0}{1}">Account aktivieren</a><p></br>""".format(
                host_protocol, link))
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


class Trash(Database):

    def __init__(self):
        super().__init__()
        self.item_editable = False
        self.table_name = "trash"
        self.put_into_trash = False

    def get_item_id(self):
        return self.get("item_id")

    def get_item_table(self):
        return self.get("item_table")

    def set_item_id(self, value):
        self.set("item_id", value)

    def set_item_table(self, value):
        self.set("item_table", value)

    def recover(self):
        connection = self.get_connection()
        cursor = connection.cursor(prepared=True)
        row = 0
        try:
            item_id = self.get_item_id()
            item_table = self.get_item_table()
            sql = """UPDATE {0} SET ctrl_deleted = 0 WHERE id = %s""".format(item_table)
            cursor.execute(sql, item_id)
            connection.commit()
            row = cursor.lastrowid
        except Exception as error:
            my_logger.log(10, error)
        finally:
            self.close_connection(cursor)
        if row > 0:
            return True
        return False

    def delete_final(self):
        connection = self.get_connection()
        cursor = connection.cursor(prepared=True)
        row = 0
        try:
            item_id = self.get_item_id()
            item_table = self.get_item_table()
            sql = """DELETE FROM {0} WHERE id = %s""".format(item_table)
            cursor.execute(sql, item_id)
            connection.commit()
            row = cursor.lastrowid
        except Exception as error:
            my_logger.log(10, error)
        finally:
            self.close_connection(cursor)
        if row > 0:
            return True
        return False


class News(Database):

    def __init__(self):
        super().__init__()
        self.table_name = "news"
        self.class_label = "News-Meldung"
        self.edit_node = "edit_" + self.table_name
        self.delete_node = "delete_" + self.table_name

    def get_eid_custom(self):
        return self.get("eid_custom")

    def get_ctrl_datetime(self):
        return self.get("ctrl_datetime")

    def get_meta_description(self):
        return self.get("meta_description")

    def get_meta_title(self):
        return self.get("meta_title")

    def get_meta_image(self):
        return self.get("meta_image")

    def get_main_image(self):
        return self.get("main_image")

    def get_teaser_image(self):
        return self.get("teaser_image")

    def get_news_images(self):
        return self.get("news_images")

    def set_eid_custom(self, value):
        self.set("eid_custom", value)

    def set_ctrl_datetime(self, value):
        self.set("ctrl_datetime", value)

    def set_meta_description(self, value):
        self.set("meta_description", value)

    def set_meta_title(self, value):
        self.set("meta_title", value)

    def set_meta_image(self, value):
        self.set("meta_image", value)

    def set_main_image(self, value):
        self.set("main_image", value)

    def set_teaser_image(self, value):
        self.set("teaser_image", value)

    def set_news_images(self, value):
        self.set("news_images", value)


class Page(Database):

    def __init__(self):
        super().__init__()
        self.table_name = "page"
        self.class_label = "Seite"
        self.edit_node = "edit_" + self.table_name
        self.delete_node = "delete_" + self.table_name

    def get_label(self):
        return self.get("label")

    def get_parent_id(self):
        return self.get("parent_id")

    def get_intro_text(self):
        return self.get("introtext")

    def get_teaser_text(self):
        return self.get("teasertext")

    def get_slider_images(self):
        return self.get("slider_images")

    def get_head_image(self):
        return self.get("head_image")

    def get_teaser_image(self):
        return self.get("teaser_image")

    def get_meta_title(self):
        return self.get("meta_title")

    def get_meta_image(self):
        return self.get("meta_image")

    def get_meta_description(self):
        return self.get("meta_description")

    def get_ctrl_template(self):
        return self.get("ctrl_template")

    def get_ctrl_navigation(self):
        return self.get("ctrl_navigation")

    def get_ctrl_edit(self):
        return self.get("ctrl_edit")

    def get_ctrl_sort(self):
        return self.get("ctrl_sort")

    def get_ctrl_delete(self):
        return self.get("ctrl_delete")

    def get_ctrl_start(self):
        return self.get("ctrl_start")

    def set_label(self, value):
        self.set("label", value)

    def set_parent_id(self, value):
        self.set("parent_id", value)

    def set_intro_text(self, value):
        self.set("introtext", value)

    def set_teaser_text(self, value):
        self.set("teasertext", value)

    def set_slider_images(self, value):
        self.set("slider_images", value)

    def set_head_image(self, value):
        self.set("head_image", value)

    def set_teaser_image(self, value):
        self.set("teaser_image", value)

    def set_meta_title(self, value):
        self.set("meta_title", value)

    def set_meta_image(self, value):
        self.set("meta_image", value)

    def set_meta_description(self, value):
        self.set("meta_description", value)

    def set_ctrl_template(self, value):
        self.set("ctrl_template", value)

    def set_ctrl_navigation(self, value):
        self.set("ctrl_navigation", value)

    def set_ctrl_edit(self, value):
        self.set("ctrl_edit", value)

    def set_ctrl_sort(self, value):
        self.set("ctrl_sort", value)

    def set_ctrl_delete(self, value):
        self.set("ctrl_delete", value)

    def set_ctrl_start(self, value):
        self.set("ctrl_start", value)

    def get_page_title(self):
        title = self.get_title()
        if title == "":
            title = self.get_label()
        return title

    def prepare_eid(self):
        if self.get_custom_eid() == "":
            eid = self.get_label()
        else:
            eid = self.get_custom_eid()
        eid = str(eid).lower()
        # leerzeichen und sonderzeichen ersetzen
        self.set_eid(eid)

    def save(self):
        self.prepare_eid()
        super().save()
