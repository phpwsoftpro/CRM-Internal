import logging
import requests
import msal
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class OutlookAuthController(http.Controller):

    @http.route("/odoo/outlook/auth/callback", type="http", auth="user")
    def outlook_callback(self, **kw):
        _logger.info("Received OAuth callback from Outlook")

        code = kw.get("code")
        error = kw.get("error")

        if error:
            _logger.error(f"OAuth error: {error}")
            return "<h3>❌ Authentication failed. Please try again.</h3>"

        if not code:
            return "<h3>❌ No authentication code received.</h3>"

        config = request.env["outlook.mail.sync"].sudo().get_outlook_config()

        token_url = config["token_uri"]
        data = {
            "client_id": config["client_id"],
            "client_secret": config["client_secret"],
            "code": code,
            "redirect_uri": config["redirect_uri"],
            "grant_type": "authorization_code",
        }

        token_res = requests.post(token_url, data=data)

        if token_res.status_code != 200:
            _logger.error(f"Failed to get token: {token_res.text}")
            return "<h3>❌ Failed to get token from Outlook.</h3>"

        token_data = token_res.json()
        access_token = token_data.get("access_token")
        refresh_token = token_data.get("refresh_token")

        if not access_token:
            _logger.error(f"No access token received: {token_data}")
            return "<h3>❌ No access token received.</h3>"

        # Lấy thông tin user Outlook
        user_info_res = requests.get(
            "https://graph.microsoft.com/v1.0/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        if user_info_res.status_code != 200:
            _logger.error(f"Failed to fetch user info: {user_info_res.text}")
            return "<h3>❌ Failed to fetch user info.</h3>"

        user_info = user_info_res.json()
        outlook_email = user_info.get("mail") or user_info.get("userPrincipalName")

        # Lưu vào gmail.account (chung cho cả Gmail và Outlook)
        request.env["gmail.account"].sudo().create(
            {
                "user_id": request.env.user.id,
                "email": outlook_email,
                "access_token": access_token,
                "refresh_token": refresh_token,
                "provider": "outlook",
            }
        )

        _logger.info(f"✅ Outlook account {outlook_email} linked successfully!")

        # Trả về giao diện đẹp + đóng popup
        return """
            <html>
                <head><title>Outlook Connected</title></head>
                <body>
                    <h3>✅ Outlook account connected successfully!</h3>
                    <script>
                        window.opener.postMessage("outlook-auth-success", "*");
                        setTimeout(function() {
                            window.close();
                        }, 1500);
                    </script>
                    <p>This window will close automatically...</p>
                </body>
            </html>
        """

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
