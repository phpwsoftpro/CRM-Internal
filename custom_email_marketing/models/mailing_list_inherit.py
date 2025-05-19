from odoo import models, fields

class MailingList(models.Model):
    _inherit = "mailing.list"

    start_date = fields.Datetime(string="Start Date", default=lambda self: fields.Datetime.now())

