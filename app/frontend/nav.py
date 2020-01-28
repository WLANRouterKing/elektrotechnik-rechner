from app import nav
from app.models import Page


def create_nav():
    nav.Bar('frontend')

    navbar_main = nav.bars.__getitem__('frontend')
    navbar_main_items = navbar_main.items

    page = Page()

    for id in page.get_top_level_pages():
        sub_pages = []
        page = Page()
        page.set_id(id[0])
        page.load()

        for sub_page_id in page.get_child_pages(page.get_id()):
            sub_page = Page()
            sub_page.set_id(sub_page_id[0])
            sub_page.load()
            item = nav.Item(sub_page.get_label(), 'frontend.page', {'page_eid': sub_page.get_eid()})
            sub_pages.append(item)

        navbar_main_items.append(
            nav.Item(page.get_label(), 'frontend.page', {'page_eid': page.get_eid()}, items=sub_pages))
