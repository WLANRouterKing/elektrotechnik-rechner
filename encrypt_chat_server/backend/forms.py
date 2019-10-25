from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length, Email


class LoginForm(FlaskForm):
    username = StringField('Benutzername', validators=[DataRequired()])
    password = PasswordField('Passwort', validators=[DataRequired()])
    submit = SubmitField('Einloggen')


class RegisterForm(FlaskForm):
    username = StringField('Benutzername', validators=[DataRequired(), Length(min=4, max=30)])
    password = PasswordField('Passwort',
                             validators=[DataRequired(),
                                         EqualTo('password2', message='Passwörter müssen übereinstimmen')])
    password2 = PasswordField('Passwort wiederholen', validators=[DataRequired()])
    email = StringField('E-Mail',
                        validators=[DataRequired(), Email(message="Bitte eine korrekte E-Mail Adresse angeben")])
    submit = SubmitField('Registrieren')
