from flask import flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, DateTimeField, BooleanField
from wtforms.validators import DataRequired, EqualTo, Length, Email


class EditAccountForm(FlaskForm):
    username = StringField('Benutzername', validators=[DataRequired(), Length(min=4, max=30)])
    password = PasswordField('Passwort', validators=[EqualTo('password2', message='Passwörter müssen übereinstimmen')])
    password2 = PasswordField('Passwort wiederholen')
    email = StringField('E-Mail', validators=[DataRequired(), Email(message="Bitte eine korrekte E-Mail Adresse angeben")])
    ctrl_access_level = SelectField("Zugriffslevel", choices=[(10, 'Admin'), (5, 'Moderator'), (1, 'Benutzer')])
    ctrl_last_login = DateTimeField("Letzter Login")
    ctrl_active = BooleanField("Aktiv", false_values=('false', 0))
    activation_token = StringField("Activation Token")
    ctrl_failed_logins = StringField("Fehlgeschlagene Loginversuche")
    ctrl_locked = BooleanField("Gesperrt", false_values=('false', 'false'))
    ctrl_authenticated = BooleanField("Authentifiziert", false_values=('false', 'false'))
    user_password = PasswordField("Ihr Benutzerpasswort zur Authentifizierung", validators=[DataRequired(), Length(min=4, max=128)])
    submit = SubmitField('Account aktualisieren')

    def init_user_values(self, user):
        self.username.data = user.get("username")
        self.password.data = ""
        self.email.data = user.get("email")
        self.ctrl_access_level.data = user.get("ctrl_access_level")
        self.ctrl_last_login.data = user.get("ctrl_last_login")
        self.ctrl_active.data = int(user.get("ctrl_active"))
        self.activation_token.data = user.get("activation_token")
        self.ctrl_failed_logins.data = user.get("ctrl_failed_logins")
        self.ctrl_locked.data = int(user.get("ctrl_locked"))
        self.ctrl_authenticated.data = int(user.get("ctrl_authenticated"))

    def get_error_messages(self):
        if self.username.errors:
            flash(self.username.label)
            flash(self.username.errors, 'danger')
        if self.password.errors:
            flash(self.password.label)
            flash(self.password.errors, 'danger')
        if self.email.errors:
            flash(self.email.label)
            flash(self.email.errors, 'danger')
        if self.ctrl_access_level.errors:
            flash(self.ctrl_access_level.label)
            flash(self.ctrl_access_level.errors, 'danger')
        if self.ctrl_last_login.errors:
            flash(self.ctrl_last_login.label)
            flash(self.ctrl_last_login.errors, 'danger')
        if self.ctrl_active.errors:
            flash(self.ctrl_active.label)
            flash(self.ctrl_active.errors, 'danger')
        if self.activation_token.errors:
            flash(self.activation_token.label)
            flash(self.activation_token.errors, 'danger')
        if self.ctrl_failed_logins.errors:
            flash(self.ctrl_failed_logins.label)
            flash(self.ctrl_failed_logins.errors, 'danger')
        if self.ctrl_locked.errors:
            flash(self.ctrl_locked.label)
            flash(self.ctrl_locked.errors, 'danger')
        if self.ctrl_authenticated.errors:
            flash(self.ctrl_authenticated.label)
            flash(self.ctrl_authenticated.errors, 'danger')


class LoginForm(FlaskForm):
    username = StringField('Benutzername', validators=[DataRequired()])
    password = PasswordField('Passwort', validators=[DataRequired()])
    submit = SubmitField('Einloggen')

    def get_error_messages(self):
        if self.username.errors:
            flash(self.username.errors, 'danger')
        if self.password.errors:
            flash(self.password.errors, 'danger')


class AddUserForm(FlaskForm):
    username = StringField('Benutzername', validators=[DataRequired(), Length(min=4, max=30)])
    password = PasswordField('Passwort', validators=[DataRequired(), EqualTo('password2', message='Passwörter müssen übereinstimmen')])
    password2 = PasswordField('Passwort wiederholen', validators=[DataRequired()])
    email = StringField('E-Mail', validators=[DataRequired(), Email(message="Bitte eine korrekte E-Mail Adresse angeben")])
    ctrl_access_level = SelectField("Zugriffslevel", choices=[("10", 'Admin'), ("5", 'Moderator'), ("1", 'Benutzer')])
    submit = SubmitField('Registrieren')


class EditUserForm(FlaskForm):
    username = StringField('Benutzername', validators=[DataRequired(), Length(min=4, max=30)])
    password = PasswordField('Passwort', validators=[EqualTo('password2', message='Passwörter müssen übereinstimmen')])
    password2 = PasswordField('Passwort wiederholen')
    email = StringField('E-Mail', validators=[DataRequired(), Email(message="Bitte eine korrekte E-Mail Adresse angeben")])
    ctrl_access_level = SelectField("Zugriffslevel", choices=[(10, 'Admin'), (5, 'Moderator'), (1, 'Benutzer')])
    ctrl_last_login = DateTimeField("Letzter Login")
    ctrl_active = BooleanField("Aktiv", false_values=('false', 'false'))
    activation_token = StringField("Activation Token")
    ctrl_failed_logins = StringField("Fehlgeschlagene Loginversuche")
    ctrl_locked = BooleanField("Gesperrt", false_values=('false', 'false'))
    ctrl_authenticated = BooleanField("Authentifiziert", false_values=('false', 'false'))
    user_password = PasswordField("Ihr Benutzerpasswort zur Authentifizierung", validators=[DataRequired(), Length(min=4, max=128)])
    submit = SubmitField('Benutzer aktualisieren')

    def init_user_values(self, user):
        self.username.data = user.get("username")
        self.password.data = ""
        self.email.data = user.get("email")
        self.ctrl_access_level.data = user.get("ctrl_access_level")
        self.ctrl_last_login.data = user.get("ctrl_last_login")
        self.ctrl_active.data = user.get("ctrl_active")
        self.activation_token.data = user.get("activation_token")
        self.ctrl_failed_logins.data = user.get("ctrl_failed_logins")
        self.ctrl_locked.data = user.get("ctrl_locked")
        self.ctrl_authenticated.data = user.get("ctrl_authenticated")

    def get_error_messages(self):
        if self.username.errors:
            flash(self.username.label)
            flash(self.username.errors, 'danger')
        if self.password.errors:
            flash(self.password.label)
            flash(self.password.errors, 'danger')
        if self.email.errors:
            flash(self.email.label)
            flash(self.email.errors, 'danger')
        if self.ctrl_access_level.errors:
            flash(self.ctrl_access_level.label)
            flash(self.ctrl_access_level.errors, 'danger')
        if self.ctrl_last_login.errors:
            flash(self.ctrl_last_login.label)
            flash(self.ctrl_last_login.errors, 'danger')
        if self.ctrl_active.errors:
            flash(self.ctrl_active.label)
            flash(self.ctrl_active.errors, 'danger')
        if self.activation_token.errors:
            flash(self.activation_token.label)
            flash(self.activation_token.errors, 'danger')
        if self.ctrl_failed_logins.errors:
            flash(self.ctrl_failed_logins.label)
            flash(self.ctrl_failed_logins.errors, 'danger')
        if self.ctrl_locked.errors:
            flash(self.ctrl_locked.label)
            flash(self.ctrl_locked.errors, 'danger')
        if self.ctrl_authenticated.errors:
            flash(self.ctrl_authenticated.label)
            flash(self.ctrl_authenticated.errors, 'danger')
