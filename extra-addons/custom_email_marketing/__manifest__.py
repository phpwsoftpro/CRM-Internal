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
        "mass_mailing",
        "project",
        "web",  # assuming you need this based on your menus
    ],
    "assets": {
        "web.assets_backend": [
            # "custom_email_marketing/static/src/js/chatter_filter.js",
        ],
    },
    "data": [
        "security/ir.model.access.csv",  # File CSV chứa quyền truy cập
        "views/custom_menu_view.xml",
        "views/form_view_company.xml",
        "views/mailing_view_inherit.xml",
        "views/data/tech_stack_data.xml",
        "views/custom_send_email_template.xml",
        "views/discuss_view.xml",
        # "views/chatter_filter.xml",
    ],
    "installable": True,
    "auto_install": False,
    "application": True,
}
