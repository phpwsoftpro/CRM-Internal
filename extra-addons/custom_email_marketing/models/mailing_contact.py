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

            # 🔍 1. Tìm hoặc tạo res.company
            company = (
                self.env["res.company"]
                .sudo()
                .search([("x_domain_email", "=", domain)], limit=1)
            )

            if not company:
                # Nếu domain chưa có, thì kiểm tra tên công ty đã có chưa
                existing_company_name = (
                    self.env["res.company"]
                    .sudo()
                    .search([("name", "=", company_name)], limit=1)
                )
                if company and not company.x_domain_email:
                    company.sudo().write({"x_domain_email": domain})
                elif not company:
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

            # 🔍 2. Tìm hoặc tạo partner công ty liên kết với res.company
            company_partner = (
                self.env["res.partner"]
                .sudo()
                .search(
                    [
                        ("is_company", "=", True),
                        ("id", "=", company.partner_id.id),
                    ],
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
                        }
                    )
                )
                company.sudo().write({"partner_id": company_partner.id})

            # 🔍 3. Tìm hoặc tạo partner cá nhân (contact)
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

            # 🔄 4. Gán partner_id nếu chưa gán
            if not contact.partner_id:
                contact.sudo().write({"partner_id": partner.id})


class ResCompany(models.Model):
    _inherit = "res.company"

    x_domain_email = fields.Char(
        string="Domain Email", help="Company domain extracted from email"
    )
