from odoo import models, fields, api
import re


class MailingContact(models.Model):
    _inherit = "mailing.contact"

    partner_id = fields.Many2one("res.partner", string="Linked Partner")

    @api.model_create_multi
    def create(self, vals_list):
        contacts = super().create(vals_list)
        contacts.sudo()._ensure_partner_links()
        return contacts

    def write(self, vals):
        res = super().write(vals)
        if "email" in vals:
            self.sudo()._ensure_partner_links()
        return res

    def _ensure_partner_links(self):
        for contact in self:
            if not contact.email:
                continue

            # Lấy domain từ email
            domain_match = re.search(r"@([\w\-\.]+)", contact.email)
            if not domain_match:
                continue

            domain = domain_match.group(1).lower()
            company_name = domain.split(".")[0].capitalize()

            # Kiểm tra công ty đã tồn tại chưa
            company = (
                self.env["res.company"]
                .sudo()
                .search([("x_domain_email", "=", domain)], limit=1)
            )
            if not company:
                company = (
                    self.env["res.company"]
                    .sudo()
                    .create(
                        {
                            "name": company_name,
                            "x_domain_email": domain,
                        }
                    )
                )

            # Kiểm tra partner đã tồn tại chưa
            partner = (
                self.env["res.partner"]
                .sudo()
                .search([("email", "=", contact.email)], limit=1)
            )

            # Tạo partner nếu chưa tồn tại
            if not partner:
                # Tạo partner công ty trước (nếu chưa có)
                company_partner = (
                    self.env["res.partner"]
                    .sudo()
                    .search(
                        [("is_company", "=", True), ("name", "=", company_name)],
                        limit=1,
                    )
                )

                if not company_partner:
                    company_partner = (
                        self.env["res.partner"]
                        .sudo()
                        .create(
                            {
                                "name": company_name,
                                "is_company": True,
                                "company_id": company.id,
                            }
                        )
                    )

                # Tạo partner cá nhân
                partner = (
                    self.env["res.partner"]
                    .sudo()
                    .create(
                        {
                            "name": contact.name or contact.email.split("@")[0],
                            "email": contact.email,
                            "company_id": company.id,
                            "parent_id": company_partner.id,  # Liên kết với partner công ty
                        }
                    )
                )

            # Cập nhật partner_id cho contact
            if not contact.partner_id:
                contact.sudo().write({"partner_id": partner.id})

    def send_email(self, subject, body):
        """Giả lập hàm gửi email"""
        for contact in self:
            history_vals = {
                "contact_id": contact.id,
                "company_id": (
                    contact.partner_id.company_id.id if contact.partner_id else False
                ),
                "subject": subject,
                "body": body,
                "state": "sent",
            }
            self.env["mailing.history"].create(history_vals)


class ResCompany(models.Model):
    _inherit = "res.company"

    x_domain_email = fields.Char(
        string="Domain Email", help="Company domain extracted from email"
    )
