import logging
from odoo import models, fields, api

_logger = logging.getLogger(__name__)

class GmailMessage(models.Model):
    _inherit = 'mail.message'

    gmail_id = fields.Char(string="Gmail ID", index=True)
    gmail_body = fields.Text(string="Body")
    is_gmail = fields.Boolean(string="Is Gmail Message", default=False)
    date_received = fields.Datetime(string="Date Received")
    email_sender = fields.Char(string="Email Sender")
    email_receiver = fields.Char(string="Email Receiver")
    email_cc = fields.Char(string="Email CC")
    last_fetched_email_id = fields.Char(string="Last Fetched Email ID", help="Stores the last fetched Gmail ID to optimize fetching new emails.")