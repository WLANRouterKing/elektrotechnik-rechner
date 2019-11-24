#!/usr/bin/python
# -*- coding: utf-8 -*-
from flask_wtf.file import FileAllowed
from wtforms import StringField, PasswordField, SubmitField, SelectField, DateTimeField, BooleanField, TextAreaField, FileField, HiddenField
from wtforms.validators import DataRequired, EqualTo, Length, Email
from ..forms import CustomForm


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
    username = StringField('Benutzername', validators=[DataRequired()], render_kw={'class': 'form-control form-control-sm'})
    password = PasswordField('Passwort', validators=[DataRequired()])
    submit = SubmitField('Einloggen')

    def __init__(self):
        super().__init__()
        self.page = "login"
        self.display_tabs = False


class AddBeUserForm(CustomForm):
    username = StringField('Benutzername', validators=[DataRequired(), Length(min=4, max=30)])
    password = PasswordField('Passwort', validators=[DataRequired(), EqualTo('password2', message='Passwörter müssen übereinstimmen')])
    password2 = PasswordField('Passwort wiederholen', validators=[DataRequired()])
    email = StringField('E-Mail', validators=[DataRequired(), Email(message="Bitte eine korrekte E-Mail Adresse angeben")])
    ctrl_access_level = SelectField("Zugriffslevel", choices=[("10", 'Admin'), ("5", 'Moderator'), ("1", 'Benutzer')])
    submit = SubmitField('Registrieren')

    def __init__(self):
        super().__init__()
        self.type = "be_user"
        self.page = "add_be_user"
        self.module = "be_user"


class EditBeUserForm(CustomForm):
    ctrl_login_message = BooleanField("Soll eine Benachrichtung bei erfolgreichem Login versendet werden ?", false_values=('false', 'false'))
    ctrl_lockout_message = BooleanField("Soll eine Benachrichtung versendet werden wenn der Account ausgesperrt wird ?", false_values=('false', 'false'))
    ctrl_active = BooleanField("Aktiv", false_values=('false', 'false'))
    ctrl_locked = BooleanField("Gesperrt", false_values=('false', 'false'))
    id = HiddenField()
    username = StringField('Benutzername', validators=[DataRequired(), Length(min=4, max=30)])
    email = StringField('E-Mail', validators=[DataRequired(), Email(message="Bitte eine korrekte E-Mail Adresse angeben")])
    ctrl_access_level = SelectField("Zugriffslevel", choices=[("10", 'Admin'), ("5", 'Moderator'), ("1", 'Benutzer')])
    ctrl_last_login = DateTimeField("Letzter Login")
    activation_token = StringField("Activation Token")
    user_password = PasswordField("Ihr Benutzerpasswort zur Authentifizierung", validators=[DataRequired(), Length(min=4, max=128)])
    submit = SubmitField('Benutzer aktualisieren')

    def __init__(self):
        super().__init__()
        self.type = "be_user"
        self.page = "edit_be_user"
        self.module = "be_user"


class ImageUploadField(FileField):
    type = "ImageUploadField"

    def __call__(self, **kwargs):
        return super().__call__(**kwargs)


class DocumentUploadField(FileField):
    type = "DocumentUploadField"

    def __call__(self, **kwargs):
        return super().__call__(**kwargs)


class Texteditor(TextAreaField):
    type = "Texteditor"

    def __call__(self, **kwargs):
        return super().__call__(**kwargs)


class NewsEditorForm(CustomForm):
    id = HiddenField()
    eid = StringField("EID")
    eid_custom = StringField("Custom EID")
    title = StringField("Titel", validators=[DataRequired()])
    intro_text = Texteditor("Intro Text", validators=[Length(max=145)])
    text = Texteditor("Text")
    main_image = ImageUploadField("Hauptbild", validators=[FileAllowed(["jpg", "png", "gif", "svg"], "Nur Bilder")], render_kw={'class': 'fileupload'})
    meta_image = ImageUploadField("Meta Bild", validators=[FileAllowed(["jpg", "png", "gif", "svg"], "Nur Bilder")], render_kw={'class': 'fileupload'})
    teaser_image = ImageUploadField("Teaser Bild", validators=[FileAllowed(["jpg", "png", "gif", "svg"], "Nur Bilder")], render_kw={'class': 'fileupload'})
    submit = SubmitField("News Meldung speichern")

    def __init__(self):
        super().__init__()
        self.type = "content"
        self.page = "edit_news"
        self.module = "news"
