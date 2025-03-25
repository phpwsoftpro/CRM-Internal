from odoo import http
from odoo.http import request


class GmailInboxController(http.Controller):

    @http.route("/gmail/messages", type="json", auth="user", csrf=False)
    def get_gmail_messages(self):
        """
        API để lấy danh sách email từ mail.message (đã fetch từ Gmail API).
        """
        user_id = request.env.user.partner_id.id
        messages = (
            request.env["mail.message"]
            .sudo()
            .search(
                [
                    ("message_type", "=", "email"),
                    ("author_id", "=", user_id),
                    ("is_gmail", "=", True),
                ],
                order="date_received desc",
                limit=20,
            )
        )

        result = []
        for msg in messages:
            result.append(
                {
                    "id": msg.id,
                    "subject": msg.subject,
                    "sender": msg.email_sender,
                    "receiver": msg.email_receiver,
                    "date_received": (
                        msg.date_received.strftime("%Y-%m-%d %H:%M:%S")
                        if msg.date_received
                        else ""
                    ),
                    "body": msg.body + "..." if msg.body else "No Content",
                }
            )

        return result
