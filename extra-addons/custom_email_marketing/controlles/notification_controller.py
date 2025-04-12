from odoo import http
from odoo.http import request


class ProjectNotificationController(http.Controller):

    @http.route("/project/notifications", type="json", auth="user")
    def get_project_notifications(self):
        messages = (
            request.env["mail.message"]
            .sudo()
            .search(
                [
                    ("model", "=", "project.task"),
                    ("message_type", "=", "notification"),
                    ("res_id", "!=", False),
                ],
                order="create_date desc",
                limit=50,
            )
        )

        result = []
        for msg in messages:
            result.append(
                {
                    "subject": msg.subject,
                    "body": msg.body,
                    "date": msg.date.strftime("%Y-%m-%d %H:%M:%S"),
                    "author": msg.author_id.name,
                }
            )

        return result
