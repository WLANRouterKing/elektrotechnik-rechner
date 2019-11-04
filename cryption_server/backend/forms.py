from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, DateTimeField, BooleanField
from wtforms.validators import DataRequired, EqualTo, Length, Email


class LoginForm(FlaskForm):
    username = StringField('Benutzername', validators=[DataRequired()])
    password = PasswordField('Passwort', validators=[DataRequired()])
    submit = SubmitField('Einloggen')


class AddUserForm(FlaskForm):
    username = StringField('Benutzername', validators=[DataRequired(), Length(min=4, max=30)])
    password = PasswordField('Passwort',
                             validators=[DataRequired(),
                                         EqualTo('password2', message='Passwörter müssen übereinstimmen')])
    password2 = PasswordField('Passwort wiederholen', validators=[DataRequired()])
    email = StringField('E-Mail',
                        validators=[DataRequired(), Email(message="Bitte eine korrekte E-Mail Adresse angeben")])
    ctrl_access_level = SelectField("Zugriffslevel", choices=[("10", 'Admin'), ("5", 'Moderator'), ("1", 'Benutzer')])
    submit = SubmitField('Registrieren')


class EditUserForm(FlaskForm):
    username = StringField('Benutzername', validators=[DataRequired(), Length(min=4, max=30)])
    password = PasswordField('Passwort',
                             validators=[DataRequired(),
                                         EqualTo('password2', message='Passwörter müssen übereinstimmen')])
    password2 = PasswordField('Passwort wiederholen', validators=[DataRequired()])
    email = StringField('E-Mail',
                        validators=[DataRequired(), Email(message="Bitte eine korrekte E-Mail Adresse angeben")])
    ctrl_access_level = SelectField("Zugriffslevel",
                                    choices=[("10", 'Admin'), ("5", 'Moderator'), ("1", 'Benutzer')])
    ctrl_last_login = DateTimeField("Letzter Login")
    ctrl_active = BooleanField("Aktiv")
    activation_token = StringField("Activation Token")
    ctrl_failed_logins = StringField("Fehlgeschlagene Loginversuche")
    ctrl_locked = BooleanField("Gesperrt")
    ctrl_lockout_time = DateTimeField("Gesperrt bis")
    ctrl_authenticated = BooleanField("Authentifiziert")
    user_password = PasswordField("Ihr Benutzerpasswort zur Authentifizierung", validators=[DataRequired()])
    submit = SubmitField('Benutzer aktualisieren')
