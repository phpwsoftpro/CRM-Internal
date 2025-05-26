import logging
from odoo import models, fields, api

_logger = logging.getLogger(__name__)
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
        _logger.info("[🔁] Running _ensure_partner_links for contacts: %s", self)
        for contact in self:
            if not contact.email:
                continue

            domain_match = re.search(r"@([\w\-\.]+)", contact.email)
            if not domain_match:
                continue

            domain = domain_match.group(1).lower()
            company_name = (contact.company_name or domain.split(".")[0]).strip()

            company = None

            # 1️⃣ Ưu tiên tìm theo name (chỉ chọn active=True)
            company_by_name = (
                self.env["res.company"]
                .sudo()
                .search(
                    [
                        ("name", "=ilike", company_name),
                        ("active", "=", True),
                    ],
                    limit=1,
                )
            )

            if company_by_name:
                company = company_by_name
            else:
                # 2️⃣ Nếu không có name, tìm theo domain (active=True)
                company_by_domain = (
                    self.env["res.company"]
                    .sudo()
                    .search(
                        [
                            ("x_domain_email", "=", domain),
                            ("active", "=", True),
                        ],
                        limit=1,
                    )
                )
                if company_by_domain:
                    company = company_by_domain

            # 3️⃣ Nếu có công ty active nhưng chưa có domain → gán domain
            if company and not company.x_domain_email:
                company.sudo().write({"x_domain_email": domain})

            # 4️⃣ Nếu không có công ty nào active → tạo mới
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

            # 🔄 Liên kết hoặc tạo res.partner công ty
            company_partner = company.partner_id
            if not company_partner:
                company_partner = (
                    self.env["res.partner"]
                    .sudo()
                    .create(
                        {
                            "name": company.name,
                            "is_company": True,
                        }
                    )
                )
                company.sudo().write({"partner_id": company_partner.id})

            # 🔄 Liên kết hoặc tạo partner cá nhân (contact)
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

            if not contact.partner_id:
                contact.sudo().write({"partner_id": partner.id})


class ResCompany(models.Model):
    _inherit = "res.company"

    x_domain_email = fields.Char(
        string="Domain Email", help="Company domain extracted from email"
    )

    @api.model
    def update_companies_domain(self):
        _logger.info("[🛠️] Updating companies x_domain_email from existing emails...")
        companies = self.sudo().search([("x_domain_email", "=", False)])
        for company in companies:
            if company.partner_id and company.partner_id.email:
                domain_match = re.search(r"@([\w\-\.]+)", company.partner_id.email)
                if domain_match:
                    domain = domain_match.group(1).lower()
                    _logger.info(
                        "[✅] Updating company %s domain to %s", company.name, domain
                    )
                    company.sudo().write({"x_domain_email": domain})
