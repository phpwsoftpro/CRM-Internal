from odoo import models, fields, api


class MailingMailing(models.Model):
    _inherit = "mailing.mailing"

    test_subject = fields.Many2one(
        "mailing.mailtext", string="Mail Template", ondelete="set null"
    )

    @api.model
    def default_get(self, fields_list):
        vals = super().default_get(fields_list)
        default_template = self.env["mailing.mailtext"].search(
            [], limit=1, order="id ASC"
        )
        if default_template:
            vals["test_subject"] = default_template.id
            vals["body_arch"] = default_template.text_mailtest
        return vals

    @api.onchange("test_subject")
    def _onchange_test_subject(self):
        if self.test_subject and self.state == "draft":
            self.body_arch = self.test_subject.text_mailtest
