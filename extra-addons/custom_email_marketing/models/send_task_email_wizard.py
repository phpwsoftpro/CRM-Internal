from odoo import models, fields, api
from odoo.exceptions import UserError


class TaskEmailHistory(models.Model):
    _name = "task.email.history"
    _description = "Store last email details per task"

    task_id = fields.Many2one("project.task", string="Task", required=True, ondelete="cascade")
    user_id = fields.Many2one("res.users", string="User", required=True)
    last_email_to = fields.Char(string="Last Recipient Email") 
    last_subject = fields.Char(string="Last Subject")
    last_message_id = fields.Char(string="Last Message-ID")
    last_body_html = fields.Html(string="Last Body", sanitize=False)  
    last_email_cc = fields.Char(string="Last CC", sanitize=False)
    _sql_constraints = [
        (
            "task_user_unique",
            "unique(task_id, user_id)",
            "Only one email history per task and user is allowed!",
        )
    ]


class SendTaskEmailWizard(models.TransientModel):
    _name = "send.task.email.wizard"
    _description = "Wizard gửi email mới cho Task"

    email_to = fields.Char(string="To", required=True)
    email_subject = fields.Char(string="Subject", required=True)
    body_html = fields.Html(string="Body", required=True, sanitize=False)
    message_id = fields.Char(
        string="Message-ID", help="Nhập Message-ID từ Gmail khi reply"
    )
    attachment_ids = fields.Many2many("ir.attachment", string="File đính kèm")
    task_id = fields.Many2one("project.task", string="Related Task")
    email_cc = fields.Char(string="CC", help="Nhập nhiều email cách nhau bằng dấu phẩy hoặc chấm phẩy")
    def _get_signature_template(self):
        """Generate HTML signature template for current user"""
        user = self.env.user
        company = self.env.company

        signature_template = f"""
        <div style="margin-top: 20px; padding-top: 10px; border-top: 1px solid #e5e5e5;">
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
            <table cellpadding="0" cellspacing="0" style="font-family: Poppins, sans-serif; color: #333333; width: 100%; max-width: 600px;">
                <tr>
                    <td style="width: 150px; vertical-align: top; padding-right: 20px;">
                        <img src="/web/image/res.company/{company.id}/logo" alt="{company.name}" style="width: 120px; height: auto;"/>
                    </td>
                    <td style="vertical-align: top;">
                        <div style="font-size: 18px; font-weight: 650; margin-bottom: 5px;">Vanessa Ha</div>
                        <div style="color: black; margin-bottom: 5px; font-size: 15px; font-weight: 500;">Project Manager</div>
                        <div style="margin-bottom: 10px; font-weight: 600;">WSOFTPRO</div>
                        <hr />
                        <div style="margin: 4px 0;">
                            <span>📞</span> <a href="tel:+84393558941" style="color: black; margin-left: 10px; font-size: 15px;">(+84) 393 558 941</a>
                        </div>
                        <div style="margin: 4px 0;">
                            <span>✉️</span> <a href="mailto:vanessa@wsoftpro.com" style="color: black; margin-left: 10px; font-size: 15px;">vanessa@wsoftpro.com</a>
                        </div>
                        <div style="margin: 4px 0;">
                            <span>🌐</span> <a href="https://wsoftpro.com/" target="_blank" style="color: black; margin-left: 10px; font-size: 15px;">https://wsoftpro.com/</a>
                        </div>
                        <div style="margin: 4px 0;">
                            <span>📍</span> <span style="color: black; margin-left: 10px; font-size: 15px;">7/26 Nguyen Hong, Dong Da, Hanoi, Vietnam</span>
                        </div>
                    </td>
                </tr>
            </table>
        </div>
        """
        return signature_template

    @api.model
    def default_get(self, fields_list):
        """Lấy mặc định Customer email khi mở wizard và lưu trữ thông tin email theo task"""
        res = super(SendTaskEmailWizard, self).default_get(fields_list)

        # Get the current task ID
        active_id = self.env.context.get("active_id")
        if active_id:
            res["task_id"] = active_id

            # Get last email data for this task and user
            email_history = self.env["task.email.history"].search(
                [("task_id", "=", active_id), ("user_id", "=", self.env.user.id)],
                limit=1,
            )

            if email_history:
                res["email_to"] = email_history.last_email_to
                res["email_subject"] = email_history.last_subject
                res["message_id"] = email_history.last_message_id
                res["body_html"] = email_history.last_body_html
                res["email_cc"] = email_history.last_email_cc

        # Default email recipient
        if "default_email_to" in self.env.context:
            res["email_to"] = self.env.context.get("default_email_to")

        # Default signature
        if not res.get("body_html"):
            signature = self._get_signature_template()
            res["body_html"] = f"<p><br/></p>{signature}"

        return res

    def save_draft(self):
        """Lưu tạm thời Subject, Message-ID và Body mà không gửi email"""
        self.ensure_one()  # Đảm bảo chỉ có một record được thao tác

        task = self.env["project.task"].browse(self.env.context.get("active_id"))
        if not task:
            raise UserError("Không tìm thấy Task để lưu tạm!")

        # Lấy dữ liệu email đã lưu trước đó
        email_history = self.env["task.email.history"].search(
            [("task_id", "=", task.id), ("user_id", "=", self.env.user.id)], limit=1
        )

        history_vals = {
            "task_id": task.id,
            "user_id": self.env.user.id,
            "last_email_to": self.email_to,
            "last_subject": self.email_subject,
            "last_message_id": self.message_id,
            "last_body_html": self.body_html, 
            "last_email_cc": self.email_cc,
        }

        if email_history:
            email_history.write(history_vals)
        else:
            self.env["task.email.history"].create(history_vals)

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Lưu thành công!",
                "message": "Email subject, Message-ID và nội dung đã được lưu tạm thời.",
                "type": "success",
                "sticky": False,
            },
        }

    def send_email(self):
        """Gửi email phản hồi theo Message-ID nhập từ Gmail và lưu thông tin gửi"""
        if not self.email_to:
            raise UserError("Vui lòng nhập địa chỉ email người nhận!")

        task = self.env["project.task"].browse(self.env.context.get("active_id"))
        attachment_ids = self.attachment_ids.ids if self.attachment_ids else []

        # Xác định headers nếu là email phản hồi
        headers = {}
        if self.message_id:
            headers["In-Reply-To"] = f"<{self.message_id}>"
            headers["References"] = f"<{self.message_id}>"
        mail_server = self.env['ir.mail_server'].search([], limit=1)  
        email_from = mail_server.smtp_user if mail_server else self.env.user.email or "no-reply@example.com"

        mail_values = {
            "subject": self.email_subject,
            "body_html": self.body_html,
            "email_to": self.email_to,
            "email_cc": self.email_cc,
            "email_from": email_from,  
            "reply_to": email_from,  
            "headers": headers,
            "attachment_ids": [(6, 0, attachment_ids)] if attachment_ids else [],
        }

        mail = self.env["mail.mail"].create(mail_values)
        mail.send()

        # Save the email details for this task
        if task:
            email_history = self.env["task.email.history"].search(
                [("task_id", "=", task.id), ("user_id", "=", self.env.user.id)], limit=1
            )

            history_vals = {
                "last_subject": self.email_subject,
                "last_message_id": self.message_id,
            }

            if email_history:
                email_history.write(history_vals)
            else:
                self.env["task.email.history"].create(
                    {"task_id": task.id, "user_id": self.env.user.id, **history_vals}
                )

            # Create a mail.message directly instead of using message_post
            self.env["mail.message"].create(
                {
                    "body": f"""
                    <div>
                        <div style="margin-top: 15px; border-top: 1px solid #ddd; padding-top: 15px;">
                            {self.body_html}
                        </div>
                        {f'<div style="margin-top: 10px;"><strong>Attachments:</strong> {len(attachment_ids)} files</div>' if attachment_ids else ''}
                    </div>
                """,
                    "subject": self.email_subject,
                    "message_type": "comment",
                    "subtype_id": self.env.ref("mail.mt_comment").id,
                    "model": "project.task",
                    "res_id": task.id,
                    "author_id": self.env.user.partner_id.id,
                    "email_from": self.env.user.email,
                    "attachment_ids": (
                        [(6, 0, attachment_ids)] if attachment_ids else []
                    ),
                    "date": fields.Datetime.now(),
                }
            )

            return {"type": "ir.actions.act_window_close"}
