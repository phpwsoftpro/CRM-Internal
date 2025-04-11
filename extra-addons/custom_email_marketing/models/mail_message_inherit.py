from odoo import models, fields
from odoo import api


class MailMessage(models.Model):
    _inherit = "mail.message"

    project_id = fields.Many2one("project.project", string="Project")
