import requests
from odoo import models, fields, api


class GmailMessage(models.Model):
    _inherit = "mail.message"

    is_gmail = fields.Boolean(string="Is Gmail Message", default=False)
    gmail_id = fields.Char(string="Gmail ID")
    gmail_snippet = fields.Text(string="Snippet")

    @api.model
    def fetch_gmail_messages(self):
        """
        Fetch Gmail messages via API and store them in the mail.message model
        """
        client_id = (
            "934598997197-13d2tluslcltooi7253r1s1rkafj601h.apps.googleusercontent.com"
        )
        client_secret = "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"
        redirect_uri = "https://crm2.wsoftpro.com/auth_oauth/signin"
        token_uri = "https://oauth2.googleapis.com/token"
        access_token = (
            self.env["ir.config_parameter"].sudo().get_param("gmail_access_token")
        )

        if not access_token:
            raise ValueError("Access token not found. Please authenticate first.")

        url = "https://gmail.googleapis.com/gmail/v1/users/me/messages"
        headers = {
            "Authorization": f"Bearer {access_token}",
        }

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            messages = response.json().get("messages", [])
            for msg in messages:
                gmail_id = msg.get("id")
                # Get detailed message
                message_url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{gmail_id}"
                message_response = requests.get(message_url, headers=headers)
                if message_response.status_code == 200:
                    message_data = message_response.json()
                    snippet = message_data.get("snippet")

                    # Check if message already exists
                    if not self.search([("gmail_id", "=", gmail_id)]):
                        self.create(
                            {
                                "gmail_id": gmail_id,
                                "gmail_snippet": snippet,
                                "is_gmail": True,
                                "body": snippet,
                                "subject": message_data.get("payload", {})
                                .get("headers", [{}])[0]
                                .get("value", ""),
                                "message_type": "email",
                                "author_id": self.env.user.partner_id.id,  # Set current user as the author
                            }
                        )
        else:
            raise ValueError(f"Failed to fetch Gmail messages: {response.text}")

    def action_sync_gmail(self):
        """
        Sync Gmail messages on button click
        """
        self.fetch_gmail_messages()
        return {
            "type": "ir.actions.client",
            "tag": "reload",
        }
