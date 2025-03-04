from odoo import models, fields, api
from .industries import INDUSTRY_SELECTION
from odoo.exceptions import ValidationError

import logging

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    last_activity_date = fields.Datetime(
        string="Last Email Activity",
        compute="_compute_last_activity_date",
        help="Date of last email sent to this contact",
    )

    last_modified_date = fields.Datetime(
        string="Last Modified Date (GMT+7)",
        compute="_compute_last_modified_date",
        store=True,
    )
    industry = fields.Selection(
        INDUSTRY_SELECTION,
        string="Industry",
    )
    state_id = fields.Many2one("res.country.state", string="State/Region")
    timezone = fields.Char(string="Timezone")
    description = fields.Text(string="Description Company")
    linkedin_link = fields.Char(string="LinkedIn Link")
    message_ids = fields.One2many(
        "mail.message",
        "res_id",
        string="Messages",
        domain=[("model", "=", "res.partner")],
    )
    company_owner_id = fields.Many2one("res.users", string="Company Owner")
    contact_owner_id = fields.Many2one("res.users", string="Contact Owner")
    send_again = fields.Boolean(string="Send Again")
    lead_status = fields.Selection(
        [
            ("new", "New"),
            ("open", "Open"),
            ("in_progress", "In Progress"),
            ("open_deal", "Open Deal"),
            ("unqualified", "Unqualified"),
            ("attempted_to_contact", "Attempted to Contact"),
            ("connected", "Connected"),
            ("bad_timing", "Bad Timing"),
        ],
        string="Lead Status",
    )
    tech_stack_ids = fields.Many2many("tech.stack", string="Area (Techstack)")
    email = fields.Char(string="Email", required=True)
    website = fields.Char(string="Website")

    @api.model
    def message_get_reply_to(self):
        reply_to = super(ResPartner, self).message_get_reply_to()
        return reply_to

    @api.depends("write_date")
    def _compute_last_activity_date(self):
        for record in self:
            record.last_activity_date = record.write_date
    @api.model
    def create(self, vals):
        if 'name' in vals:
            existing_company = self.search([('name', '=', vals['name'])], limit=1)
            if existing_company:
                raise ValidationError("The company name already exists! Please choose another name.")
        return super(ResPartner, self).create(vals)
    @api.constrains("email", "website")
    def _check_unique_email_website(self):
        for record in self:
            # Check duplicate email
            if record.email:
                existing_email = self.env["res.partner"].search(
                    [("email", "=", record.email), ("id", "!=", record.id)], limit=1
                )
                if existing_email:
                    # Send warning notification to frontend
                    self.env["bus.bus"]._sendone(
                        self.env.user.partner_id,
                        "simple_notification",
                        {
                            "title": "Duplicate Email Detected",
                            "message": f"The email '{record.email}' is already in use.",
                            "type": "warning",  # Types: success, warning, danger, info
                        },
                    )
                    # Raise ValidationError to stop creation
                    raise ValidationError(
                        f"The email '{record.email}' is already in use. Please use a unique email."
                    )

            # Check duplicate website
            if record.website:
                existing_website = self.env["res.partner"].search(
                    [("website", "=", record.website), ("id", "!=", record.id)], limit=1
                )
                if existing_website:
                    # Send warning notification to frontend
                    self.env["bus.bus"]._sendone(
                        self.env.user.partner_id,
                        "simple_notification",
                        {
                            "title": "Duplicate Website Detected",
                            "message": f"The website '{record.website}' is already in use.",
                            "type": "warning",
                        },
                    )
                    # Raise ValidationError to stop creation
                    raise ValidationError(
                        f"The website '{record.website}' is already in use. Please use a unique website."
                    )

    def action_open_mail_composer(self):
        self.ensure_one()
        # Get the current user's formatted email
        user_email = self.env.user.partner_id.email_formatted
        company_email = self.env.user.company_id.email_formatted

        ctx = {
            "default_model": "res.partner",
            "default_res_ids": [self.id],
            "default_composition_mode": "comment",
            "force_email": True,
            "default_email_from": user_email or company_email,
            "default_author_id": self.env.user.partner_id.id,
            "default_email_to": self.email,
            "default_recipient_ids": [(6, 0, [self.id])],
            "default_partner_ids": [(6, 0, [self.id])],
            "show_email_from": True,
            "mail_notify_force_send": True,
            "default_subject": f"{self.name}",
        }

        return {
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "mail.compose.message",
            "views": [(False, "form")],
            "target": "new",
            "context": ctx,
        }
