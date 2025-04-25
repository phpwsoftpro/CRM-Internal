from odoo import http
from odoo.http import request
from werkzeug.utils import redirect
import urllib
import logging

_logger = logging.getLogger(__name__)


class GmailSyncController(http.Controller):

    @http.route("/odoo/<string:provider>/auth/callback", type="http", auth="user")
    def mail_auth_redirect(self, provider, **kwargs):
        _logger.info(f"🚀 Bắt đầu OAuth với provider: {provider}")

        if provider == "gmail":
            config = request.env["mail.message"].sudo().get_google_config()
            scope = "openid email https://www.googleapis.com/auth/gmail.readonly https://www.googleapis.com/auth/gmail.send"
            params = {
                "client_id": config["client_id"],
                "redirect_uri": config["redirect_uri"],
                "response_type": "code",
                "access_type": "offline",
                "scope": scope,
                "prompt": "consent select_account",
            }
            auth_url = f'{config["auth_uri"]}?{urllib.parse.urlencode(params)}'
            _logger.info(f"🔗 Redirect Google OAuth URL: {auth_url}")
            return redirect(auth_url)

        elif provider == "outlook":
            config = request.env["outlook.mail.sync"].sudo().get_outlook_config()
            params = {
                "client_id": config["client_id"],
                "response_type": "code",
                "redirect_uri": config["redirect_uri"],
                "response_mode": "query",
                "scope": "offline_access Mail.Read",
            }
            auth_url = f'https://login.microsoftonline.com/{config["tenant_id"]}/oauth2/v2.0/authorize?{urllib.parse.urlencode(params)}'
            _logger.info(f"🔗 Redirect Outlook OAuth URL: {auth_url}")
            return redirect(auth_url)

        else:
            _logger.error(f"❌ Provider không hợp lệ: {provider}")
            return "Provider không hợp lệ"

    @http.route("/gmail/user_email", auth="user", type="json")
    def gmail_user_email(self):
        email = (
            request.env["ir.config_parameter"]
            .sudo()
            .get_param("gmail_authenticated_email")
        )
        return {"email": email or ""}
