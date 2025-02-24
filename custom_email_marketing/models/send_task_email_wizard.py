from odoo import models, fields, api
from odoo.exceptions import UserError

class SendTaskEmailWizard(models.TransientModel):
    _name = 'send.task.email.wizard'
    _description = 'Wizard gửi email mới cho Task'

    email_to = fields.Char(string="To", required=True)
    email_subject = fields.Char(string="Subject", required=True)
    body_html = fields.Html(string="Body", required=True, sanitize=False) 
    message_id = fields.Char(string="Message-ID", help="Nhập Message-ID từ Gmail khi reply")
    attachment_ids = fields.Many2many('ir.attachment', string="File đính kèm")

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
        """Lấy mặc định Customer email khi mở wizard"""
        res = super(SendTaskEmailWizard, self).default_get(fields_list)
        if 'default_email_to' in self.env.context:
            res['email_to'] = self.env.context.get('default_email_to')
        
        signature = self._get_signature_template()
        res['body_html'] = f"<p><br/></p>{signature}"
        return res

    def send_email(self):
        """Gửi email phản hồi theo Message-ID nhập từ Gmail"""
        if not self.email_to:
            raise UserError("Vui lòng nhập địa chỉ email người nhận!")

        task = self.env['project.task'].browse(self.env.context.get('active_id'))
        attachment_ids = self.attachment_ids.ids if self.attachment_ids else []

        # Xác định headers nếu là email phản hồi
        headers = {}
        if self.message_id:
            headers['In-Reply-To'] = f"<{self.message_id}>"
            headers['References'] = f"<{self.message_id}>"

        mail_values = {
            'subject': self.email_subject,
            'body_html': self.body_html,
            'email_to': self.email_to,
            'email_from': self.env.user.email or 'no-reply@example.com',
            'reply_to': self.env.user.email,
            'headers': headers,
            'attachment_ids': [(6, 0, attachment_ids)] if attachment_ids else [],
        }

        mail = self.env['mail.mail'].create(mail_values)
        mail.send()
        if task:
            task.message_post(
                body=f"📧 Email sent to: {self.email_to}\nSubject: {self.email_subject}",
                subtype_xmlid="mail.mt_note",
            )
