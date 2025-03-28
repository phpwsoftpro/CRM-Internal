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
    last_fetched_email_id = fields.Char(
        string="Last Fetched Email ID",
        help="Stores the last fetched Gmail ID to optimize fetching new emails.",
    )


# _logger = logging.getLogger(__name__)


# class MailMail(models.Model):
#     _inherit = "mail.mail"

#     @api.model
#     def create_and_send_email(self, values):
#         _logger.info("BODY_HTML = %s", values.get("body_html"))  # Debug log

#         # Lấy Gmail người dùng đã xác thực OAuth
#         gmail_from = (
#             self.env["ir.config_parameter"]
#             .sudo()
#             .get_param("gmail_authenticated_email")
#         )

#         mail = self.create(
#             {
#                 "email_to": values.get("email_to"),
#                 "subject": values.get("subject"),
#                 "body_html": values.get("body_html"),
#                 "email_from": gmail_from
#                 or self.env.user.email,  # Ưu tiên dùng Gmail nếu có
#             }
#         )

#         mail.send()
#         return True
