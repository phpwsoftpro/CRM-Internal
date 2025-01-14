{
    "name": "Custom Menu Override",
    "summary": "Override the Email Marketing menu with Companies and Contacts",
    "version": "1.0",
    "author": "Your Name",
    "category": "Marketing",
    "license": "LGPL-3",
    "depends": [
        "base",  # Module cơ bản
        "mass_mailing",
        "contacts",  # Module Email Marketing
    ],
    "data": [
        "views/custom_menu_view.xml",  # File XML chứa khai báo menu
    ],
    "installable": True,
    "auto_install": False,
    "application": True,
}
