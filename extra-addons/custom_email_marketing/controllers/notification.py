from odoo import http
from odoo.http import request


class NotificationController(http.Controller):

    @http.route("/notification/list", auth="user", type="json")
    def list_notifications(self):
        uid = request.env.uid
        notifications = (
            request.env["custom.notification"]
            .sudo()
            .search(
                [("user_id", "=", uid)],
                order="create_date desc",
                limit=20,
            )
        )
        return [
            {
                "id": n.id,
                "message": n.message,
                "is_read": n.is_read,
                "create_date": n.create_date.strftime("%Y-%m-%d %H:%M:%S"),
            }
            for n in notifications
        ]
