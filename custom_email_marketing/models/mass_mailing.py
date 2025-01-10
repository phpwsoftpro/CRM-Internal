from odoo import models, fields


class MassMailing(models.Model):
    _inherit = "mail.mass_mailing"

    filter_mode = fields.Selection(
        [("contacts", "Contacts"), ("companies", "Companies")],
        string="Filter Mode",
        default="contacts",
    )
