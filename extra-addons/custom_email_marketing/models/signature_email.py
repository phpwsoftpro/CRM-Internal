from odoo import models, fields, api
import logging
import base64

_logger = logging.getLogger(__name__)


class MailComposer(models.TransientModel):
    _inherit = "mail.compose.message"

    def _get_user_signature(self, user):
        """Generate unified HTML signature with proper image handling"""
        user = self.env.user

        # Lấy base_url từ cấu hình hệ thống
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        if "localhost" in base_url:
            base_url = (
                self.env["ir.config_parameter"]
                .sudo()
                .get_param("mail.external.url", base_url)
            )
        # Get images in base64
        company_logo_url = (
            f"{base_url}/web/image?model=res.company&id={user.company_id.id}&field=logo"
        )

        # Tạo HTML cho ảnh chỉ khi có ảnh
        if company_logo_url:
            # Nếu có logo công ty, hiển thị logo
            company_logo_url = f"""
                <img src="{company_logo_url}" 
                    alt="{user.company_id.name}" 
                    style="width: 120px; margin-top: 10px; object-fit: contain;">
            """

        signature_html = f"""
            <table style="display: inline-block; text-align: left;">
                <tr>
                    <td style="padding-right: 15px; vertical-align: top;">
                    {company_logo_url or ''}
                    </td>
                    <td style="vertical-align: top;">
                        <div style="margin-bottom: 10px;">
                            <span style="font-size: 16px; color: #2d2d2d; font-weight: bold;">{user.name}</span>
                            <br>
                            <span style="font-size: 14px; color: #45795b;">{user.function or ''}</span>
                            <br>
                            <span style="font-size: 14px; color: #2d2d2d; font-weight: bold;">{user.company_id.name}</span>
                        </div>
                        <hr style="border: none; border-top: 1px solid #ddd; margin: 10px 0;">
                        <div style="margin-bottom: 4px;">
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16" style="color: #666666;">
                                <path d="M3.654 1.328a.678.678 0 0 1 .563-.011c.896.41 2.69 1.88 3.693 3.114.466.57.944 1.154 1.396 1.497l2.536-2.536c.098-.099.226-.13.345-.066.119.063.211.183.24.333l.547 2.715c.037.186-.022.38-.16.517l-1.601 1.602c.285.482.528.959.731 1.415a2.07 2.07 0 0 1-.812.812c-.457.203-.933.446-1.415.73l-1.601-1.601a.677.677 0 0 0-.517-.161l-2.714.548a.678.678 0 0 0-.333.239.678.678 0 0 0 .066.345l2.536 2.536c-.343.452-.927.93-1.497 1.396C3.636 12.82 2.166 14.613 1.757 15.51a.678.678 0 0 1-.354.354C1.37 15.89.886 16 .5 16a.678.678 0 0 1-.5-.22.678.678 0 0 1-.144-.63c.025-.093.184-.497.355-.896.172-.399.41-.926.656-1.41.415-.832.951-1.752 1.636-2.438 1.116-1.116 3.447-2.9 4.325-3.692a.678.678 0 0 0 .104-.815C7.09 5.247 5.313 3.127 4.147 2.32 3.374 1.815 2.22 1.221 1.756.913a.678.678 0 0 1-.332-.563.678.678 0 0 1 .23-.517ZM6.96 5.96c.244-.244.545-.407.877-.477a2.071 2.071 0 0 0-.877-.477Zm1.216-.1a2.071 2.071 0 0 0-.477-.877c.07.332.233.633.477.877Z"/>
                            </svg>
                            <span style="color: #666666; font-size: 13px;">{user.company_id.phone or user.phone}</span>
                        </div>
                        <div style="margin-bottom: 4px;">
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16" style="color: #666666;">
                                <path d="M0 4a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2V4Zm13.86 0H2a.9.9 0 0 0-.8.54l6.8 4.93 6.8-4.93a.9.9 0 0 0-.8-.54ZM2.14 10.46l4.93-3.57L2 4v6h12V4l-5.07 3.6 4.93 3.57a.9.9 0 0 0 .8-.54H2a.9.9 0 0 0-.8.54Z"/>
                            </svg>
                            <span style="color: #666666; font-size: 13px;">{user.email}</span>
                        </div>
                        <div style="margin-bottom: 4px;">
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16" style="color: #666666;">
                                <path d="M2 6.146V9a6 6 0 0 0 12 0V6.146c0-.83-.404-1.508-1.047-1.762a4.002 4.002 0 0 1-.867-.56C10.986 3.412 10 2.81 10 2s.987-1.412 2.086-1.82c.202-.067.414-.157.603-.26.342-.187.511-.412.511-.764 0-.533-.87-.937-2.2-.936C8.94.216 7 1.126 7 2s.94 1.784 2.086 2.18c.201.067.413.156.602.259a4.002 4.002 0 0 1 .867.56C10.596 5.42 10 6.146 10 6.146s-.597-.726-.47-1.5h-1.06c.127.774-.47 1.5-.47 1.5Zm12-2.462c0 .57-.37.888-.893 1.179a5.004 5.004 0 0 1-.493.26c-.291.125-.572.204-.822.204h-.092c.222.492.471.99.77 1.501a6.002 6.002 0 0 0 2.03-1.163V3.684ZM8.055 7.12a.85.85 0 0 1-.55-.32L3.972 4.52c-.21-.243-.45-.22-.605-.072-.154.147-.203.42-.046.652l3.044 2.08c.19.13.5.19.704.103.205-.087.305-.294.305-.594Zm-4.11 1.202c-.18.105-.336.155-.472.157H1a6.003 6.003 0 0 0 2.204 1.164c.366-.57.683-1.139.94-1.697ZM1.8 3.684v1.077c.556.558 1.245.952 2.022 1.11.289.057.574.108.837.157a5.002 5.002 0 0 1-.302-.41A4.002 4.002 0 0 1 2.4 5.047c-.195-.087-.328-.18-.404-.263-.076-.083-.196-.196-.196-.396v-1.7a4.001 4.001 0 0 1 .06-.445c.072-.353.263-.735.477-1.134C2.412 1.07 2.686 1 2.998 1 3.254 1 3.514 1.162 3.797 1.455c.28.288.544.687.783 1.127a4.002 4.002 0 0 1-.977-.025 5.002 5.002 0 0 0-.591.356c-.227.142-.445.306-.675.489C2.667 3.413 2.377 3.608 2.077 3.838a.9.9 0 0 0-.277.156Z"/>
                            </svg>
                            <a href="{user.company_id.website}" style="color: #45795b; text-decoration: none; font-size: 13px;">
                                {user.company_id.website or ''}
                            </a>
                        </div>
                        <div>
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16" style="color: #666666;">
                                <path d="M4 1c-1.105 0-2 .895-2 2s.895 2 2 2 2-.895 2-2-.895-2-2-2zm1 3H3V2h2v2zm6-3c-1.105 0-2 .895-2 2s.895 2 2 2 2-.895 2-2-.895-2-2-2zm1 3h-2V2h2v2zm1 7.775c-.39-.233-1.197-.541-2.308-.894-.278-.087-.626-.107-.992-.064l-1.097.137-.01-.037c-.21-.757-.574-1.49-1.051-2.128-.8-1.056-1.732-1.963-2.415-2.666C6.427 8.676 5.372 9.62 4.5 10.59c-.563.65-.95 1.28-1.245 1.826a5.607 5.607 0 0 0-.66 2.186c.007.14.02.28.04.418C3.108 14.873 3.601 15 4.053 15h7.894c.451 0 .945-.127 1.418-.376a5.617 5.617 0 0 0 .04-.418c-.07-.85-.338-1.625-.66-2.186-.294-.545-.682-1.176-1.245-1.826-.892-.97-1.947-1.914-2.415-2.666-.477-.638-.841-1.37-1.051-2.128l-.01-.037-1.097.137c-.366.043-.714.023-.992-.064-1.111-.353-1.918-.661-2.308-.894a5.617 5.617 0 0 0-.633 2.016 5.617 5.617 0 0 0 .633 2.016C2.82 11.045 3.628 11.353 4.739 11.706c.278.087.626.107.992.064l1.097-.137.01.037c.21.757.574 1.49 1.051 2.128.8 1.056 1.732 1.963 2.415 2.666.872-.97 1.927-1.914 2.415-2.666.477-.638.841-1.37 1.051-2.128l.01-.037 1.097.137c.366.043.714.023.992-.064C13.182 11.353 14.63 10.66 15.63 9.775a5.607 5.607 0 0 0 .01-.418 5.607 5.607 0 0 0-.01-.418c-.612.646-1.307 1.174-2.027 1.576C11.926 11.503 10.92 12 10 12c-.92 0-1.926-.497-2.613-.87C6.473 11.346 5.77 11 5 11H3c-.336 0-.636-.101-.925-.297C1.739 10.422.824 9.528.633 8.616a5.607 5.607 0 0 0-.01-.418c.174-.925.57-1.665 1.113-2.205C2.3 5.312 3.182 5 4.154 5H6.5v-.5C6.5 2.644 5.856 1 4 1h-.5z"/>
                            </svg>
                            <span style="color: #666666; font-size: 13px;">{user.company_id.street or ''}, {user.company_id.city or ''}, {user.company_id.country_id.name or ''}</span>
                        </div>
                    </td>
                </tr>
            </table>
        """
        return signature_html

    def _add_signature_once(self, content):
        """Add signature if it does not already exist"""
        signature_html = self._get_user_signature(self.env.user)
        if signature_html not in content:
            return f"{content}<br>{signature_html}"
        return content

    @api.onchange("composition_mode", "model", "template_id")
    def onchange_template_id(self):
        """Add signature when template changes"""
        if self.body and not self.template_id:
            self.body = self._add_signature_once(self.body)

    @api.model
    def create(self, vals):
        """Override create to add signature"""
        if vals.get("body") and not vals.get("template_id"):
            vals["body"] = self._add_signature_once(vals.get("body"))
        return super(MailComposer, self).create(vals)


class MassMailing(models.Model):
    _inherit = "mailing.mailing"

    def _get_user_signature(self, user):
        """Get unified HTML signature"""
        return self.env["mail.compose.message"]._get_user_signature(user)

    def action_send_mail(self, res_ids=None):
        """Override to add correct signature before sending"""
        if not self.body_html:
            self.body_html = ""

        # Lấy thông tin của người tạo mailing list, hoặc người dùng hiện tại
        user = self.create_uid or self.env.user
        signature_html = self._get_user_signature(user)

        # Thêm chữ ký nếu chưa có
        if signature_html.strip() not in self.body_html:
            self.body_html = f"{self.body_html}<br>{signature_html}"

        # Log thông tin để kiểm tra
        _logger.info(f"Using signature for user: {user.name}, Email: {user.email}")

        return super(MassMailing, self).action_send_mail(res_ids=res_ids)

    def action_test(self):
        """Override test action to add signature"""
        if not self.body_html:
            self.body_html = ""

        signature_html = self._get_user_signature(self.create_uid or self.env.user)
        # Chỉ thêm chữ ký nếu chưa có
        if signature_html.strip() not in self.body_html:
            self.body_html = f"{self.body_html}<br>{signature_html}"

        return super(MassMailing, self).action_test()
