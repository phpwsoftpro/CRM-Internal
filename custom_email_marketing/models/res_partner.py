from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    last_activity_date = fields.Datetime(string="Last Activity Date (GMT+7)")
    last_modified_date = fields.Datetime(
        string="Last Modified Date (GMT+7)",
        compute='_compute_last_modified_date',
        store=True
    )
    industry = fields.Char(string="Industry")
    state_id = fields.Many2one('res.country.state', string="State/Region")
    timezone = fields.Char(string="Timezone")
    description = fields.Text(string="Description Company")
    linkedin_link = fields.Char(string="LinkedIn Link")
    message_ids = fields.One2many('mail.message', 'res_id', string="Messages", domain=[('model', '=', 'res.partner')])
    company_owner_id = fields.Many2one('res.users', string="Company Owner")
    contact_owner_id = fields.Many2one('res.users', string="Contact Owner")
    send_again = fields.Boolean(string="Send Again")
    lead_status = fields.Selection([
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('won', 'Won'),
        ('lost', 'Lost'),
    ], string="Lead Status")
    tech_stack_ids = fields.Many2many(
        'tech.stack',
        string="Area (Techstack)"
    )

    @api.model
    def message_get_reply_to(self):
        reply_to = super(ResPartner, self).message_get_reply_to()
        return reply_to
    
    @api.depends('write_date')
    def _compute_last_modified_date(self):
        for record in self:
            record.last_modified_date = record.write_date