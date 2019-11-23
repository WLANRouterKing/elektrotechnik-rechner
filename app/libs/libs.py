from flask_login import current_user
from translations import COLUMN_LABELS


def translate_column(key):
    # language = current_user.language
    language = "DE"
    if key in COLUMN_LABELS:
        return COLUMN_LABELS[key][language]
    return "Übersetzung für Key:{0} nicht gefunden".format(key)
