from odoo import models, fields, api


class MassMailing(models.Model):
    _inherit = "mailing.mailing"

    # Thêm trường mới cho chiến dịch email
    campaign_type = fields.Selection(
        [("promotional", "Promotional"), ("informational", "Informational")],
        string="Campaign Type",
        default="promotional",
        help="Loại chiến dịch email.",
    )

    # Ghi đè hàm gửi email để thêm logic kiểm tra loại chiến dịch
    @api.model
    def send_mail(self):
        for record in self:
            if record.campaign_type == "promotional":
                # Logic tùy chỉnh cho chiến dịch quảng cáo
                self.env["mail.mail"].create(
                    {
                        "subject": f"[Promotional] {record.subject}",
                        "body_html": record.body_html,
                        "email_to": record.email_to,
                    }
                )
            else:
                # Logic cho chiến dịch thông tin
                super(MassMailing, record).send_mail()

    # Ví dụ kế thừa logic tạo mẫu email
    def create_email_template(self):
        # Logic tùy chỉnh nếu cần
        return super(MassMailing, self).create_email_template()
