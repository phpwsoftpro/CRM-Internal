from odoo import models, fields

class MailingMailText(models.Model):
    _name = "mailing.mailtext"
    _description = "Mail Text Template"
    _rec_name = "char_mailtest"

    char_mailtest = fields.Char("Title", required=True)
    text_mailtest = fields.Html(
        string="Mail Content", sanitize='email_outgoing',
        render_engine='qweb', render_options={'post_process': True})