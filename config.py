############################################################################
# Column Labels
############################################################################
COLUMN_LABELS = {
    "id": {"DE": "Id", "EN": "Id"},
    "username": {"DE": "Benutzername", "EN": "Username"},
    "password": {"DE": "Passwort", "EN": "Password"},
    "email": {"DE": "Benutzername", "EN": "E-Mail"},
    "ctrl_access_level": {"DE": "Benutzergruppe", "EN": "Usergroup"},
    "ctrl_last_login": {"DE": "Letzter Login", "EN": "Last Login"},
    "ctrl_active": {"DE": "Aktiv", "EN": "Active"},
    "activation_token": {"DE": "Aktivierungstoken", "EN": "Activation Token"},
    "ctrl_failed_logins": {"DE": "Fehlgeschlagene Loginversuche", "EN": "Failed Logins"},
    "ctrl_locked": {"DE": "Gesperrt", "EN": "Locked"},
    "ctrl_lockout_time": {"DE": "Sperrzeit", "EN": "Time Lockout"},
    "ctrl_deleted": {"DE": "Gelöscht", "EN": "Deleted"},
    "user_id": {"DE": "Benutzer", "EN": "Username"},
}
############################################################################
# Image Formate
############################################################################
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'svg'}
IMAGE_FORMATS = {
    "news": {
        "main_image": {
            "width": "1920",
            "height": "0"
        },
        "teaser_image": {
            "width": "480",
            "height": "480"
        },
        "meta_image": {
            "width": "1920",
            "height": "0"
        }
    }
}
