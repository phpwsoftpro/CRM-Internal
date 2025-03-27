from odoo import http
from odoo.http import request
from bs4 import BeautifulSoup


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
