from wtforms import HiddenField

from app.forms import CustomForm


class PageElementEditorForm(CustomForm):
    id = HiddenField("id")

    def __init__(self):
        super().__init__()
        self.type = "content"
        self.page = "edit_page_element"
        self.module = "page_element"
