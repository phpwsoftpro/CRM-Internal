from odoo import models, fields,api


class ResUsers(models.Model):
    _inherit = "res.users"

    outlook_email = fields.Char(string="Outlook Email")
    outlook_auth_code = fields.Char(string="Outlook Auth Code", readonly=True)
    outlook_auth_state = fields.Char(string="Outlook Auth State", readonly=True)
    outlook_access_token = fields.Char(string="Outlook Access Token")
    outlook_refresh_token = fields.Char(string="Outlook Refresh Token")
    gmail_authenticated_email = fields.Char("Gmail Authenticated Email")
    outlook_authenticated_email = fields.Char("Outlook Authenticated Email")
