from odoo import http
from odoo.http import request
import requests
import logging
from lxml import html
import re

_logger = logging.getLogger(__name__)


class OutlookMessageController(http.Controller):

    @http.route("/outlook/messages", type="json", auth="user", csrf=False)
    def outlook_messages(self, **kw):
        user = request.env.user.sudo()
        access_token = user.outlook_access_token
        if not access_token:
            return {"status": "error", "message": "No Outlook access token found"}

        headers = {"Authorization": f"Bearer {access_token}"}
        list_url = "https://graph.microsoft.com/v1.0/me/messages?$orderby=receivedDateTime desc&$top=20"
        list_response = requests.get(list_url, headers=headers)

        if list_response.status_code != 200:
            _logger.error(f"❌ Failed to fetch message list: {list_response.text}")
            return {"status": "error", "message": "Failed to fetch messages"}

        message_list = list_response.json().get("value", [])
        full_messages = []

        for msg in message_list:
            msg_id = msg["id"]
            # detail_url = f"https://graph.microsoft.com/v1.0/me/messages/{msg_id}?$select=subject,body,bodyPreview,receivedDateTime,from,sender"
            detail_url = f"https://graph.microsoft.com/v1.0/me/messages/{msg_id}"
            detail_response = requests.get(detail_url, headers=headers)

            if detail_response.status_code == 200:
                detail = detail_response.json()
                full_messages.append(
                    {
                        "id": detail["id"],
                        "subject": detail.get("subject", "No Subject"),
                        "sender": detail.get("sender", {})
                        .get("emailAddress", {})
                        .get("name"),
                        "from": detail.get("from", {})
                        .get("emailAddress", {})
                        .get("address"),
                        "date": detail.get("receivedDateTime"),
                        "body": detail.get("body", {}).get("content", "No Content"),
                        "bodyPreview": detail.get("bodyPreview", ""),
                        "type": "outlook",
                    }
                )
            else:
                _logger.warning(f"⚠️ Failed to fetch detail for message {msg_id}")

        return {"status": "ok", "messages": full_messages}

    @http.route("/outlook/current_user_info", type="json", auth="user")
    def outlook_current_user_info(self):
        access_token = request.env.user.outlook_access_token
        if not access_token:
            return {"status": "error", "message": "No access token"}

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
        response = requests.get("https://graph.microsoft.com/v1.0/me", headers=headers)

        if response.status_code != 200:
            return {"status": "error", "message": "Failed to fetch user info"}

        user_info = response.json()
        email = user_info.get("mail") or user_info.get("userPrincipalName")
        return {"status": "success", "email": email}

    @http.route("/outlook/my_accounts", type="json", auth="user")
    def my_outlook_accounts(self):
        accounts = (
            request.env["outlook.account"]
            .sudo()
            .search(
                [
                    ("user_id", "=", request.env.user.id),
                ]
            )
        )
        return [
            {
                "id": acc.id,
                "email": acc.email,
                "name": (acc.email or "").split("@")[0] if acc.email else "Unknown",
                "initial": (acc.email or "X")[0].upper(),
                "status": "active",
                "type": "outlook",
            }
            for acc in accounts
        ]

    @http.route("/outlook/delete_account", type="json", auth="user", csrf=False)
    def delete_outlook_account(self, account_id):
        account = (
            request.env["outlook.account"]
            .sudo()
            .search(
                [
                    ("id", "=", account_id),
                    ("user_id", "=", request.env.user.id),
                ],
                limit=1,
            )
        )

        if account:
            account.unlink()
            return {"status": "deleted"}
        return {"status": "not_found"}

    @http.route("/outlook/message_detail", type="json", auth="user")
    def outlook_message_detail(self, message_id):
        access_token = request.env.user.sudo().outlook_access_token
        if not access_token:
            return {"status": "error", "message": "No Outlook access token found"}

        url = f"https://graph.microsoft.com/v1.0/me/messages/{message_id}"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            _logger.error(f"❌ Failed to fetch Outlook message detail: {response.text}")
            return {"status": "error", "message": "Failed to fetch message detail"}

        message = response.json()
        raw_body = message.get("body", {}).get("content", "")

        # 👉 Strip Word-style CSS, HTML, and extract clean text
        try:
            # 1. Replace <br> with newline (optional)
            raw_body = (
                raw_body.replace("<br>", "\n")
                .replace("<br/>", "\n")
                .replace("<br />", "\n")
            )

            # 2. Remove style/comments (e.g., <!-- ... -->)
            raw_body = re.sub(r"<!--.*?-->", "", raw_body, flags=re.DOTALL)

            # 3. Parse and extract plain text
            parsed = html.fromstring(raw_body)
            cleaned_body = parsed.text_content()
        except Exception:
            cleaned_body = raw_body  # fallback if parsing fails

        return {
            "status": "ok",
            "subject": message.get("subject"),
            "sender": message.get("sender", {}).get("emailAddress", {}).get("name"),
            "from": message.get("from", {}).get("emailAddress", {}).get("address"),
            "date": message.get("receivedDateTime"),
            "body": cleaned_body.strip(),  # 👉 plain text only
            "content_type": message.get("body", {}).get("contentType", "unknown"),
        }
