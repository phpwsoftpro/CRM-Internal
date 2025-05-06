import json
import requests
import logging
from odoo import models, api, fields
import base64
from lxml import html
import mimetypes
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)


def replace_cid_links(html_body, attachments):
    try:
        tree = html.fromstring(html_body)
        for img in tree.xpath("//img"):
            src = img.get("src", "")
            if src.startswith("cid:"):
                cid_name = src.replace("cid:", "").strip("<>")
                for att in attachments:
                    possible_cids = [
                        (att.description or "").strip("<>"),
                        (att.description or "").split("@")[0],
                        att.name or "",
                    ]
                    if cid_name in possible_cids:
                        img.set("src", f"/web/content/{att.id}")
                        _logger.debug(
                            "🔁 Replaced CID %s → /web/content/%s", cid_name, att.id
                        )
                        break
        return html.tostring(tree, encoding="unicode")
    except Exception as e:
        _logger.warning("⚠️ CID replacement failed: %s", e)
        return html_body


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

    def save_attachments(self, payload, gmail_msg_id, res_id, headers):
        saved_attachments = []

        def recurse(part):
            filename = part.get("filename")
            body_info = part.get("body", {})
            att_id = body_info.get("attachmentId")
            content_id = part.get("headers", [])

            # Lấy Content-ID (CID) nếu có
            cid = next(
                (
                    h.get("value").strip("<>")
                    for h in content_id
                    if h.get("name") == "Content-ID"
                ),
                None,
            )

            if filename and att_id:
                att_url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{gmail_msg_id}/attachments/{att_id}"
                att_response = requests.get(att_url, headers=headers)
                if att_response.status_code == 200:
                    att_data = att_response.json().get("data")
                    if att_data:
                        try:
                            file_data = base64.urlsafe_b64decode(att_data + "==")
                        except Exception as e:
                            _logger.warning(
                                "❌ Lỗi decode attachment %s: %s", filename, e
                            )
                            return

                        # Dự đoán mimetype nếu Google API không trả về
                        mimetype = (
                            part.get("mimeType")
                            or mimetypes.guess_type(filename)[0]
                            or "application/octet-stream"
                        )

                        att_vals = {
                            "name": filename,
                            "datas": base64.b64encode(file_data).decode(
                                "utf-8"
                            ),  # 🧠 decode để đúng định dạng Odoo
                            "res_model": "mail.message",
                            "res_id": res_id,
                            "mimetype": mimetype,
                            "type": "binary",
                        }

                        if cid:
                            att_vals["description"] = (
                                cid  # Dùng để replace ảnh inline (cid)
                            )

                        att = self.env["ir.attachment"].sudo().create(att_vals)
                        saved_attachments.append(att)
                        _logger.debug(
                            "✅ Attachment saved: %s - CID: %s - Type: %s",
                            filename,
                            cid,
                            mimetype,
                        )

            for sub in part.get("parts", []):
                recurse(sub)

        recurse(payload)
        return saved_attachments

    def extract_all_html_parts(self, payload):
        html_parts = []

        def recurse(part):
            mime_type = part.get("mimeType")
            body_data = part.get("body", {}).get("data")
            if mime_type == "text/html" and body_data:
                try:
                    html_parts.append(
                        base64.urlsafe_b64decode(body_data + "==").decode("utf-8")
                    )
                except Exception as e:
                    _logger.warning("❌ Decode HTML failed: %s", e)
            for sub in part.get("parts", []):
                recurse(sub)

        recurse(payload)
        return "\n".join(html_parts) if html_parts else ""

    @api.model
    def fetch_gmail_for_account(self, account_id):
        account = self.env["gmail.account"].sudo().browse(account_id)
        if not account:
            return

        # ✅ Kiểm tra token hết hạn → refresh nếu cần
        if account.token_expiry and account.token_expiry < datetime.utcnow():
            _logger.info(f"🔄 Token expired for {account.email}, refreshing...")
            success = self.env["gmail.account"].refresh_access_token(account)
            if not success:
                raise ValueError(f"❌ Failed to refresh token for {account.email}")

        headers = {"Authorization": f"Bearer {account.access_token}"}
        max_messages = 15
        fetched_count = 0
        next_page_token = None
        base_url = "https://gmail.googleapis.com/gmail/v1/users/me/messages"

        # ✅ Lấy danh sách gmail_id đã sync trong 30 ngày
        thirty_days_ago = fields.Datetime.to_string(datetime.now() - timedelta(days=30))
        existing_gmail_ids = set(
            self.search([("create_date", ">=", thirty_days_ago)]).mapped("gmail_id")
        )

        while fetched_count < max_messages:
            # ✅ Thêm buffer 5 phút để tránh miss mail
            if account.last_fetch_at:
                after_ts = int(account.last_fetch_at.timestamp()) - 300  # trừ 5 phút
            else:
                after_ts = int((datetime.utcnow() - timedelta(days=30)).timestamp())
            params = {"maxResults": 15}
            # params = {"maxResults": 15, "q": f"after:{after_ts}"}
            if next_page_token:
                params["pageToken"] = next_page_token

            response = requests.get(base_url, headers=headers, params=params)
            _logger.debug("📨 Gmail API RAW response: %s", response.text)

            if response.status_code != 200:
                _logger.error("❌ Failed to fetch message list: %s", response.text)
                return

            messages = response.json().get("messages", [])
            next_page_token = response.json().get("nextPageToken")

            _logger.debug(
                "📨 Gmail API trả về message IDs: %s", [m.get("id") for m in messages]
            )

            if not messages:
                break

            for msg in messages:
                if fetched_count >= max_messages:
                    break

                gmail_id = msg.get("id")
                thread_id = msg.get("threadId")

                # ✅ Check tồn tại → bỏ qua (KHÔNG unlink)
                if gmail_id in existing_gmail_ids:
                    _logger.debug("🔁 Đã tồn tại trong DB, bỏ qua: %s", gmail_id)
                    continue

                # ✅ Fetch chi tiết message
                detail_url = f"{base_url}/{gmail_id}?format=full"
                message_response = requests.get(detail_url, headers=headers)
                if message_response.status_code != 200:
                    _logger.warning("❌ Lỗi khi lấy chi tiết message %s", gmail_id)
                    continue

                msg_data = message_response.json()
                payload = msg_data.get("payload", {})

                # Extract headers
                def extract_header(payload, header_name):
                    headers = payload.get("headers", [])
                    for h in headers:
                        if h.get("name", "").lower() == header_name.lower():
                            return h.get("value", "")
                    for part in payload.get("parts", []):
                        result = extract_header(part, header_name)
                        if result:
                            return result
                    return ""

                subject = extract_header(payload, "Subject") or "No Subject"
                sender = extract_header(payload, "From")
                receiver = extract_header(payload, "To")
                cc = extract_header(payload, "Cc")
                raw_date = extract_header(payload, "Date")
                date_received = self.parse_date(raw_date) if raw_date else None
                raw_message_id = extract_header(payload, "Message-Id")
                message_id = raw_message_id.strip("<>") if raw_message_id else ""

                body_html = self.extract_all_html_parts(payload)

                created_message = self.create(
                    {
                        "gmail_id": gmail_id,
                        "is_gmail": True,
                        "body": body_html,
                        "subject": subject,
                        "date_received": date_received,
                        "message_type": "email",
                        "author_id": self.env.user.partner_id.id,
                        "email_sender": sender,
                        "email_receiver": receiver,
                        "email_cc": cc,
                        "thread_id": thread_id,
                        "message_id": message_id,
                    }
                )

                # ✅ Lưu attachment
                attachments = self.save_attachments(
                    payload, gmail_id, created_message.id, headers
                )
                attachment_list = [
                    {
                        "id": att.id,
                        "name": att.name,
                        "url": f"/web/content/{att.id}?download=true",
                        "mimetype": att.mimetype,
                    }
                    for att in attachments
                ]

                # ✅ Replace inline CID → gọi function trực tiếp
                if attachments and "cid:" in body_html:
                    updated_body = replace_cid_links(body_html, attachments)
                    created_message.body = updated_body
                else:
                    updated_body = body_html

                # ✅ Tạo notification
                self.env["mail.notification"].sudo().create(
                    {
                        "mail_message_id": created_message.id,
                        "res_partner_id": self.env.user.partner_id.id,
                        "notification_type": "inbox",
                        "is_read": False,
                    }
                )

                fetched_count += 1
                _logger.info("📩 Synced Gmail message: %s", subject)

            if not next_page_token or fetched_count >= max_messages:
                break

        _logger.info("✅ Đồng bộ Gmail hoàn tất (%s messages)", fetched_count)
        account.last_fetch_at = fields.Datetime.now()
        return True
