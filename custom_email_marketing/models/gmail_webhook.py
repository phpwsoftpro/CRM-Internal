from odoo import http
from odoo.http import request
import json
import logging
import base64

_logger = logging.getLogger(__name__)


class GmailWebhookController(http.Controller):

    @http.route(
        "/gmail/webhook", type="json", auth="public", methods=["POST"], csrf=False
    )
    def gmail_webhook(self, **kwargs):
        """
        Nhận thông báo từ Gmail Webhook khi có email mới.
        """
        _logger.info("Nhận Webhook từ Gmail: %s", json.dumps(kwargs))

        # Xác minh dữ liệu từ Google
        if "message" not in kwargs:
            return {"status": "no_message"}

        # Lấy Message ID từ dữ liệu Gmail
        message_id_encoded = kwargs["message"]["data"]
        message_id = base64.urlsafe_b64decode(message_id_encoded).decode("utf-8")
        _logger.info("New Gmail Message ID: %s", message_id)

        # Fetch email từ Gmail API
        access_token = (
            request.env["ir.config_parameter"].sudo().get_param("gmail_access_token")
        )
        if access_token:
            request.env["mail.message"].sudo().fetch_gmail_messages(access_token)

        return {"status": "success"}
