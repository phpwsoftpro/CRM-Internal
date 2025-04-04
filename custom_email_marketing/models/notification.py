import logging
from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)


class ProjectTask(models.Model):
    _inherit = "project.task"

    def _send_stage_change_notification(self, from_stage, to_stage):
        message = (
            self.env["mail.message"]
            .sudo()
            .create(
                {
                    "model": "project.task",
                    "res_id": self.id,
                    "message_type": "notification",
                    "subject": f"Task moved: {self.name}",
                    "body": f"<p><b>{self.name}</b> was moved from <b>{from_stage}</b> to <b>{to_stage}</b></p>",
                    "author_id": self.env.user.partner_id.id,
                }
            )
        )

        for user in self.user_ids:
            existing = (
                self.env["mail.notification"]
                .sudo()
                .search(
                    [
                        ("mail_message_id", "=", message.id),
                        ("res_partner_id", "=", user.partner_id.id),
                    ],
                    limit=1,
                )
            )

            if not existing:
                self.env["mail.notification"].sudo().create(
                    {
                        "mail_message_id": message.id,
                        "res_partner_id": user.partner_id.id,
                        "notification_type": "inbox",
                        "is_read": False,
                    }
                )

    def _send_create_notification(self):
        message = (
            self.env["mail.message"]
            .sudo()
            .create(
                {
                    "model": "project.task",
                    "res_id": self.id,
                    "message_type": "notification",
                    "subject": f"New Task Created: {self.name}",
                    "body": f"<p>A new task <b>{self.name}</b> has been created in project <b>{self.project_id.name}</b>.</p>",
                    "author_id": self.env.user.partner_id.id,
                }
            )
        )

        for user in self.user_ids:
            existing = (
                self.env["mail.notification"]
                .sudo()
                .search(
                    [
                        ("mail_message_id", "=", message.id),
                        ("res_partner_id", "=", user.partner_id.id),
                    ],
                    limit=1,
                )
            )

            if not existing:
                self.env["mail.notification"].sudo().create(
                    {
                        "mail_message_id": message.id,
                        "res_partner_id": user.partner_id.id,
                        "notification_type": "inbox",
                        "is_read": False,
                    }
                )

    def message_post(self, **kwargs):
        res = super().message_post(**kwargs)

        # Gửi notification cho người được tag
        partner_ids = kwargs.get("partner_ids", [])
        notified_partner_ids = set(partner_ids)

        # Gửi thêm cho người được assign nếu chưa có
        for user in self.user_ids:
            if user.partner_id.id not in notified_partner_ids:
                notified_partner_ids.add(user.partner_id.id)

        # Gửi thông báo đến tất cả partner đã tổng hợp
        for partner_id in notified_partner_ids:
            existing = (
                self.env["mail.notification"]
                .sudo()
                .search(
                    [
                        ("mail_message_id", "=", res.id),
                        ("res_partner_id", "=", partner_id),
                    ],
                    limit=1,
                )
            )
            if not existing:
                self.env["mail.notification"].sudo().create(
                    {
                        "mail_message_id": res.id,
                        "res_partner_id": partner_id,
                        "notification_type": "inbox",
                        "is_read": False,
                    }
                )

        return res

    @api.model
    def create(self, vals):
        task = super().create(vals)
        task._send_create_notification()
        return task

    def write(self, vals):
        stage_before_map = {rec.id: rec.stage_id.name for rec in self}
        result = super().write(vals)

        if "stage_id" in vals:
            for rec in self:
                from_stage = stage_before_map.get(rec.id)
                to_stage = rec.stage_id.name
                if from_stage != to_stage:
                    rec._send_stage_change_notification(from_stage, to_stage)

        return result
