from odoo import models, fields

class ResUsers(models.Model):
    _inherit = 'res.users'
    
    outlook_auth_code = fields.Char(string='Outlook Auth Code', readonly=True)
    outlook_auth_state = fields.Char(string='Outlook Auth State', readonly=True)