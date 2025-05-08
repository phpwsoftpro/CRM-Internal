import logging
from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class GmailMessage(models.Model):
    _inherit = "mail.message"

    gmail_id = fields.Char(string="Gmail ID", index=True)
    gmail_body = fields.Text(string="Body")
    is_gmail = fields.Boolean(string="Is Gmail Message", default=False)
    date_received = fields.Datetime(string="Date Received")
    email_sender = fields.Char(string="Email Sender")
    email_receiver = fields.Char(string="Email Receiver")
    email_cc = fields.Char(string="Email CC")
    last_fetched_email_id = fields.Char(string="Last Fetched Email ID")
    thread_id = fields.Char(string="Thread ID")
    message_id = fields.Char(string="Message ID")
    is_trashed = fields.Boolean(string="Is in Trash", default=False)
    gmail_account_id = fields.Many2one(
        "gmail.account", string="Gmail Account", index=True
    )

    _sql_constraints = [
        ("unique_gmail_id", "unique(gmail_id)", "Gmail ID must be unique!")
    ]
