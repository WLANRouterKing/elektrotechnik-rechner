from flask import jsonify


class Response:

    def __init__(self):
        self.arrData = dict()

    def get(self, key):
        return self.arrData[key]

    def set(self, key, value):
        try:
            value = value.decode()
        except (UnicodeDecodeError, AttributeError):
            pass
        self.arrData[key] = value

    def get_json_response(self):
        return jsonify(self.arrData)
