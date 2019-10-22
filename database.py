import mysql.connector
from system import System
from flask import jsonify


class Database:
    """
    init funktion setzt tabellen namen, system objekt, arrData und initialisiert die datenbankverbindung
    """

    def __init__(self):
        self.system = System()
        self.table_name = ""
        self.arrData = dict()

    """
    generische get funktion -> muss zur sicherheit noch ergänzt werden
    """

    def get(self, key):
        if key in self.arrData:
            return self.arrData[key]
        else:
            return 0

    """
    generische set funktion -> muss zur sicherheit noch ergänzt werden
    """

    def set(self, key, value):
        self.arrData[key] = value

    def get_id(self):
        return self.get("id")

    def get_user_id(self):
        return self.get("user_id")

    """
    gibt ein MySQLConnection Objekt zurück
    """

    def get_connection(self):
        return mysql.connector.connect(host="localhost", database="encrypt_chat", user="encrypt_chat",
                                       password="root")

    """
    lädt einen datensatz anhand der id oder user_id aus der datenbank
    ist keine id angegeben wird die komplette tabelle geladen
    """

    def load(self):
        success = False
        connection = self.get_connection()
        cursor = connection.cursor()
        table = self.table_name

        try:
            data = self.arrData
            values = list(data.values())
            if int(self.get("id")) > 0:
                sql = """SELECT * FROM {0} WHERE id = %s""".format(table)
                cursor = connection.cursor(prepared=True)
                cursor.execute(sql, values)
            else:
                sql = """SELECT * FROM {0}""".format(table)
                cursor.execute(sql)

            result = []
            columns = tuple([str(d[0]) for d in cursor.description])
            for row in cursor:
                for v in row:
                    print(v)
                    try:
                        v.decode("utf-8")
                    except:
                        pass
                result.append(dict(zip(columns, row)))
            self.arrData = result
            success = True
        except mysql.connector.Error as error:
            self.system.log_exception("Loading failed ({0}) for following reason: {1}".format(table, error))

        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

        return success

    """
    generische update funktion
    verarbeitet die key,value pairs aus arrData in ein prepared statement mit platzhaltern
    und führt danach die query aus
    """

    def update(self):
        table = self.table_name
        id = self.get("id")
        data = self.arrData
        for d in data:
            try:
                d.decode("utf-8")
            except:
                str(d)
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

        connection = self.get_connection()
        cursor = connection.cursor(prepared=True)
        print(sql)
        print(values)
        success = cursor.execute(sql, values)

        return str(success)

    """
    generische insert methode
    verarbeitet die key,value pairs aus arrData in ein prepared statement mit platzhaltern
    und führt danach die query aus
    """

    def insert(self):
        try:
            table = self.table_name
            data = self.arrData
            columns = ','.join(data.keys())
            placeholders = ','.join(['%s'] * len(data))
            values = list(data.values())
            sql = """INSERT INTO {0} ({1}) VALUES ({2});""".format(table, columns, placeholders)
            connection = self.get_connection()
            cursor = connection.cursor(prepared=True)
            cursor.execute(sql, values)
            success = cursor.rowcount
            connection.commit()
            cursor.close()
            connection.close()
        except Exception as error:
            return "Ausnahme: ".format(error)
        return str(success)

    """
    generische speicher methode anhand der id wird überprüft ob der datensatz aus der Datenbank
    geladen wurde. Wenn dem so ist sollte die id > 0 sein und somit wird ein update() ausgeführt
    andernfalls wird insert() aufgerufen
    """

    def save(self):
        if self.get("id") > 0:
            return self.update()
        else:
            return self.insert()

    def get_json_response(self):
        return jsonify(self.arrData)
