#!/usr/bin/python
# -*- coding: utf-8 -*-
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
    """
    Verschlüsselungs Klasse
    """

    def create_random_token(self, length):
        """
        Generiert einen Token mit random bytes

        Args:
            length: Die Länge des Tokens

        Returns:
            str: Den generierten Token

        """
        return nacl.utils.random(length)

    def bin_2_hex(self, value):
        """
        Konvertiert bytes in ihre hexadezimale darstellung

        Args:
            value: Der Byte-String der konvertiert werden soll

        Returns:
            str: Den hexadezimalen String

        """
        return nacl.encoding.HexEncoder.encode(value).decode('utf-8')

    def hex_2_bin(self, value):
        """
        Konvertiert einen hexadezimalen String in einen Byte-String

        Args:
            value: Der hexadezimale String

        Returns:
            str: Den Byte-String

        """
        return nacl.encoding.HexEncoder.decode(value)

    def create_sym_key(self):
        """
        Erstellt einen Schlüssel für die symmetrische Verschlüsselung

        Returns:
            str: Der generierte Schlüssel

        """
        return self.bin_2_hex(self.create_random_token(nacl.secret.SecretBox.KEY_SIZE))

    def get_sym_key(self):
        """
        Liefert den Schlüssel für die Synchrone Verschlüsselung aus der App Config

        Returns:
            str: Den Schlüssel
        """
        return self.hex_2_bin(current_app.config["SYM_KEY"])

    def encrypt(self, data):
        """
        Verschlüsselt den übergebenen String mit dem symmetrischen Schlüssel

        Args:
            data: Der String der verschlüsselt werden soll

        Returns:
            str: Der verschlüsselte String oder der übergebene String wenn die Verschlüsselung fehlgeschlagen ist
        """
        try:
            box = nacl.secret.SecretBox(self.get_sym_key)
            data_encrypted = box.encrypt(bytes(data, encoding="utf-8"), nonce=None, encoder=encoding.Base64Encoder)
            return data_encrypted.decode('utf-8')
        except Exception as error:
            my_logger.log(10, error)
        return data

    def decrypt(self, data):
        """
        Entschlüsselt den übergebenen String mit dem symmetrischen Schlüssel

        Args:
            data: Der String der entschlüsselt werden soll

        Returns:
            Den entschlüsselten String insofern die Entschlüsselung erfolgreich war
            Ansonsten wird der übergebene String zurück gegeben

        """
        try:
            box = nacl.secret.SecretBox(self.get_sym_key)
            data_decrypted = box.decrypt(bytes(data, encoding="utf-8"), nonce=None, encoder=encoding.Base64Encoder)
            return data_decrypted.decode('utf-8')
        except Exception as error:
            my_logger.log(10, error)
        return data

    def hash_password(self, password):
        """
        Generiert einen sicheren Hash für das Passwort

        Args:
            password: Das Passwort das gehashed werden soll

        Returns:
            str: Den Passwort Hash

        """
        return nacl.pwhash.argon2id.str(password.encode())

    def validate_hash(self, hash_string, string):
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
            pass
        return False

    def as_base_64(self, data):
        """
        Base64 encoded einen String

        Args:
            data: der String der Base64 encoded werden soll

        Returns:
            str: den Base64 String

        """
        return nacl.encoding.Base64Encoder.encode(data)

    def get_key_pair(self):
        """
        Generiert ein asynchrones Public/Private KeyPair

        Returns:
            KeyPair: Das generierte Schlüsselpaar Objekt

        """
        secret_key = PrivateKey.generate()
        public_key = secret_key.public_key
        key_pair = KeyPair()
        key_pair.set_private_key(secret_key)
        key_pair.set_public_key(public_key)
        return key_pair


class Database:
    """

    Eltern Klasse für alle Datenbankbezogenen Objekte

    """

    def __init__(self):
        """

        Setzt die Default Werte der Klasse

        """
        self.connection = None
        self.encryption = Encryption()
        self.class_label = ""
        self.table_name = ""
        self.arrData = dict()
        self.put_into_trash = True
        self.exclude_from_encryption = ["id", "username", "user_id", "ctrl"]
        self.column_admin_rights = ["ctrl_access_level"]
        self.filter_from_form_prepare = ["csrf_token", "user_password", "submit"]

    def __del__(self):
        """

        Klassen Destruktor
        Schließt die Datenbankverbindung

        """
        self.close_connection()

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

    def create_connection(self):
        """
        Erstellt und öffnet anhand der Config eine Datenbankverbindung

        Returns:

        """
        host = current_app.config["DATABASE_HOST"]
        database = current_app.config["DATABASE_NAME"]
        user = current_app.config["DATABASE_USER"]
        password = current_app.config["DATABASE_PASSWORD"]
        self.connection = mysql.connector.connect(host=host, database=database, user=user, password=password)

    def get_connection(self):
        """
        Gibt die Datenbankverbindung zurück

        Returns:
            MySQLConnection: Die Datenbankverbindung

        """
        if self.connection is None:
            self.create_connection()
        return self.connection

    def close_connection(self):
        """
        Schließt die Datenbankverbindung insofern diese Verbunden ist

        Returns:
            bool: True wenn die Datenbankverbindung geschlossen wurde andernfalls False

        """
        if self.connection.is_connected():
            self.connection.close()
            return True
        return False

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
                        pass
                self.decrypt_data()
                return True
        except Exception as error:
            my_logger.log(10, error)

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

        return False

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

        return False

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
        if row > 0:
            return self.delete()
        return False
