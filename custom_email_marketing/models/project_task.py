from odoo import models, fields, api
from datetime import datetime, timedelta
from pathlib import Path
import logging

_logger = logging.getLogger(__name__)


class ProjectTask(models.Model):
    _inherit = "project.task"

    remaining_days = fields.Char(
        string="Remaining Time", compute="_compute_remaining_days"
    )
    priority = fields.Selection(
        [("0", "Low"), ("1", "Medium"), ("2", "High")], string="Priority", default="1"
    )
    has_new_log = fields.Boolean(string="New Log Note", default=False)
    new_log_count = fields.Integer(string="New Log Note Count", default=0)
    connected_task_ids = fields.Many2many(
        "project.task",
        "project_task_connection_rel",
        "task_id",
        "connected_task_id",
        string="Connected Tasks",
    )
    cover_image = fields.Binary("Cover Image")

    @api.model
    def create(self, vals):
        record = super(ProjectTask, self).create(vals)
        if "cover_image" in vals and vals.get("cover_image"):
            attachment = self.env["ir.attachment"].browse(vals["cover_image"])
            if attachment.exists():
                record.message_post(
                    body="Cover image set", attachment_ids=[(4, attachment.id)]
                )
        return record

    def write(self, vals):
        result = super(ProjectTask, self).write(vals)
        for record in self:
            if "cover_image" in vals and vals.get("cover_image"):
                attachment = self.env["ir.attachment"].browse(vals["cover_image"])
                if attachment.exists():
                    record.message_post(
                        body="Cover image updated", attachment_ids=[(4, attachment.id)]
                    )
        return result

    @api.depends("date_deadline")
    def _compute_remaining_days(self):
        for task in self:
            if task.date_deadline:
                # Chuyển đổi deadline sang datetime với timezone của hệ thống
                deadline = fields.Datetime.to_datetime(task.date_deadline)

                # Chuyển deadline sang timezone của user
                deadline = fields.Datetime.context_timestamp(task, deadline)

                # Lấy thời gian hiện tại theo timezone của user
                now = fields.Datetime.context_timestamp(task, fields.Datetime.now())

                # Tính khoảng cách thời gian
                remaining = deadline - now

                # Format lại hiển thị
                task.remaining_days = (
                    f"{remaining.days} days → {deadline.strftime('%I:%M%p %d/%m/%Y')}"
                )
            else:
                task.remaining_days = "No Deadline"

    def action_move_to_project(self):
        return {
            "name": "Move Task to Another Project",
            "type": "ir.actions.act_window",
            "res_model": "move.task.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {"default_task_id": self.id},
        }

    def message_post(self, **kwargs):
        """Override message_post to track new log notes"""
        message = super(ProjectTask, self).message_post(**kwargs)

        # Check if this is a note (not a regular comment)
        if (
            kwargs.get("message_type") == "comment"
            and kwargs.get("subtype_xmlid") == "mail.mt_note"
        ):

            # Update counter for other users
            other_users = self.message_follower_ids.mapped(
                "partner_id.user_ids"
            ).filtered(lambda u: u.id != self.env.user.id)

            if other_users:
                self.sudo().write(
                    {"has_new_log": True, "new_log_count": self.new_log_count + 1}
                )

        if message and message.attachment_ids:
            # Filter to get only image attachments
            image_attachments = message.attachment_ids.filtered(
                lambda a: a.mimetype and a.mimetype.startswith("image/")
            )

            # Make sure we have at least one image
            if image_attachments and not self.cover_image:
                # Get the first image attachment only
                first_image = image_attachments[0]

                # Try different field names that might be used for the Kanban card image
                try:
                    # Option 1: displayed_image_id (Odoo 14+)
                    if hasattr(self, "displayed_image_id"):
                        self.sudo().write({"displayed_image_id": first_image.id})

                    # Option 2: kanban_image (some custom implementations)
                    elif hasattr(self, "kanban_image"):
                        self.sudo().write({"kanban_image": first_image.id})

                    # Option 3: cover_image as a binary field
                    elif hasattr(self, "cover_image"):
                        self.sudo().write({"cover_image": first_image.datas})

                    # Option 4: For Odoo 15+, preview_image field
                    elif hasattr(self, "preview_image"):
                        self.sudo().write({"preview_image": first_image.datas})
                except Exception as e:
                    _logger.error("Error setting task image: %s", str(e))
        return message

    def action_view_task(self):
        """Action to view task and reset notification"""
        self.ensure_one()
        # Reset notification state
        self.write({"has_new_log": False, "new_log_count": 0})

        # Return form view action
        return {
            "name": self.name,
            "type": "ir.actions.act_window",
            "res_model": "project.task",
            "res_id": self.id,
            "view_mode": "form",
            "view_type": "form",
            "target": "current",
        }

    def action_reply_email(self):
        """Mở form nhập nội dung và Message-ID khi reply email"""
        wizard_model = self.env["send.task.email.wizard"]  # Import gián tiếp
        return {
            "type": "ir.actions.act_window",
            "name": "Reply Email",
            "res_model": wizard_model._name,  # Sử dụng model name từ Odoo ORM
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_email_to": self.partner_id.email,  # Điền email khách hàng
            },
        }

    # Notification
    # @api.model
    # def create(self, vals):
    #     task = super().create(vals)
    #     message = f'{self.env.user.name} created task "{task.name}"'

    #     # 🔴 Gửi realtime
    #     self.env["bus.bus"]._sendone(
    #         (self.env.cr.dbname, "notification_channel", self.env.uid),
    #         "notification",
    #         {"message": message},
    #     )

    #     # ✅ Lưu lại
    #     self.env["custom.notification"].create({
    #         "user_id": self.env.uid,
    #         "message": message,
    #     })

    #     return task

    # def write(self, vals):
    #     res = super().write(vals)
    #     for task in self:
    #         message = f'{self.env.user.name} updated "{task.name}"'
    #         self.env["bus.bus"]._sendone(
    #             (self.env.cr.dbname, "notification_channel", self.env.uid),
    #             "notification",
    #             {"message": message},
    #         )
    #         self.env["custom.notification"].create({
    #             "user_id": self.env.uid,
    #             "message": message,
    #         })
    #     return res

    # def message_post(self, **kwargs):
    #     result = super().message_post(**kwargs)
    #     if kwargs.get("body"):
    #         for task in self:
    #             message = f'{self.env.user.name} commented on "{task.name}"'
    #             self.env["bus.bus"]._sendone(
    #                 (self.env.cr.dbname, "notification_channel", self.env.uid),
    #                 "notification",
    #                 {"message": message},
    #             )
    #             self.env["custom.notification"].create({
    #                 "user_id": self.env.uid,
    #                 "message": message,
    #             })
    #     return result
    def action_open_in_new_tab(self):
        """Open the task in a new tab using client action"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': '/web#id=%d&model=project.task&view_type=form' % self.id,
            'target': 'new',
        }
