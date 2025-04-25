import requests
import json
import logging
import urllib
from odoo.http import request, Controller
from datetime import datetime, timedelta
from odoo import http
from werkzeug.utils import redirect

_logger = logging.getLogger(__name__)


class GmailAuthController(Controller):

    @http.route("/gmail/auth/start", type="http", auth="user", methods=["GET"])
    def gmail_auth_start(self, **kw):
        _logger.info("🔐 Gmail OAuth flow started from /gmail/auth/start")
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
        _logger.info(f"🔗 Redirecting to Google auth URL: {auth_url}")
        return redirect(auth_url)

    @http.route("/odoo/gmail/auth/callback", type="http", auth="user", methods=["GET"])
    def gmail_auth_callback(self, **kw):
        _logger.info(f"📥 Gmail callback received with params: {kw}")
        code = kw.get("code")
        if not code:
            _logger.error("❌ Missing authorization code in callback.")
            return "Missing code"

        config = request.env["mail.message"].sudo().get_google_config()
        data = {
            "code": code,
            "client_id": config["client_id"],
            "client_secret": config["client_secret"],
            "redirect_uri": config["redirect_uri"],
            "grant_type": "authorization_code",
        }

        _logger.info("🔄 Exchanging code for tokens...")
        token_res = requests.post(config["token_uri"], data=data)
        token_data = token_res.json()

        if "error" in token_data:
            _logger.error(f"❌ Token exchange failed: {token_data}")
            return (
                f"Token Error: {token_data.get('error_description', 'Unknown error')}"
            )

        access_token = token_data.get("access_token")
        refresh_token = token_data.get("refresh_token")
        expires_in = token_data.get("expires_in")

        _logger.info("📧 Fetching user info from Google...")
        user_info = requests.get(
            "https://openidconnect.googleapis.com/v1/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
        ).json()

        gmail_email = user_info.get("email")
        if not gmail_email:
            _logger.error(
                f"❌ Failed to get Gmail email! UserInfo: {json.dumps(user_info, indent=2)}"
            )
            return request.render(
                "custom_gmail.gmail_auth_error",
                {
                    "error": "Không thể xác định email Gmail. Vui lòng thử lại.",
                },
            )

        _logger.info(f"📌 Gmail authenticated email: {gmail_email}")

        # Tạo hoặc cập nhật account
        account = (
            request.env["gmail.account"]
            .sudo()
            .search(
                [
                    ("user_id", "=", request.env.user.id),
                    ("email", "=", gmail_email),
                ],
                limit=1,
            )
        )

        if not account:
            _logger.info("➕ Creating new Gmail account record")
            account = (
                request.env["gmail.account"]
                .sudo()
                .create(
                    {
                        "user_id": request.env.user.id,
                        "email": gmail_email,
                        "access_token": access_token,
                        "refresh_token": refresh_token,
                        "token_expiry": datetime.utcnow()
                        + timedelta(seconds=expires_in),
                        "provider": "gmail",
                    }
                )
            )
        else:
            _logger.info("♻️ Updating existing Gmail account record")
            account.write(
                {
                    "access_token": access_token,
                    "refresh_token": refresh_token or account.refresh_token,
                    "token_expiry": datetime.utcnow() + timedelta(seconds=expires_in),
                    "provider": "gmail",
                }
            )

        # Gọi đồng bộ mail
        _logger.info(f"📬 Fetching Gmail for account ID {account.id}")
        request.env["mail.message"].sudo().fetch_gmail_for_account(account.id)

        _logger.info("✅ Gmail sync complete. Closing popup.")
        return """
            <html><body>
                <script>
                    window.opener.postMessage("gmail-auth-success", "*");
                    window.close();
                </script>
                <p>Đang hoàn tất kết nối Gmail...</p>
            </body></html>
        """
