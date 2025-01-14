from odoo import models, fields


class CustomEmailWizard(models.TransientModel):
    _name = "custom.email.wizard"
    _description = "Custom Email Wizard"

    partner_id = fields.Many2one("res.partner", string="Contact", required=True)
    email_to = fields.Char(string="To", required=True)
    subject = fields.Char(string="Subject", required=True)
    body = fields.Text(string="Body", required=True)

    def send_email(self):
        mail_values = {
            "subject": self.subject,
            "body_html": self.body,
            "email_to": self.email_to,
        }
        self.env["mail.mail"].create(mail_values).send()
