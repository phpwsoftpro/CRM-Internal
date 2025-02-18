import requests
from odoo import models, api, _


class GmailWebhook(models.Model):
    _inherit = "mail.message"

    @api.model
    def watch_gmail_webhook(self):
        """
        Đăng ký webhook với Gmail API để nhận thông báo khi có email mới.
        """
        access_token = (
            self.env["ir.config_parameter"].sudo().get_param("gmail_access_token")
        )
        if not access_token:
            _logger.error("Không có access token để đăng ký Webhook Gmail.")
            return

        url = "https://gmail.googleapis.com/gmail/v1/users/me/watch"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
        data = {
            "labelIds": ["INBOX"],  # Chỉ theo dõi hộp thư đến
            "topicName": "projects/odoo-2-18122024/topics/gmail-webhook-topic",
        }

        response = requests.post(url, headers=headers, json=data)
        _logger.info(
            "Gmail Webhook đăng ký thành công: %s",
            response.text if response.status_code == 200 else response.text,
        )
