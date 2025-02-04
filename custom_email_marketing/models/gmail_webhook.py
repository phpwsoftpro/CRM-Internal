from odoo import http
from odoo.http import request
import json
import logging
import requests

_logger = logging.getLogger(__name__)


def create_gmail_webhook():
    access_token = "YOUR_ACCESS_TOKEN"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    data = {
        "labelIds": ["INBOX"],
        "topicName": "projects/YOUR_PROJECT_ID/topics/YOUR_TOPIC_NAME",
    }
    response = requests.post(
        "https://gmail.googleapis.com/gmail/v1/users/me/watch",
        headers=headers,
        json=data,
    )
    return response.json()


class GmailWebhookController(http.Controller):
    @http.route("/gmail/webhook", type="json", auth="public", csrf=False)
    def gmail_webhook(self, **kwargs):
        _logger.info("Webhook received: %s", json.dumps(kwargs))

        # Xác minh webhook
        if "message" not in kwargs:
            _logger.info("Verification request received from Google Pub/Sub.")
            return {"status": "verified"}

        # Lấy message ID từ webhook
        message_id = kwargs["message"]["data"]  # Thường được mã hóa base64
        _logger.info("New Gmail message ID: %s", message_id)

        # Giải mã và xử lý message
        access_token = (
            request.env["ir.config_parameter"].sudo().get_param("gmail_access_token")
        )
        if access_token:
            request.env["mail.message"].sudo().fetch_gmail_messages(access_token)

        return {"status": "success"}
