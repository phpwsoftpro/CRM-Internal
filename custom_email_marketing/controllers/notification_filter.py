import logging
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class ProjectNotificationController(http.Controller):
    @http.route("/project/notifications", type="json", auth="user")
    def get_all_notifications(self):
        partner_id = request.env.user.partner_id.id
        notifications = []

        _logger.info(f"🔎 Đang lấy thông báo cho partner_id: {partner_id}")

        # Tìm các message liên quan đến project.task mà được gửi đến partner này
        task_messages = (
            request.env["mail.message"]
            .sudo()
            .search(
                [
                    ("model", "=", "project.task"),
                    ("notification_ids.res_partner_id", "=", partner_id),
                ],
                order="date desc",
                limit=50,
            )
        )

        _logger.info(
            f"📥 Tìm thấy {len(task_messages)} thông báo được gửi đến partner_id: {partner_id}"
        )

        for msg in task_messages:
            notifications.append(
                {
                    "id": msg.id,
                    "subject": msg.subject,
                    "body": msg.body,
                    "author": msg.author_id.name if msg.author_id else "System",
                    "date": msg.date.strftime("%Y-%m-%d %H:%M:%S"),
                    "model": msg.model,
                    "res_id": msg.res_id,
                }
            )

        return {"result": notifications}
