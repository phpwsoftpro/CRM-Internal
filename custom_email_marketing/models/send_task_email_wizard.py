from odoo import models, fields, api
from odoo.exceptions import UserError

class SendTaskEmailWizard(models.TransientModel):
    _name = 'send.task.email.wizard'
    _description = 'Wizard gửi email mới cho Task'

    email_to = fields.Char(string="To", required=True)
    email_subject = fields.Char(string="Subject", required=True)
    body_html = fields.Html(string="Body", required=True, sanitize=True) 
    message_id = fields.Char(string="Message-ID", help="Nhập Message-ID từ Gmail khi reply")
    attachment_ids = fields.Many2many('ir.attachment', string="File đính kèm")

    def _get_signature_template(self):
        """Generate HTML signature template for current user"""
        user = self.env.user
        company = self.env.company

        signature_template = f"""
        <div style="margin-top: 20px; padding-top: 10px; border-top: 1px solid #e5e5e5;">
            <table cellpadding="0" cellspacing="0" style="font-family: Arial, sans-serif; color: #333333; width: 100%; max-width: 600px;">
                <tr>
                    <td style="width: 150px; vertical-align: top; padding-right: 20px;">
                        <img src="/web/image/res.company/{company.id}/logo" alt="{company.name}" style="width: 120px; height: auto;"/>
                    </td>
                    <td style="vertical-align: top;">
                        <div style="font-size: 16px; font-weight: bold; margin-bottom: 5px;">Vanessa Ha</div>
                        <div style="color: #4CAF50; margin-bottom: 5px;">Nhân viên</div>
                        <div style="margin-bottom: 10px;">{company.name}</div>
                        
                        <div style="margin: 4px 0;">
                            <span style="color: #666;">📞</span> {user.phone or ''}
                        </div>
                        <div style="margin: 4px 0;">
                            <span style="color: #666;">✉️</span> {user.email or ''}
                        </div>
                        <div style="margin: 4px 0;">
                            <span style="color: #666;">🌐</span> {company.website or ''}
                        </div>
                        <div style="margin: 4px 0;">
                            <span style="color: #666;">📍</span> {company.street or ''} {company.street2 or ''}, {company.city or ''}, {company.country_id.name or ''}
                        </div>
                    </td>
                </tr>
            </table>
        </div>
        """
        return signature_template

    @api.model
    def default_get(self, fields_list):
        """Lấy chữ ký mặc định khi mở wizard"""
        res = super(SendTaskEmailWizard, self).default_get(fields_list)
        signature = self._get_signature_template()
        res['body_html'] = f"<p><br/></p>{signature}"
        return res

    def send_email(self):
        """Gửi email phản hồi theo Message-ID nhập từ Gmail"""
        if not self.email_to:
            raise UserError("Vui lòng nhập địa chỉ email người nhận!")

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
            'attachment_ids': [(6, 0, self.attachment_ids.ids)],
        }
        
        mail = self.env['mail.mail'].create(mail_values)
        mail.send()