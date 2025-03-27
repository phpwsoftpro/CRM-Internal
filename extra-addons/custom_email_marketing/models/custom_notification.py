from odoo import models, fields

class CustomNotification(models.Model):
    _name = "custom.notification"
    _description = "Custom Notification"
    _order = "create_date desc"

    user_id = fields.Many2one("res.users", string="User", required=True)
    message = fields.Text(string="Message", required=True)
    is_read = fields.Boolean(default=False)
    create_date = fields.Datetime(string="Created On", readonly=True)
