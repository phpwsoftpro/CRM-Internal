import logging
import werkzeug
from odoo import http
from odoo.http import request
import msal
import urllib.parse

_logger = logging.getLogger(__name__)


class OutlookAuthController(http.Controller):

    @http.route("/outlook/auth/start", type="http", auth="user", methods=["GET"])
    def outlook_auth_start(self, **kw):

        _logger.info("🔐 Outlook OAuth flow started from /outlook/auth/start")

        # Gọi config từ model outlook.mail.sync

        config = request.env["outlook.mail.sync"].sudo().get_outlook_config()

        scope = "https://graph.microsoft.com/Mail.Read offline_access"

        params = {
            "client_id": config["client_id"],
            "response_type": "code",
            "redirect_uri": config["redirect_uri"],
            "response_mode": "query",
            "scope": scope,
            "prompt": "select_account",
        }

        auth_url = f"https://login.microsoftonline.com/{config['tenant_id']}/oauth2/v2.0/authorize?{urllib.parse.urlencode(params)}"

        _logger.info(f"🔗 Redirecting to Outlook OAuth URL: {auth_url}")

        return werkzeug.utils.redirect(auth_url)

    @http.route("/odoo/outlook/auth/callback", type="http", auth="user")
    def outlook_callback(self, **kw):
        _logger.info("Received OAuth callback from Outlook")

        code = kw.get("code")
        state = kw.get("state")
        error = kw.get("error")

        if error:
            _logger.error(f"OAuth error: {error}")
            return "Authentication failed. Please try again."

        if not code:
            _logger.warning("No code received from Outlook.")
            return "No authentication code received."

        try:
            user = request.env.user.sudo()  # dùng sudo để tránh lỗi nếu không đủ quyền
            user.write(
                {
                    "outlook_auth_code": code,
                    "outlook_auth_state": state,
                }
            )
            _logger.info(f"Saved Outlook auth code for user {user.id}")

            # Sync ngay sau khi đăng nhập
            success = request.env["outlook.mail.sync"].sudo().create_sync_job(user.id)
            if not success:
                return "Authentication succeeded, but email sync failed. Check logs."

            return werkzeug.utils.redirect("/web#action=mail.action_discuss")

        except Exception as e:
            _logger.exception("Exception during Outlook callback handling")
            return f"Unexpected error during sync: {str(e)}"

    @http.route("/outlook/auth", type="http", auth="user")
    def outlook_auth(self):
        config = request.env["outlook.mail.sync"].sudo().get_outlook_config()
        auth_app = msal.ConfidentialClientApplication(
            config["client_id"],
            authority=f"https://login.microsoftonline.com/{config['tenant_id']}",
            client_credential=config["client_secret"],
        )

        auth_url = auth_app.get_authorization_request_url(
            scopes=["https://graph.microsoft.com/Mail.Read"],
            redirect_uri=config["redirect_uri"],
        )

        return request.redirect(auth_url)
