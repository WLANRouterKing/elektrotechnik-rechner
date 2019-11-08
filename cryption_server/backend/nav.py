from flask_login import current_user

from cryption_server import nav


def create_nav():
    nav.Bar('main', [
        nav.Item('Dashboard', 'backend.dashboard'),
        nav.Item('Inhalte', 'backend.dashboard'),
    ])

    navbar_main = nav.bars.__getitem__('main')
    navbar_main_items = navbar_main.items

    # navigationpunkte für admins
    if current_user.is_admin:
        navbar_main_items.append(nav.Item('Backend Benutzer', 'backend.be_user', items=[
            nav.Item('Übersicht', 'backend.be_user'),
            nav.Item('Benutzer hinzufügen', 'backend.be_user_add')
        ]))
        navbar_main_items.append(nav.Item('Benutzer', 'backend.user', items=[
            nav.Item('Benutzer hinzufügen', 'backend.user_add')
        ]))

    # navigationspunkte für admins und moderatoren
    if current_user.is_admin or current_user.is_moderator:
        navbar_main_items.append(nav.Item('System', 'backend.system', items=[
            nav.Item("Fehlgeschlagene Login Versuche", 'backend.failed_login_records'),
            nav.Item("System Mails", 'backend.system_mails'),
            nav.Item('Reports', 'backend.reports')
        ]))

    # navigationspunkt account
    navbar_main_items.append(nav.Item('Account', '', items=[nav.Item("Account bearbeiten", 'backend.account_edit'), nav.Item('Logout', 'backend.logout')]))
