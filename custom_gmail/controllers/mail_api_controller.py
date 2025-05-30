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
            full_body = msg.body or "No Content"
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
            "email": accounts.email,  # ✅ trả về duy nhất 1 email
        }

    @http.route("/gmail/account_id_by_email", type="json", auth="user")
    def get_account_id(self, email):
        account = (
            request.env["gmail.account"]
            .sudo()
            .search(
                [
                    ("gmail_email", "=", email),
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

    @http.route("/mail/messages", type="json", auth="user")
    def get_mail_messages(self, provider, **kwargs):
        domain = [("message_type", "=", "email")]
        if provider == "gmail":
            domain.append(("is_gmail", "=", True))
        elif provider == "outlook":
            domain.append(("is_outlook", "=", True))

        messages = (
            request.env["mail.message"]
            .sudo()
            .search(domain, order="date_received desc", limit=1000)
        )

        result = [
            {
                "id": msg.id,
                "subject": msg.subject or "No Subject",
                "sender": msg.email_sender or "Unknown",
                "receiver": msg.email_receiver or "Unknown",
                "date_received": (
                    msg.date_received.strftime("%Y-%m-%d %H:%M:%S")
                    if msg.date_received
                    else ""
                ),
            }
            for msg in messages
        ]

        return result

    @http.route("/api/send_email", type="http", auth="user", csrf=False, methods=["POST"])
    def send_email(self, **kwargs):
        data = json.loads(request.httprequest.get_data(as_text=True))

        to = extract_email_only(data.get("to", ""))
        subject = data.get("subject")
        body_html = data.get("body_html")
        thread_id = data.get("thread_id")
        message_id = data.get("message_id")

        if not to or not subject or not body_html:
            return request.make_json_response(
                {"status": "error", "message": "Missing required fields"}, status=400
            )

        # ✅ Lấy token từ gmail.account
        account = (
            request.env["gmail.account"]
            .sudo()
            .search([
                ("user_id", "=", request.env.user.id),
                ("access_token", "!=", False),
            ], limit=1)
        )

        if not account:
            return request.make_json_response(
                {"status": "error", "message": "No Gmail token available"}, status=400
            )

        access_token = account.access_token
        sender_email = account.email

        result = send_email_with_gmail_api(
            access_token=access_token,
            sender_email=sender_email,
            to_email=to,
            subject=subject,
            html_content=body_html,
            thread_id=thread_id,
            message_id=message_id,
            headers={
                "In-Reply-To": f"<{message_id}>",
                "References": f"<{message_id}>",
            } if message_id else None
        )

        return request.make_json_response(result)


