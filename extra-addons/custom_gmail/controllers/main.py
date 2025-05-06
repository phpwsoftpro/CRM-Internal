from odoo import http
from odoo.http import request


class GmailSyncController(http.Controller):

    # @http.route('/custom_gmail/gmail_inbox', type='http', auth='user', website=True)
    # def gmail_inbox(self):
    #     return request.render('custom_gmail.gmail_custom_ui')

    # @http.route('/custom_gmail/get_email_details', type='json', auth='user')
    # def get_email_details(self, email_id):
    #     message = request.env['mail.message'].sudo().browse(int(email_id))
    #     return {
    #         'subject': message.subject or "No Subject",
    #         'body': message.body or "No Content",
    #     }
    @http.route("/gmail/user_email", auth="user", type="json")
    def gmail_user_email(self):
        gmail_email = (
            request.env["ir.config_parameter"]
            .sudo()
            .get_param("gmail_authenticated_email")
        )
        return {"gmail_email": gmail_email or ""}

    @http.route("/outlook/user_email", auth="user", type="json")
    def outlook_user_email(self):
        outlook_email = (
            request.env["ir.config_parameter"]
            .sudo()
            .get_param("outlook_authenticated_email")
        )
        return {"outlook_email": outlook_email or ""}
