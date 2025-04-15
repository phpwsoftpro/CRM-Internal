from odoo import models, fields, api
from .industries import INDUSTRY_SELECTION
from odoo.exceptions import ValidationError
from odoo.fields import Html
import logging
import pytz


class ResPartner(models.Model):
    _inherit = "res.partner"

    last_activity_date = fields.Datetime(
        string="Last Email Activity", compute="_compute_last_activity_date", store=True
    )
    mailing_trace_ids = fields.One2many(
        "mailing.trace", "res_partner_id", string="Email History", store=True
    )

    mail_history_summary = Html(
        string="Mail History Summary",
        compute="_compute_mail_history_summary",
        store=False,
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
    mail_message_ids = fields.One2many(
        comodel_name="mail.message",
        inverse_name="res_id",
        string="Mail History",
        domain=lambda self: [("model", "=", "res.partner")],
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
    company_url = fields.Char(string="Company Link", compute="_compute_company_url")

    @api.model
    def message_get_reply_to(self):
        reply_to = super(ResPartner, self).message_get_reply_to()
        return reply_to

    @api.depends("child_ids.mailing_trace_ids.sent_datetime")
    def _compute_last_modified_date(self):
        for partner in self:
            if partner.is_company:
                traces = self.env["mailing.trace"].search(
                    [
                        ("res_partner_id", "in", partner.child_ids.ids),
                        ("sent_datetime", "!=", False),
                    ]
                )
                dates = [t.sent_datetime for t in traces if t.sent_datetime]
                partner.last_modified_date = max(dates) if dates else False
            else:
                # Optional: để contact rỗng
                partner.last_modified_date = False

    @api.depends("mailing_trace_ids.sent_datetime")
    def _compute_last_activity_date(self):
        for partner in self:
            valid_dates = [
                d for d in partner.mailing_trace_ids.mapped("sent_datetime") if d
            ]
            partner.last_activity_date = max(valid_dates) if valid_dates else False

    @api.depends(
        "mailing_trace_ids.sent_datetime",
        "tech_stack_ids",
        "child_ids.mailing_trace_ids.sent_datetime",
    )
    def _compute_mail_history_summary(self):
        user_tz = self.env.user.tz or "UTC"
        tz = pytz.timezone(user_tz)

        for partner in self:
            lines = []

            if partner.is_company:
                # 📩 Company: 1 dòng email mới nhất từ child_ids
                trace = self.env["mailing.trace"].search(
                    [
                        ("res_partner_id", "in", partner.child_ids.ids),
                        ("sent_datetime", "!=", False),
                    ],
                    order="sent_datetime desc",
                    limit=1,
                )

                if trace:
                    local_dt = trace.sent_datetime.replace(tzinfo=pytz.utc).astimezone(
                        tz
                    )
                    date_str = local_dt.strftime("%d/%m/%Y %H:%M")
                    email = trace.email or "-"

                    # 🔍 Truy subject bằng email + thời điểm gửi
                    subject = "-"
                    if trace.email and trace.sent_datetime:
                        mailing = (
                            self.env["mailing.mailing"]
                            .sudo()
                            .search(
                                [
                                    (
                                        "contact_list_ids.contact_ids.email",
                                        "=",
                                        trace.email,
                                    ),
                                    ("create_date", "<=", trace.sent_datetime),
                                ],
                                order="create_date desc",
                                limit=1,
                            )
                        )
                        subject = mailing.subject or "(No Subject)"

                    lines.append(
                        f"<div style='color:#444; font-weight:400;'>"
                        f"🕒 {date_str} — 📧 {subject} — ✉️ {email} "
                        f"</div>"
                    )
                else:
                    lines.append("<div style='color:#888;'>No recent email sent.</div>")

            else:
                # 📩 Contact: nhiều dòng
                traces = self.env["mailing.trace"].search(
                    [("res_partner_id", "=", partner.id)],
                    order="sent_datetime desc",
                    limit=10,
                )

                for t in traces:
                    if t.sent_datetime:
                        local_dt = t.sent_datetime.replace(tzinfo=pytz.utc).astimezone(
                            tz
                        )
                        date_str = local_dt.strftime("%d/%m/%Y %H:%M")
                    else:
                        date_str = "-"

                    email = t.email or "-"

                    # 🔍 Truy subject như trên
                    subject = "-"
                    if t.email and t.sent_datetime:
                        mailing = (
                            self.env["mailing.mailing"]
                            .sudo()
                            .search(
                                [
                                    (
                                        "contact_list_ids.contact_ids.email",
                                        "=",
                                        t.email,
                                    ),
                                    ("create_date", "<=", t.sent_datetime),
                                ],
                                order="create_date desc",
                                limit=1,
                            )
                        )
                        subject = mailing.subject or "(No Subject)"

                    # 🧠 Tech stack
                    techs = t.res_partner_id.tech_stack_ids.mapped("name")
                    tech_str = ", ".join(techs) if techs else "No Tech"

                    lines.append(
                        f"<div style='color:#444; font-weight:400;'>"
                        f"🕒 {date_str} — 📧 {subject} — ✉️ {email}  — 🧠 {tech_str}"
                        f"</div>"
                    )

            partner.mail_history_summary = (
                "<div style='padding-left:10px;'>" + "".join(lines) + "</div>"
            )

    @api.model
    def create(self, vals):
        if "name" in vals:
            existing_company = self.search([("name", "=", vals["name"])], limit=1)
            if existing_company:
                raise ValidationError(
                    "The company name already exists! Please choose another name."
                )
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

    def action_open_company_in_new_tab(self):
        self.ensure_one()
        if self.parent_id:
            return {
                "type": "ir.actions.act_url",
                "url": f"/web#id={self.parent_id.id}&model=res.partner&view_type=form",
                "target": "new",
            }

    def action_open_contact_in_new_tab(self):
        """Open the contact in a new tab using client action"""
        self.ensure_one()
        return {
            "type": "ir.actions.act_url",
            "url": "/web#id=%d&model=res.partner&view_type=form" % self.id,
            "target": "new",
        }
