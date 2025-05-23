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
        if "email" in vals or "company_name" in vals:
            self.sudo()._ensure_partner_links()
        return res

    def _ensure_partner_links(self):
        for contact in self:
            if not contact.email:
                continue

            domain_match = re.search(r"@([\w\-\.]+)", contact.email)
            if not domain_match:
                continue

            domain = domain_match.group(1).lower()
            company_name = contact.company_name or domain.split(".")[0].capitalize()

            # 1. Ưu tiên tìm theo domain
            company = (
                self.env["res.company"]
                .sudo()
                .search(
                    [("x_domain_email", "=", domain), ("active", "=", True)], limit=1
                )
            )

            # 2. Nếu không có domain, tìm theo tên công ty
            if not company:
                company = (
                    self.env["res.company"]
                    .sudo()
                    .search(
                        [("name", "=ilike", company_name), ("active", "=", True)],
                        limit=1,
                    )
                )

            # Gán domain nếu tìm được theo name
            if company and not company.x_domain_email:
                company.sudo().write({"x_domain_email": domain})

            # Nếu vẫn không có thì tạo mới
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

            # Tạo hoặc lấy partner công ty
            company_partner = company.partner_id or self.env[
                "res.partner"
            ].sudo().search(
                [("is_company", "=", True), ("name", "=ilike", company_name)], limit=1
            )

            if not company_partner:
                company_partner = (
                    self.env["res.partner"]
                    .sudo()
                    .create(
                        {
                            "name": company_name,
                            "is_company": True,
                        }
                    )
                )
                company.sudo().write({"partner_id": company_partner.id})

            # Tìm hoặc tạo cá nhân liên kết
            partner = (
                self.env["res.partner"]
                .sudo()
                .search([("email", "=", contact.email)], limit=1)
            )

            if not partner:
                partner = (
                    self.env["res.partner"]
                    .sudo()
                    .create(
                        {
                            "name": contact.name or contact.email.split("@")[0],
                            "email": contact.email,
                            "parent_id": company_partner.id,
                        }
                    )
                )

            # Gán lại partner_id
            if not contact.partner_id:
                contact.sudo().write({"partner_id": partner.id})


class ResCompany(models.Model):
    _inherit = "res.company"

    x_domain_email = fields.Char(
        string="Domain Email", help="Company domain extracted from email"
    )
