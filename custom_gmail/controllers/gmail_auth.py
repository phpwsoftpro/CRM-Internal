import requests
import json
import logging
from odoo.http import request, Controller, route

_logger = logging.getLogger(__name__)


class GmailAuthController(Controller):

    @route("/odoo/gmail/auth/callback", type="http", auth="user", csrf=False)
    def gmail_auth_callback(self, **kwargs):
        """
        Handle Google OAuth2 callback and extract the access token.
        """
        _logger.debug("Google OAuth2 callback invoked.")
        code = kwargs.get("code")
        if not code:
            _logger.error("Authorization code not provided.")
            return request.render(
                "custom_gmail.gmail_auth_error",
                {"error": "Authorization code not provided"},
            )

        config = request.env["mail.message"].sudo().get_google_config()
        token_url = config["token_uri"]
        payload = {
            "code": code,
            "client_id": config["client_id"],
            "client_secret": config["client_secret"],
            "redirect_uri": config["redirect_uri"],
            "grant_type": "authorization_code",
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        response = requests.post(token_url, data=payload, headers=headers)
        _logger.debug("Token exchange response: %s", response.text)

        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get("access_token")
            refresh_token = token_data.get("refresh_token")
            expires_in = token_data.get("expires_in")

            config_params = request.env["ir.config_parameter"].sudo()
            config_params.set_param("gmail_access_token", access_token)
            if refresh_token:
                config_params.set_param("gmail_refresh_token", refresh_token)
            if expires_in:
                config_params.set_param("gmail_token_expiry", expires_in)

            # Fetch email address của người dùng Gmail sau khi đăng nhập
            profile_response = requests.get(
                "https://gmail.googleapis.com/gmail/v1/users/me/profile",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            if profile_response.status_code == 200:
                email_address = profile_response.json().get("emailAddress")
                config_params.set_param("gmail_authenticated_email", email_address)
                _logger.info("Gmail authenticated email: %s", email_address)
            else:
                _logger.warning(
                    "Failed to get Gmail profile: %s", profile_response.text
                )

            # 🔄 Optional: Refresh function
            def refresh_access_token():
                refresh_payload = {
                    "client_id": config["client_id"],
                    "client_secret": config["client_secret"],
                    "refresh_token": refresh_token,
                    "grant_type": "refresh_token",
                }
                refresh_response = requests.post(
                    token_url, data=refresh_payload, headers=headers
                )
                if refresh_response.status_code == 200:
                    refresh_data = refresh_response.json()
                    new_access_token = refresh_data.get("access_token")
                    config_params.set_param("gmail_access_token", new_access_token)
                    _logger.info("Access token refreshed.")
                    return new_access_token
                else:
                    _logger.error("Failed to refresh token: %s", refresh_response.text)
                    return None

            try:
                gmail_messages = (
                    request.env["mail.message"]
                    .sudo()
                    .fetch_gmail_messages(access_token)
                )
                _logger.info("Gmail sync completed.")
                self.sync_messages_and_notifications(gmail_messages)
            except Exception as e:
                _logger.error("Gmail sync error: %s", str(e))
                return request.render(
                    "custom_gmail.gmail_auth_error", {"error": str(e)}
                )

            _logger.info("Redirecting to Discuss.")
            return request.redirect("/web#menu_id=mail.menu_root_discuss")

        else:
            error_message = response.json()
            _logger.error("Failed to obtain access token: %s", error_message)
            request.env["ir.logging"].create(
                {
                    "name": "Gmail OAuth2 Error",
                    "type": "server",
                    "level": "error",
                    "dbname": request.env.cr.dbname,
                    "message": json.dumps(error_message),
                }
            )
            return request.render(
                "custom_gmail.gmail_auth_error", {"error": error_message}
            )

    def sync_messages_and_notifications(self, gmail_messages):
        """
        Sync Gmail messages and create notifications.
        """
        current_partner_id = request.env.user.partner_id.id
        discuss_channel = (
            request.env["discuss.channel"]
            .sudo()
            .search([("name", "=", "Inbox")], limit=1)
        )

        if not discuss_channel:
            _logger.debug("Creating Discuss Inbox channel.")
            discuss_channel = (
                request.env["discuss.channel"]
                .sudo()
                .create(
                    {
                        "name": "Inbox",
                        "channel_type": "chat",
                        "channel_partner_ids": [(4, current_partner_id)],
                    }
                )
            )

        all_created = True
        for message in gmail_messages:
            try:
                _logger.info("Creating Discuss message for Gmail ID: %s", message["id"])
                created_message = (
                    request.env["mail.message"]
                    .sudo()
                    .create(
                        {
                            "gmail_id": message["id"],
                            "subject": message["subject"] or "No Subject",
                            "body": message["body"] or "No Body",
                            "message_type": "email",
                            "model": "discuss.channel",
                            "res_id": discuss_channel.id,
                            "author_id": current_partner_id,
                        }
                    )
                )

                _logger.info("Creating notification for Gmail ID: %s", message["id"])
                request.env["mail.notification"].sudo().create(
                    {
                        "mail_message_id": created_message.id,
                        "res_partner_id": current_partner_id,
                        "notification_type": "inbox",
                        "is_read": False,
                    }
                )
            except Exception as e:
                _logger.error(
                    "Failed to create Discuss message or notification for Gmail ID: %s. Error: %s",
                    message["id"],
                    str(e),
                )
                all_created = False

        if not all_created:
            raise Exception("Failed to create all Discuss messages or notifications.")
