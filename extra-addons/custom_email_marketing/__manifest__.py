{
    "name": "Custom Menu Override",
    "summary": "Override the Email Marketing menu with Companies and Contacts",
    "version": "1.0",
    "author": "",
    "category": "Marketing",
    "license": "LGPL-3",
    "depends": [
        "base",
        "mail",
        "mass_mailing",  # assuming you need this based on your menus
    ],
    "data": [
        "security/ir.model.access.csv",  # File CSV chứa quyền truy cập
        "views/custom_menu_view.xml",
        "views/form_view_company.xml",
        "views/data/tech_stack_data.xml",
        "views/custom_send_email_template.xml",
    ],
    "installable": True,
    "auto_install": False,
    "application": True,
}
