#!/usr/bin/python
# -*- coding: utf-8 -*-
from datetime import timedelta
from flask import session, flash
from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, FileAllowed
from markupsafe import iteritems
from wtforms import StringField, PasswordField, SubmitField, SelectField, DateTimeField, BooleanField, TextAreaField, FileField
from wtforms.validators import DataRequired, EqualTo, Length, Email
from wtforms.csrf.session import SessionCSRF


class CustomForm(FlaskForm):
    type = "content"
    module = ""

    class Meta:
        csrf = True
        csrf_class = SessionCSRF
        csrf_time_limit = timedelta(minutes=30)

        @property
        def csrf_context(self):
            return session

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

    def get_editor_add_message(self, object):
        label = object.class_label
        message = """{0} erstellen""".format(label)
        flash(message, "info")

    def get_editor_edit_message(self, object):
        label = object.class_label
        message = "{0} bearbeiten".format(label)
        flash(message, "info")

    def get_error_messages(self):
        for key, field in iteritems(self._fields):
            element = field
            if element.errors:
                flash(element.errors, "danger")


class EditAccountForm(CustomForm):
    ctrl_active = BooleanField("Aktiv", false_values=('false', 0))
    ctrl_locked = BooleanField("Gesperrt", false_values=('false', 'false'))
    username = StringField('Benutzername', validators=[DataRequired(), Length(min=4, max=30)])
    email = StringField('E-Mail', validators=[DataRequired(), Email(message="Bitte eine korrekte E-Mail Adresse angeben")])
    activation_token = StringField("Activation Token")
    ctrl_access_level = SelectField("Zugriffslevel", choices=[("10", 'Admin'), ("5", 'Moderator'), ("1", 'Benutzer')])
    ctrl_last_login = DateTimeField("Letzter Login")
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
    ctrl_active = BooleanField("Aktiv", false_values=('false', 'false'))
    ctrl_locked = BooleanField("Gesperrt", false_values=('false', 'false'))
    username = StringField('Benutzername', validators=[DataRequired(), Length(min=4, max=30)])
    email = StringField('E-Mail', validators=[DataRequired(), Email(message="Bitte eine korrekte E-Mail Adresse angeben")])
    ctrl_access_level = SelectField("Zugriffslevel", choices=[("10", 'Admin'), ("5", 'Moderator'), ("1", 'Benutzer')])
    ctrl_last_login = DateTimeField("Letzter Login")
    activation_token = StringField("Activation Token")
    user_password = PasswordField("Ihr Benutzerpasswort zur Authentifizierung", validators=[DataRequired(), Length(min=4, max=128)])
    submit = SubmitField('Benutzer aktualisieren')


class NewsEditorForm(CustomForm):
    module = "news"
    eid = StringField("EID")
    eid_custom = StringField("Custom EID")
    title = StringField("Titel", validators=[DataRequired()])
    intro_text = TextAreaField("Intro Text", validators=[Length(max=145)])
    text = TextAreaField("Text", render_kw={'class': 'texteditor'})
    main_image = FileField("Hauptbild", validators=[FileAllowed(["jpg", "png", "gif", "svg"], "Nur Bilder")], render_kw={'class': 'fileupload'})
    meta_image = FileField("Meta Bild", validators=[FileAllowed(["jpg", "png", "gif", "svg"], "Nur Bilder")], render_kw={'class': 'fileupload'})
    teaser_image = FileField("Teaser Bild", validators=[FileAllowed(["jpg", "png", "gif", "svg"], "Nur Bilder")], render_kw={'class': 'fileupload'})
    submit = SubmitField("News Meldung speichern")
