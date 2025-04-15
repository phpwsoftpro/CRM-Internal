from odoo import models, fields, api


class ResCompany(models.Model):
    _inherit = "res.company"

    domain = fields.Char(
        string="Domain", store=True, help="Company domain extracted from email"
    )
