import requests
import json
import logging
from datetime import datetime
from odoo import models, fields, api, _
from odoo.http import request, Controller, route
import pytz

_logger = logging.getLogger(__name__)

import requests
import json
import logging
from datetime import datetime
from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)


class GmailMessage(models.Model):
    _inherit = "mail.message"

    gmail_id = fields.Char(string="Gmail ID", index=True)
    gmail_snippet = fields.Text(string="Snippet")
    is_gmail = fields.Boolean(string="Is Gmail Message", default=False)
    date_received = fields.Datetime(string="Date Received")

    @api.model
    def get_google_config(self):
        """
        Load Google API configuration for OAuth2.
        """
        _logger.debug("Loading Google API configuration.")
        return {
            "client_id": "934598997197-13d2tluslcltooi7253r1s1rkafj601h.apps.googleusercontent.com",
            "client_secret": "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",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uri": "http://localhost:8070/odoo/gmail/auth/callback",
        }

    @api.model
    def action_redirect_gmail_auth(self):
        """
        Redirect user to Google's OAuth2 consent screen for authentication.
        """
        _logger.debug("Preparing redirect to Google's OAuth2 consent screen.")
        config = self.get_google_config()
        scope = "https://www.googleapis.com/auth/gmail.readonly"
        auth_url = (
            f"{config['auth_uri']}?response_type=code"
            f"&client_id={config['client_id']}"
            f"&redirect_uri={config['redirect_uri']}"
            f"&scope={scope}"
            f"&access_type=offline"
        )
        _logger.info("Redirect URL generated: %s", auth_url)
        return {
            "type": "ir.actions.act_url",
            "url": auth_url,
            "target": "new",
        }

    def parse_date(self, raw_date):
        """
        Attempt to parse a date string with multiple known formats.
        """
        # Remove any extra text like "(CST)" or "(UTC)"
        cleaned_date = raw_date.split("(")[0].strip()

        formats = [
            "%a, %d %b %Y %H:%M:%S %z",  # Standard RFC 2822 with timezone offset
            "%a, %d %b %Y %H:%M:%S %Z",  # Includes timezone abbreviation (e.g., CST)
            "%d %b %Y %H:%M:%S %z",  # Date without day of the week
            "%d %b %Y %H:%M:%S %Z",  # Date without day of the week, with timezone abbreviation
            "%a, %d %b %Y %H:%M:%S GMT",  # Date with GMT
        ]

        for fmt in formats:
            try:
                # Attempt parsing with the current format
                parsed_date = datetime.strptime(cleaned_date, fmt)
                # Ensure consistent UTC timezone
                if not parsed_date.tzinfo:
                    parsed_date = pytz.utc.localize(parsed_date)
                return parsed_date.strftime("%Y-%m-%d %H:%M:%S")
            except ValueError:
                continue

        # Log an error if all formats fail
        _logger.error("Failed to parse date: %s. Tried formats: %s", raw_date, formats)
        return None

    @api.model
    def fetch_gmail_messages(self, access_token):
        """
        Fetch the latest 10 Gmail messages via Gmail API and save them in `mail.message`.
        Returns the list of Gmail message data for further processing.
        """
        _logger.debug("Fetching Gmail messages with access token.")
        url = "https://gmail.googleapis.com/gmail/v1/users/me/messages"
        headers = {
            "Authorization": f"Bearer {access_token}",
        }
        params = {"maxResults": 10}  # Limit to the latest 10 emails
        response = requests.get(url, headers=headers, params=params)
        _logger.debug("Gmail messages fetch response: %s", response.text)

        if response.status_code != 200:
            _logger.error("Failed to fetch Gmail messages: %s", response.text)
            raise ValueError(f"Failed to fetch Gmail messages: {response.text}")

        messages = response.json().get("messages", [])
        _logger.info("Number of Gmail messages fetched: %s", len(messages))

        processed_messages = []  # List to store processed messages

        for msg in messages:
            gmail_id = msg.get("id")
            _logger.debug("Processing Gmail message ID: %s", gmail_id)
            message_url = (
                f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{gmail_id}"
            )
            message_response = requests.get(message_url, headers=headers)
            _logger.debug("Message details response: %s", message_response.text)

            if message_response.status_code == 200:
                message_data = message_response.json()
                snippet = message_data.get("snippet", "")
                headers_list = message_data.get("payload", {}).get("headers", [])

                # Extract subject and date from headers
                subject = next(
                    (
                        header.get("value")
                        for header in headers_list
                        if header.get("name") == "Subject"
                    ),
                    "No Subject",
                )
                raw_date = next(
                    (
                        header.get("value")
                        for header in headers_list
                        if header.get("name") == "Date"
                    ),
                    None,
                )

                # Parse date using the improved parse_date method
                date_received = self.parse_date(raw_date) if raw_date else None

                # Avoid duplicates by checking `gmail_id`
                if not self.search([("gmail_id", "=", gmail_id)]):
                    _logger.info(
                        "Creating a new mail.message record for Gmail ID: %s", gmail_id
                    )
                    self.create(
                        {
                            "gmail_id": gmail_id,
                            "gmail_snippet": snippet,
                            "is_gmail": True,
                            "body": snippet,
                            "subject": subject,
                            "date_received": date_received,
                            "message_type": "email",
                            "author_id": self.env.user.partner_id.id,
                        }
                    )

                # Append processed message data for further use
                processed_messages.append(
                    {
                        "id": gmail_id,
                        "snippet": snippet,
                        "subject": subject,
                        "date_received": date_received,
                    }
                )

        return processed_messages

    @api.model
    def scheduled_gmail_sync(self):
        """
        Scheduled action to fetch Gmail messages periodically.
        """
        _logger.debug("Scheduled Gmail sync invoked.")
        # Retrieve the stored access token (update this based on your implementation)
        config = self.get_google_config()
        access_token = (
            self.env["ir.config_parameter"].sudo().get_param("gmail_access_token")
        )

        if not access_token:
            _logger.error("Access token not available. Cannot sync Gmail messages.")
            return

        try:
            # Fetch Gmail messages using the stored token
            gmail_messages = self.sudo().fetch_gmail_messages(access_token)

            # Process Gmail messages
            current_partner_id = self.env.user.partner_id.id
            discuss_channel = (
                self.env["discuss.channel"]
                .sudo()
                .search([("name", "=", "Inbox")], limit=1)
            )

            if not discuss_channel:
                _logger.debug("Creating Discuss Inbox channel.")
                discuss_channel = (
                    self.env["discuss.channel"]
                    .sudo()
                    .create(
                        {
                            "name": "Inbox",
                            "channel_type": "chat",
                            "channel_partner_ids": [(4, current_partner_id)],
                        }
                    )
                )

            for message in gmail_messages:
                try:
                    _logger.info(
                        "Creating Discuss message for Gmail ID: %s", message["id"]
                    )
                    created_message = self.sudo().create(
                        {
                            "gmail_id": message["id"],
                            "subject": message["subject"] or "No Subject",
                            "body": message["snippet"] or "No Snippet",
                            "message_type": "email",
                            "model": "discuss.channel",
                            "res_id": discuss_channel.id,
                            "author_id": current_partner_id,
                        }
                    )

                    # Create notification
                    _logger.info(
                        "Creating notification for Gmail ID: %s", message["id"]
                    )
                    self.env["mail.notification"].sudo().create(
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
        except Exception as e:
            _logger.error("Error during scheduled Gmail sync: %s", str(e))


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

        # Get Google API credentials
        config = request.env["mail.message"].sudo().get_google_config()

        # Exchange the authorization code for an access token
        _logger.debug("Exchanging authorization code for access token.")
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
            refresh_token = token_data.get(
                "refresh_token"
            )  # Save the refresh token if provided
            expires_in = token_data.get("expires_in")

            _logger.info("Access token successfully obtained.")

            # Store the token and other data securely in `ir.config_parameter`
            config_params = request.env["ir.config_parameter"].sudo()
            config_params.set_param("gmail_access_token", access_token)
            if refresh_token:
                config_params.set_param("gmail_refresh_token", refresh_token)
            if expires_in:
                config_params.set_param("gmail_token_expiry", expires_in)

            # Trigger Gmail sync using the retrieved token
            try:
                _logger.debug("Initiating Gmail sync.")
                gmail_messages = (
                    request.env["mail.message"]
                    .sudo()
                    .fetch_gmail_messages(access_token)
                )
                _logger.info("Gmail sync completed successfully.")

                # Sync messages and notifications (existing logic)
                self.sync_messages_and_notifications(gmail_messages)
            except Exception as e:
                _logger.error("Error during Gmail sync: %s", str(e))
                return request.render(
                    "custom_gmail.gmail_auth_error", {"error": str(e)}
                )

            # Redirect to Discuss page after successful sync
            _logger.info("Redirecting to Discuss after successful Gmail sync.")
            return request.redirect("/web#menu_id=mail.menu_root_discuss")
        else:
            # Log the error and render the error template
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
                            "body": message["snippet"] or "No Snippet",
                            "message_type": "email",
                            "model": "discuss.channel",
                            "res_id": discuss_channel.id,
                            "author_id": current_partner_id,
                        }
                    )
                )

                # Create notification for the created message
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
