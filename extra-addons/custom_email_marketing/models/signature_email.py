from odoo import models, fields
import logging

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = "res.users"

    email_signature = fields.Html(
        string="Email Signature", help="Signature to include in emails."
    )
    email_image = fields.Binary(
        string="Email Image", help="Image to include in email signature."
    )


class MailingMailing(models.Model):
    _inherit = "mailing.mailing"

    def send_mail(self, **kwargs):
        current_user = self.env.user
        default_signature = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("default_email_signature", default="")
        )

        for mailing in self:
            # Lấy thông tin người dùng hoặc sử dụng chữ ký mặc định
            user_signature = current_user.email_signature or default_signature
            image_url = (
                f"/web/image?model=res.users&id={current_user.id}&field=email_image"
                if current_user.email_image
                else ""
            )

            # Log đường dẫn ảnh
            _logger.info("Image URL: %s", image_url)

            # Chữ ký HTML
            signature_html = f"""
            <div style="font-family: Arial, sans-serif; font-size: 14px; color: #333;">
                {user_signature}
                {f'<img src="{image_url}" alt="User Image" style="width: 80px; height: 80px; border-radius: 50%; margin-top: 10px;">' if image_url else ''}
            </div>
            """

            # Log chữ ký HTML
            _logger.info("Generated Signature HTML: %s", signature_html)

            # Gắn chữ ký vào nội dung email
            mailing.body_html += signature_html

            # Log nội dung body_html sau khi thêm chữ ký
            _logger.info("Updated Email Body HTML: %s", mailing.body_html)

        return super(MailingMailing, self).send_mail(**kwargs)
