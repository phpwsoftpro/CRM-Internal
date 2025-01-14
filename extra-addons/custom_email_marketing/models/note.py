from odoo import models, fields, api

class NoteNote(models.Model):
    _inherit = 'note.note'

    partner_id = fields.Many2one('res.partner', string='Partner')