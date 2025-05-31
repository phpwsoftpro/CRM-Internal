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
from odoo import http, fields, api
import time


class GmailInboxController(http.Controller):

    @http.route("/gmail/messages", type="json", auth="user", csrf=False)
    def get_gmail_messages(self, **kwargs):
        """
        API lấy danh sách email đã fetch từ Gmail API, đúng theo từng tài khoản Gmail.
        Hỗ trợ phân trang.
        """
        account_id = kwargs.get("account_id")
        page = int(kwargs.get("page", 1))
        limit = int(kwargs.get("limit", 15))
        offset = (page - 1) * limit

        domain = [
            ("message_type", "=", "email"),
            ("is_gmail", "=", True),
        ]

        if account_id:
            domain.append(("gmail_account_id", "=", int(account_id)))

        total = request.env["mail.message"].sudo().search_count(domain)

        messages = (
            request.env["mail.message"]
            .sudo()
            .search(domain, order="date_received desc", limit=limit, offset=offset)
        )

        result = []
        for msg in messages:
            full_body = self.clean_gmail_body(msg.body)
            attachments = (
                request.env["ir.attachment"]
                .sudo()
                .search([("res_model", "=", "mail.message"), ("res_id", "=", msg.id)])
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
                    "email_receiver": msg.email_receiver or "",
                    "email_cc": msg.email_cc or "",
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

        return {
            "messages": result,
            "total": total,
        }

    @staticmethod
    def clean_gmail_body(html_content):
        soup = BeautifulSoup(html_content or "", "lxml")
        for tag in soup(["style", "script"]):
            tag.decompose()
        return soup.get_text(separator="\n").strip()

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

    @http.route("/gmail/refresh_mail", type="json", auth="user", csrf=False)
    def refresh_mail(self, **kwargs):
        account_id = kwargs.get("account_id")
        if not account_id:
            _logger.warning("❌ Thiếu account_id trong request")
            return {"status": "fail", "error": "Thiếu account_id"}

        try:
            _logger.info(
                "📥 [START] Đã nhận refresh request cho account_id = %s", account_id
            )

            account = request.env["gmail.account"].sudo().browse(int(account_id))
            if not account.exists():
                _logger.warning("❌ Không tìm thấy tài khoản với ID %s", account_id)
                return {"status": "fail", "error": "Account không tồn tại"}

            result = request.env["mail.message"].fetch_gmail_for_account(account)

            _logger.info("✅ [DONE] Refresh xong cho account_id = %s", account_id)
            return {"status": "ok" if result else "fail"}

        except Exception as e:
            _logger.exception(
                "❌ Lỗi khi xử lý refresh_mail cho account_id = %s", account_id
            )
            return {"status": "fail", "error": str(e)}

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
                    ("access_token", "!=", False),  # ✅ Chỉ lấy account còn token
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

    @http.route("/gmail/session/ping", type="json", auth="user")
    def ping(self, account_id):
        _logger.warning(
            f"📥 [PING] Nhận account_id: {account_id} (type={type(account_id)})"
        )

        try:
            account_id = int(account_id)
        except Exception as e:
            _logger.error(f"❌ account_id không thể ép kiểu int: {account_id} ({e})")
            return {"error": "account_id không hợp lệ"}

        account = request.env["gmail.account"].sudo().browse(account_id)
        user_id = request.env.user.id

        _logger.warning(
            f"📥 [PING] Đang tạo session với gmail_account_id={account.id}, user_id={user_id}"
        )

        # Cập nhật hoặc tạo session
        session_model = request.env["gmail.account.session"].sudo()
        session = session_model.search(
            [("gmail_account_id", "=", account.id), ("user_id", "=", user_id)], limit=1
        )

        now = fields.Datetime.now()

        if session:
            session.write({"last_ping": now})
            _logger.info(f"🔄 [PING] Đã cập nhật last_ping cho session ID {session.id}")
        else:
            _logger.info("🆕 [PING] Chưa có session → tạo mới")
            try:
                created = session_model.create(
                    {
                        "gmail_account_id": account.id,
                        "user_id": user_id,
                        "last_ping": now,
                    }
                )
                _logger.info(f"✅ [PING] Đã tạo session ID {created.id}")
            except Exception as e:
                _logger.critical(
                    f"🔥 [PING] Lỗi khi tạo session! gmail_account_id={account.id}, user_id={user_id} ➤ {e}"
                )
                raise  # để Odoo vẫn hiển thị traceback

        return {"has_new_mail": account.has_new_mail}

    @http.route("/gmail/clear_new_mail_flag", type="json", auth="user")
    def clear_flag(self, account_id):
        account = request.env["gmail.account"].sudo().browse(int(account_id))
        account.has_new_mail = False
        return {"status": "ok"}

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

        if not account:
            return {"status": "not_found"}

        # Xoá email liên quan
        messages = (
            request.env["mail.message"]
            .sudo()
            .search(
                [
                    ("model", "=", "gmail.account"),
                    ("res_id", "=", account.id),
                    ("is_gmail", "=", True),
                ]
            )
        )

        attachments = (
            request.env["ir.attachment"]
            .sudo()
            .search(
                [("res_model", "=", "mail.message"), ("res_id", "in", messages.ids)]
            )
        )
        attachments.unlink()

        request.env["mail.notification"].sudo().search(
            [("mail_message_id", "in", messages.ids)]
        ).unlink()

        messages.unlink()

        # Xoá sync state nếu có
        request.env["gmail.account.sync.state"].sudo().search(
            [("gmail_account_id", "=", account.id)]
        ).unlink()

        account.write(
            {
                "access_token": False,
                "refresh_token": False,
                "token_expiry": False,
            }
        )

        return {"status": "token_removed"}


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
        body["threadId"] = thread_id

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
