#!/usr/bin/python
# -*- coding: utf-8 -*-
from datetime import timedelta
from re import search
from . import backend
from flask import session, flash, current_app, url_for
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from markupsafe import iteritems
from wtforms import StringField, PasswordField, SubmitField, SelectField, DateTimeField, BooleanField, TextAreaField, FileField
from wtforms.validators import DataRequired, EqualTo, Length, Email
from wtforms.csrf.session import SessionCSRF


class CustomForm(FlaskForm):
    display_tabs = True
    filter_label = ["csrf_token", "submit"]
    tabs = ["content", "meta", "ctrl"]
    method = "post"
    type = None
    module = None
    blueprint_name = backend.name
    form_id = "{0}-{1}-{2}".format(type, module, "form")
    page = ""

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

        for key, field in self.get_all_elements():
            element = field
            element.data = object.get(key)

    @property
    def action(self):
        page = "{0}.{1}".format(self.blueprint_name, self.page)
        return url_for(page)

    def get_all_elements(self):
        elements = list()
        for key, field in iteritems(self._fields):
            element = field
            elements.append(element)
        return elements

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

    def get_seo_elements(self):
        seo_elements = list()
        for element in self.get_all_elements():
            element_id = element.label.field_id
            if self.is_element_seo(element_id):
                seo_elements.append(element)
        return seo_elements

    def get_content_elements(self):
        content_elements = list()
        for element in self.get_all_elements():
            element_id = element.label.field_id
            if not self.is_element_seo(element_id) and not self.is_element_control(element_id):
                content_elements.append(element)
        return content_elements

    def get_control_elements(self):
        control_elements = list()
        for element in self.get_all_elements():
            element_id = element.label.field_id
            if self.is_element_control(element_id):
                control_elements.append(element)
        return control_elements

    def is_element_seo(self, element_id):
        if search("meta", element_id) is not None:
            return True
        return False

    def is_element_control(self, element_id):
        if search("ctrl", element_id) is not None:
            return True
        return False

    def get_image_upload_info(self, element):
        width = current_app.config["IMAGE_FORMATS"][self.module][element.label.field_id]["width"]
        height = current_app.config["IMAGE_FORMATS"][self.module][element.label.field_id]["height"]
        return "Bilder im Format {0}x{1}".format(width, height)

    def get_document_upload_info(self, element):
        return "Dokumente"

    def get_upload_message(self):
        return "Dateien hier ablegen zum Hochladen"

    def get_elements(self, prefix):
        elements = self.get_all_elements()
        elements_wanted = list()
        for element in elements:
            element_id = element.label.field_id

            if search(prefix, element_id) is not None:
                elements_wanted.append(element)
        if len(elements_wanted) <= 0 and prefix == "content":
            return self.get_content_elements()
        return elements_wanted

    def get_fileupload_container_html(self, element):
        image_format = ""
        if current_app.config["IMAGE_FORMATS"][self.module][element.label.field_id] is not None:
            image_format = element.label.field_id
        html = "<div class='fileupload-container form-control'>"
        html += '<input type="hidden" class="type" name="type" value="{0}">'.format(self.type)
        html += '<input type="hidden" class="module" name="module" value="{0}">'.format(self.module)
        html += '<input type="hidden" class="image-format" name="image-format" value="{0}">'.format(image_format)
        html += '<span class=""label">{0}</span>'.format(element.label)
        html += "<div class='dz-message form-control'>"
        html += "<span class='upload-message'>{0}</span>".format(self.get_upload_message())
        html += "</div>"
        if element.type == "ImageUploadField":
            html += "<span class='info'>{0}</span>".format(self.get_image_upload_info(element))
            html += "<span class='extensions'>{0}</span>".format(current_app.config["ALLOWED_IMAGE_EXTENSIONS"])
        elif element.type == "DocumentUploadField":
            html += "<span class='info'>{0}".format(self.get_document_upload_info(element))
            html += "<span class='extensions'>{0}</span>".format(current_app.config["ALLOWED_DOCUMENT_EXTENSIONS"])
        html += "<div class='fallback'>{0}</div>".format(element)
        html += str(element)
        html += "</div>"
        return html

    def get_element_html(self, element):
        html = "<div class='form-group'>"
        element_type = getattr(element.widget, 'type', None)
        element_input_type = getattr(element.widget, 'input_type', None)
        element_label = ""
        element_classes = list()
        element_classes.append("form-control")
        element_classes.append("form-control-sm")

        for exclude_label in self.filter_label:
            if str(element.label.field_id).lower() == str(exclude_label).lower():
                element_label = None

        if element_label is not None:
            element_label = element.label

        if element_input_type is not None:
            if element.widget.input_type == "checkbox":
                element_classes.append("form-inline")
            elif element.widget.input_type == "submit":
                element_label = None
                element_classes.append("btn-dark")
            elif element.widget.input_type == "file":
                html += self.get_fileupload_container_html(element)

        if element_type is not None:
            if element.widget.type == "DateTimeField":
                element_classes.append("datepicker")

        if element_label is not None:
            html += str(element_label)
            html += "<div class='clear'></div>"
        html += str(element)
        html += "</div>"
        return html

    def render(self):
        html = '<form id="{0}" method="{1}" action="{2}">'.format(self.form_id, self.method, self.action)
        if self.display_tabs:
            html += "<ul class='nav nav-tabs'>"
            for tab in self.tabs:
                html += "<li class='nav-item'>"
                html += '<a class="nav-link">{0}</a>'.format(str(tab).capitalize())
                html += "</li>"
            html += "</ul>"
            for tab in self.tabs:
                html += '<div id="tab-{0}" class="container-fluid">'.format(tab)
                for element in self.get_elements(tab):
                    html += self.get_element_html(element)
                html += "</div>"
        else:
            for element in self.get_all_elements():
                html += self.get_element_html(element)
        html += '</form>'
        return html


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
    page = "login"
    display_tabs = False
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


class ImageUploadField(FileField):
    type = "ImageUploadField"

    def __call__(self, **kwargs):
        return super().__call__(**kwargs)


class DocumentUploadField(FileField):
    type = "DocumentUploadField"

    def __call__(self, **kwargs):
        return super().__call__(**kwargs)


class NewsEditorForm(CustomForm):
    type = "content"
    page = "add_news"
    module = "news"
    eid = StringField("EID")
    eid_custom = StringField("Custom EID")
    title = StringField("Titel", validators=[DataRequired()])
    intro_text = TextAreaField("Intro Text", validators=[Length(max=145)])
    text = TextAreaField("Text", render_kw={'class': 'texteditor'})
    main_image = ImageUploadField("Hauptbild", validators=[FileAllowed(["jpg", "png", "gif", "svg"], "Nur Bilder")], render_kw={'class': 'fileupload'})
    meta_image = ImageUploadField("Meta Bild", validators=[FileAllowed(["jpg", "png", "gif", "svg"], "Nur Bilder")], render_kw={'class': 'fileupload'})
    teaser_image = ImageUploadField("Teaser Bild", validators=[FileAllowed(["jpg", "png", "gif", "svg"], "Nur Bilder")], render_kw={'class': 'fileupload'})
    submit = SubmitField("News Meldung speichern")
