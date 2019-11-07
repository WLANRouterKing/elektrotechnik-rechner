#!/usr/bin/python
# -*- coding: utf-8 -*-
from flask import flash
from flask_wtf import FlaskForm
from markupsafe import iteritems
from wtforms import StringField, PasswordField, SubmitField, SelectField, DateTimeField, BooleanField
from wtforms.validators import DataRequired, EqualTo, Length, Email


class CustomForm(FlaskForm):

    def exclude_from_error_messages(self):
        """

        Returns:
            list: Die Liste der Felder, die beim generieren der Fehlermeldungen und beim initialisieren übersprungen werden sollen
        """
        return ["meta", "_prefix", "_errors", "_fields", "_csrf", "csrf_token", "submit"]

    def get_error_messages(self):
        """
        Liefert die Fehlermeldungen falls die Validierung eines Form Feldes fehl schlägt

        Returns:
            bool: True wenn Fehlermeldungen vorhanden sind andernfalls False

        """

        errors = 0
        for key, field in iteritems(self._fields):
            if key not in self.exclude_from_error_messages():
                element = field
                if element.errors:
                    flash(element.label, "danger")
                    flash(element.errors, "danger")
                    errors += 1
        return errors > 0

    def init_values(self, object):
        """
        initialisiert diese Form anhand des übergebenen Benutzer Objekts

        Args:
            user: Der Benutzer dessen Daten initialisiert werden sollen

        Returns:
            bool: True wenn alle Daten initialisiert werden konnten andernfalls False

        """

        for key, field in iteritems(self._fields):
            element = field
            element.data = object.get(key)


class EditAccountForm(CustomForm):
    username = StringField('Benutzername', validators=[DataRequired(), Length(min=4, max=30)])
    password = PasswordField('Passwort', validators=[EqualTo('password2', message='Passwörter müssen übereinstimmen')])
    password2 = PasswordField('Passwort wiederholen')
    email = StringField('E-Mail', validators=[DataRequired(), Email(message="Bitte eine korrekte E-Mail Adresse angeben")])
    ctrl_access_level = SelectField("Zugriffslevel", choices=[("10", 'Admin'), ("5", 'Moderator'), ("1", 'Benutzer')])
    ctrl_last_login = DateTimeField("Letzter Login")
    ctrl_active = BooleanField("Aktiv", false_values=('false', 0))
    activation_token = StringField("Activation Token")
    ctrl_failed_logins = StringField("Fehlgeschlagene Loginversuche")
    ctrl_locked = BooleanField("Gesperrt", false_values=('false', 'false'))
    ctrl_authenticated = BooleanField("Authentifiziert", false_values=('false', 'false'))
    user_password = PasswordField("Ihr Benutzerpasswort zur Authentifizierung", validators=[DataRequired(), Length(min=4, max=128)])
    submit = SubmitField('Account aktualisieren')


class LoginForm(CustomForm):
    username = StringField('Benutzername', validators=[DataRequired()])
    password = PasswordField('Passwort', validators=[DataRequired()])
    submit = SubmitField('Einloggen')


class AddUserForm(CustomForm):
    username = StringField('Benutzername', validators=[DataRequired(), Length(min=4, max=30)])
    password = PasswordField('Passwort', validators=[DataRequired(), EqualTo('password2', message='Passwörter müssen übereinstimmen')])
    password2 = PasswordField('Passwort wiederholen', validators=[DataRequired()])
    email = StringField('E-Mail', validators=[DataRequired(), Email(message="Bitte eine korrekte E-Mail Adresse angeben")])
    ctrl_access_level = SelectField("Zugriffslevel", choices=[("10", 'Admin'), ("5", 'Moderator'), ("1", 'Benutzer')])
    submit = SubmitField('Registrieren')


class EditUserForm(CustomForm):
    username = StringField('Benutzername', validators=[DataRequired(), Length(min=4, max=30)])
    email = StringField('E-Mail', validators=[DataRequired(), Email(message="Bitte eine korrekte E-Mail Adresse angeben")])
    ctrl_access_level = SelectField("Zugriffslevel", choices=[("10", 'Admin'), ("5", 'Moderator'), ("1", 'Benutzer')])
    ctrl_last_login = DateTimeField("Letzter Login")
    ctrl_active = BooleanField("Aktiv", false_values=('false', 'false'))
    activation_token = StringField("Activation Token")
    ctrl_failed_logins = StringField("Fehlgeschlagene Loginversuche")
    ctrl_locked = BooleanField("Gesperrt", false_values=('false', 'false'))
    user_password = PasswordField("Ihr Benutzerpasswort zur Authentifizierung", validators=[DataRequired(), Length(min=4, max=128)])
    submit = SubmitField('Benutzer aktualisieren')
