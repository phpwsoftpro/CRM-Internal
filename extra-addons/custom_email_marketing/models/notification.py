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

        all_users = self.env["res.users"].sudo().search([("share", "=", False)])
        for user in all_users:
            self.env["mail.notification"].sudo().create(
                {
                    "mail_message_id": message.id,
                    "res_partner_id": user.partner_id.id,
                    "notification_type": "inbox",
                    "is_read": False,
                }
            )

    def _send_create_notification(self, user):
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

        # Chỉ gửi thông báo nếu là comment hoặc log (không gửi khi system log tự động)
        if kwargs.get("message_type") == "comment":
            all_users = self.env["res.users"].sudo().search([("share", "=", False)])
            for user in all_users:
                self.env["mail.notification"].sudo().create(
                    {
                        "mail_message_id": res.id,
                        "res_partner_id": user.partner_id.id,
                        "notification_type": "inbox",
                        "is_read": False,
                    }
                )

        return res

    @api.model
    def create(self, vals):
        task = super().create(vals)

        all_users = self.env["res.users"].sudo().search([])  # 👈 lấy tất cả user
        for user in all_users:
            task._send_create_notification(user)

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
