from flask import current_app
from flask_login import current_user
from translations import COLUMN_LABELS


def translate_column(key):
    # language = current_user.language
    language = "DE"
    if key in COLUMN_LABELS:
        return COLUMN_LABELS[key][language]
    return "Übersetzung für Key:{0} nicht gefunden".format(key)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config["ALLOWED_IMAGE_EXTENSIONS"]
