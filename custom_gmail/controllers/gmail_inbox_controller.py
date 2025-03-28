from odoo import http
from odoo.http import request
from bs4 import BeautifulSoup
import uuid
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
    def get_gmail_messages(self):
        """
        API lấy danh sách email từ mail.message đã fetch từ Gmail API,
        bao gồm attachment và xử lý HTML.
        """
        user_partner_id = request.env.user.partner_id.id
        messages = (
            request.env["mail.message"]
            .sudo()
            .search(
                [
                    ("message_type", "=", "email"),
                    ("author_id", "=", user_partner_id),
                    ("is_gmail", "=", True),
                ],
                order="date_received desc",
                limit=1000,
            )
        )

        result = []
        for msg in messages:
            # Xử lý rút gọn nội dung HTML (tránh dài quá mức)
            if msg.body:
                soup = BeautifulSoup(msg.body, "html.parser")
                text_preview = soup.get_text()
                short_body = text_preview + "..."

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
                    "url": f"/web/content/{att.id}?download=true",
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
                    "body": text_preview or "No Content",
                    "attachments": attachment_list,
                }
            )

        return result


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


def send_email_with_gmail_api(
    access_token, sender_email, to_email, subject, html_content
):
    message = MIMEMultipart("alternative")
    message["Subject"] = str(Header(subject, "utf-8"))
    message["From"] = sender_email
    message["To"] = to_email

    html_part = MIMEText(html_content, "html")
    message.attach(html_part)

    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    url = "https://gmail.googleapis.com/gmail/v1/users/me/messages/send"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    body = {"raw": raw_message}

    response = requests.post(url, headers=headers, json=body)

    if response.status_code in [200, 202]:
        resp_data = response.json()
        _logger.info(
            "Email sent via Gmail API: ID=%s, Thread=%s",
            resp_data.get("id"),
            resp_data.get("threadId"),
        )
        return {
            "status": "success",
            "gmail_id": resp_data.get("id"),
            "thread_id": resp_data.get("threadId"),
        }
    else:
        _logger.error("Failed to send Gmail: %s", response.text)
        return {
            "status": "error",
            "code": response.status_code,
            "message": response.text,
        }


_logger = logging.getLogger(__name__)


class MailAPIController(http.Controller):

    @http.route(
        "/api/send_email", type="http", auth="user", csrf=False, methods=["POST"]
    )
    def send_email(self, **kwargs):
        # Log headers và raw body để kiểm tra từ frontend
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

        to = data.get("to")
        subject = data.get("subject")
        body_html = data.get("body_html")

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

        # Gửi email qua Gmail API
        result = send_email_with_gmail_api(
            access_token, sender_email, to, subject, body_html
        )

        _logger.info("📤 Gmail API response: %s", result)
        return request.make_json_response(result)
