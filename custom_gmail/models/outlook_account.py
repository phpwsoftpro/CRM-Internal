from odoo import models, fields, api


class OutlookAccount(models.Model):
    _name = "outlook.account"
    _description = "Outlook Account"

    user_id = fields.Many2one("res.users", string="User", required=True)
    email = fields.Char("Email", required=True)
    name = fields.Char("Name", compute="_compute_name", store=True)
    active = fields.Boolean("Active", default=True)

    _sql_constraints = [
        (
            "email_user_unique",
            "unique(user_id, email)",
            "Account with this email already exists for this user.",
        )
    ]

    @api.depends("email")
    def _compute_name(self):
        for rec in self:
            rec.name = (rec.email or "").split("@")[0]
