import requests
import logging
from odoo import models, api

_logger = logging.getLogger(__name__)


class GmailFetch(models.Model):
    _inherit = "mail.message"

    @api.model
    def action_redirect_gmail_auth(self):
        """
        Redirect người dùng đến màn xác thực Gmail nếu access_token bị thiếu,
        hết hạn, hoặc không có đủ quyền (ví dụ thiếu quyền gửi mail).
        """
        config_params = self.env["ir.config_parameter"].sudo()

        # 🔁 Xoá token cũ để đảm bảo Google cấp lại đầy đủ scope
        config_params.set_param("gmail_access_token", "")
        config_params.set_param("gmail_refresh_token", "")
        config_params.set_param("gmail_authenticated_email", "")

        access_token = config_params.get_param("gmail_access_token")

        # Nếu có access_token thì thử xác thực
        if access_token:
            headers = {"Authorization": f"Bearer {access_token}"}
            profile_response = requests.get(
                "https://gmail.googleapis.com/gmail/v1/users/me/profile",
                headers=headers,
            )

            if profile_response.status_code == 200:
                email_address = profile_response.json().get("emailAddress")
                config_params.set_param("gmail_authenticated_email", email_address)
                _logger.info("Authenticated Gmail address: %s", email_address)

                try:
                    self.fetch_gmail_messages(access_token)
                    return {"type": "ir.actions.client", "tag": "reload"}
                except Exception as e:
                    _logger.warning("Access token có thể thiếu quyền: %s", str(e))

            _logger.warning("Access token is invalid or lacks permission.")

        # Cấu hình OAuth2
        _logger.debug("Redirecting to Google's OAuth2 consent screen.")
        config = self.get_google_config()

        scope = (
            "https://www.googleapis.com/auth/gmail.readonly "
            "https://www.googleapis.com/auth/gmail.send"
        )

        # ✅ Bắt buộc Google hiện lại cửa sổ chọn tài khoản + cấp refresh token mới
        auth_url = (
            f"{config['auth_uri']}?response_type=code"
            f"&client_id={config['client_id']}"
            f"&redirect_uri={config['redirect_uri']}"
            f"&scope={scope.replace(' ', '%20')}"
            f"&access_type=offline"
            f"&prompt=consent%20select_account"
            f"&include_granted_scopes=false"
        )

        _logger.info("Redirect URL generated: %s", auth_url)

        return {
            "type": "ir.actions.act_url",
            "url": str(auth_url),
            "target": "new",
        }

    @api.model
    def fetch_gmail_messages(self, access_token):
        """
        Fetch the latest 15 Gmail messages and store new ones.
        """

        def extract_body_from_payload(payload):
            """Đệ quy để lấy phần text/html body"""
            mime_type = payload.get("mimeType")
            body_data = payload.get("body", {}).get("data")

            if mime_type == "text/html" and body_data:
                try:
                    return base64.urlsafe_b64decode(body_data + "==").decode("utf-8")
                except Exception as e:
                    _logger.warning("Decode HTML body failed: %s", e)
                    return ""
            elif "parts" in payload:
                for part in payload["parts"]:
                    result = extract_body_from_payload(part)
                    if result:
                        return result
            return ""

        _logger.debug("Fetching Gmail messages...")

        url = "https://gmail.googleapis.com/gmail/v1/users/me/messages"
        headers = {"Authorization": f"Bearer {access_token}"}

        processed_messages = []
        next_page_token = None
        fetched_count = 0
        max_messages = 15

        existing_gmail_ids = set(
            self.search([], order="create_date desc", limit=15).mapped("gmail_id")
        )

        while fetched_count < max_messages:
            params = {"maxResults": 15}
            if next_page_token:
                params["pageToken"] = next_page_token

            response = requests.get(url, headers=headers, params=params)
            if response.status_code != 200:
                raise ValueError(f"Failed to fetch Gmail messages: {response.text}")

            messages = response.json().get("messages", [])
            next_page_token = response.json().get("nextPageToken")

            if not messages:
                break

            for msg in messages:
                if fetched_count >= max_messages:
                    break

                gmail_id = msg.get("id")
                if gmail_id in existing_gmail_ids:
                    continue

                message_url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{gmail_id}?format=full"
                message_response = requests.get(message_url, headers=headers)

                if message_response.status_code != 200:
                    continue

                message_data = message_response.json()
                payload = message_data.get("payload", {})
                headers_list = payload.get("headers", [])

                # Trích thông tin headers
                subject = next(
                    (
                        h.get("value")
                        for h in headers_list
                        if h.get("name") == "Subject"
                    ),
                    "No Subject",
                )
                sender = next(
                    (h.get("value") for h in headers_list if h.get("name") == "From"),
                    "Unknown Sender",
                )
                receiver = next(
                    (h.get("value") for h in headers_list if h.get("name") == "To"),
                    "Unknown Receiver",
                )
                cc = next(
                    (h.get("value") for h in headers_list if h.get("name") == "Cc"), ""
                )
                raw_date = next(
                    (h.get("value") for h in headers_list if h.get("name") == "Date"),
                    None,
                )

                date_received = self.parse_date(raw_date) if raw_date else None

                # ✅ Lấy body HTML (đệ quy)
                body = extract_body_from_payload(payload)

                # Lưu vào mail.message
                created_message = self.create(
                    {
                        "gmail_id": gmail_id,
                        "is_gmail": True,
                        "body": body,
                        "subject": subject,
                        "date_received": date_received,
                        "message_type": "email",
                        "author_id": self.env.user.partner_id.id,
                        "email_sender": sender,
                        "email_receiver": receiver,
                        "email_cc": cc,
                    }
                )

                # Ghi vào thông báo (nếu có dùng)
                self.env["mail.notification"].sudo().create(
                    {
                        "mail_message_id": created_message.id,
                        "res_partner_id": self.env.user.partner_id.id,
                        "notification_type": "inbox",
                        "is_read": False,
                    }
                )

                processed_messages.append(
                    {
                        "id": gmail_id,
                        "subject": subject,
                        "sender": sender,
                        "receiver": receiver,
                        "cc": cc,
                        "date_received": date_received,
                        "body": body,
                    }
                )

                fetched_count += 1

            if not next_page_token or fetched_count >= max_messages:
                break

        return processed_messages
