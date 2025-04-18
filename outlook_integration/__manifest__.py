{
    "name": "Outlook Integration",
    "version": "1.0",
    "category": "Discuss",
    "summary": "Integrate Outlook with Odoo Discuss",
    "description": """
        This module allows integration between Microsoft Outlook and Odoo Discuss.
    """,
    "author": "Outlook Integration",
    "depends": ["mail"],
    "data": [
        # "security/ir.model.access.csv",
        "views/discuss_view.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
