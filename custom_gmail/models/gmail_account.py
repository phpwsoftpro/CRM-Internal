from odoo import models, fields


class GmailAccount(models.Model):
    _name = "gmail.account"
    _description = "Email Account (Gmail & Outlook)"

    user_id = fields.Many2one("res.users", string="User")
    email = fields.Char("Email")
    provider = fields.Selection(
        [("gmail", "Gmail"), ("outlook", "Outlook")], string="Provider", default="gmail"
    )
    access_token = fields.Char("Access Token")
    refresh_token = fields.Char("Refresh Token")
    token_expiry = fields.Datetime("Token Expiry")
    active = fields.Boolean(default=True)
    last_fetch_at = fields.Datetime(string="Last Fetch At")
