from odoo import http
from odoo.http import request
from bs4 import BeautifulSoup
import re
import base64
import logging
import json
import requests
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header


class GmailInboxController(http.Controller):
    @staticmethod
    def clean_gmail_body(html_content):
        soup = BeautifulSoup(html_content or "", "lxml")
        for tag in soup(["style", "script"]):
            tag.decompose()
        return soup.get_text(separator="\n").strip()

    @http.route("/gmail/messages", type="json", auth="user", csrf=False)
    def get_gmail_messages(self, **kwargs):
        """
        API lấy danh sách email theo từng tài khoản (qua email), đã fetch từ Gmail API.
        """
        email = kwargs.get("email")
        domain = [
            ("message_type", "=", "email"),
            ("is_gmail", "=", True),
        ]
        if email:
            domain.append(("email_receiver", "ilike", email))

        messages = (
            request.env["mail.message"]
            .sudo()
            .search(domain, order="date_received desc", limit=1000)
        )

        result = []
        for msg in messages:
            full_body = self.clean_gmail_body(msg.body)
            attachments = (
                request.env["ir.attachment"]
                .sudo()
                .search(
                    [
                        ("res_model", "=", "mail.message"),
                        ("res_id", "=", msg.id),
                    ]
                )
            )

            attachment_list = [
                {
                    "id": att.id,
                    "name": att.name,
                    "url": f"/web/content/{att.id}",
                    "download_url": f"/web/content/{att.id}?download=true",
                    "mimetype": att.mimetype,
                }
                for att in attachments
            ]

            result.append(
                {
                    "id": msg.id,
                    "subject": msg.subject or "No Subject",
                    "sender": msg.email_sender or "Unknown Sender",
                    "receiver": msg.email_receiver or "Unknown Receiver",
                    "date_received": (
                        msg.date_received.strftime("%Y-%m-%d %H:%M:%S")
                        if msg.date_received
                        else ""
                    ),
                    "body": full_body,
                    "attachments": attachment_list,
                    "thread_id": msg.thread_id or "",
                    "message_id": msg.message_id or "",
                }
            )

        return result

    @http.route("/gmail/current_user_info", type="json", auth="user")
    def current_user_info(self, **kwargs):
        accounts = (
            request.env["gmail.account"]
            .sudo()
            .search(
                [("user_id", "=", request.env.user.id)],
                order="write_date desc",
                limit=1,
            )
        )  # ⚠️ lấy tài khoản mới nhất

        if not accounts:
            return {
                "status": "error",
                "message": "No Gmail accounts found",
            }

        return {
            "status": "success",
            "email": accounts[0].email,
        }

    @http.route("/gmail/account_id_by_email", type="json", auth="user")
    def get_account_id(self, email):
        account = (
            request.env["gmail.account"]
            .sudo()
            .search(
                [
                    ("email", "=", email),
                    ("user_id", "=", request.env.user.id),
                ],
                limit=1,
            )
        )
        return {"account_id": account.id if account else False}

    @http.route("/gmail/sync_account", type="json", auth="user")
    def sync_gmail_by_account(self, account_id):
        request.env["mail.message"].sudo().fetch_gmail_for_account(account_id)
        return {"status": "ok"}

    @http.route("/gmail/save_account", type="json", auth="user", csrf=False)
    def save_gmail_account(self, email, **kwargs):
        user_id = request.env.user.id
        GmailAccount = request.env["gmail.account"].sudo()

        # Tránh lưu trùng
        existing = GmailAccount.search(
            [
                ("email", "=", email),
                ("user_id", "=", user_id),
            ],
            limit=1,
        )

        if not existing:
            GmailAccount.create(
                {
                    "user_id": user_id,
                    "email": email,
                }
            )

        return {"status": "saved"}

    @http.route("/gmail/my_accounts", type="json", auth="user")
    def my_gmail_accounts(self):
        accounts = (
            request.env["gmail.account"]
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
                "type": "gmail",
            }
            for acc in accounts
        ]

    @http.route("/gmail/delete_account", type="json", auth="user", csrf=False)
    def delete_account(self, account_id):
        account = (
            request.env["gmail.account"]
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


class UploadController(http.Controller):

    @http.route(
        "/custom_gmail/upload_image",
        type="http",
        auth="user",
        csrf=False,
        methods=["POST"],
    )
    def upload_image_base64(self, **kwargs):
        upload = request.httprequest.files.get("upload")
        if upload:
            data = base64.b64encode(upload.read()).decode("utf-8")
            mimetype = upload.content_type
            return request.make_json_response({"url": f"data:{mimetype};base64,{data}"})
        return request.make_json_response({"error": "No file"}, status=400)


_logger = logging.getLogger(__name__)


def extract_email_only(email_str):
    match = re.search(r"<(.+?)>", email_str)
    return match.group(1) if match else email_str


def send_email_with_gmail_api(
    access_token,
    sender_email,
    to_email,
    subject,
    html_content,
    thread_id=None,
    message_id=None,
    headers=None,
):
    message = MIMEMultipart("alternative")
    message["Subject"] = str(Header(subject, "utf-8"))
    message["From"] = sender_email
    message["To"] = to_email

    # ✅ Dùng headers truyền vào nếu có
    if headers:
        for key, value in headers.items():
            message[key] = value
    elif message_id:
        # fallback nếu không truyền headers
        parent_ref = f"<{message_id}>"
        message["In-Reply-To"] = parent_ref
        message["References"] = parent_ref

    html_part = MIMEText(html_content, "html")
    message.attach(html_part)

    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    url = "https://gmail.googleapis.com/gmail/v1/users/me/messages/send"
    api_headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    body = {"raw": raw_message}
    if thread_id:
        body["threadId"] = (thread_id,)

    response = requests.post(url, headers=api_headers, json=body)
    _logger.info(
        "📬 Gmail API Response xem Message Id: %s",
        json.dumps(response.json(), indent=2),
    )
    if response.status_code in [200, 202]:
        resp_data = response.json()
        return {
            "status": "success",
            "gmail_id": resp_data.get("id"),
            "thread_id": resp_data.get("threadId"),
            "message_id": resp_data.get("messageId"),
        }
    else:
        _logger.error("Failed to send Gmail: %s", response.text)
        return {
            "status": "error",
            "code": response.status_code,
            "message": response.text,
        }


class MailAPIController(http.Controller):

    @http.route(
        "/api/send_email", type="http", auth="user", csrf=False, methods=["POST"]
    )
    def send_email(self, **kwargs):
        headers = dict(request.httprequest.headers)
        raw_data = request.httprequest.get_data(as_text=True)
        _logger.info("Headers: %s", headers)
        _logger.info("Raw Data: %s", raw_data)

        try:
            data = json.loads(raw_data)
            _logger.info("Parsed JSON: %s", data)
        except json.JSONDecodeError as e:
            _logger.error("Invalid JSON received: %s", e)
            return request.make_json_response(
                {"status": "error", "message": "Invalid JSON"}, status=400
            )

        to = extract_email_only(data.get("to", ""))
        subject = data.get("subject")
        body_html = data.get("body_html")
        thread_id = data.get("thread_id")
        message_id = data.get("message_id")
        if not to or not subject or not body_html:
            _logger.warning(
                "Missing fields: to=%s, subject=%s, body_html=%s",
                to,
                subject,
                body_html,
            )
            return request.make_json_response(
                {"status": "error", "message": "Missing required fields"}, status=400
            )

        access_token = (
            request.env["ir.config_parameter"].sudo().get_param("gmail_access_token")
        )
        sender_email = (
            request.env["ir.config_parameter"]
            .sudo()
            .get_param("gmail_authenticated_email")
        )

        if not access_token or not sender_email:
            _logger.error("Gmail token or authenticated email missing.")
            return request.make_json_response(
                {"status": "error", "message": "No Gmail token available"}, status=400
            )

        # ✅ Truyền thread_id nếu có
        result = send_email_with_gmail_api(
            access_token,
            sender_email,
            to,
            subject,
            body_html,
            thread_id,
            message_id,
            headers={
                "In-Reply-To": f"<{message_id}>",
                "References": f"<{message_id}>",
            },
        )
        _logger.info("📤 Gmail API response: %s", result)
        return request.make_json_response(result)
