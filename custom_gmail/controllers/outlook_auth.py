from odoo import http
from odoo.http import request
import requests
import logging
import urllib.parse
import werkzeug
import msal
import json

_logger = logging.getLogger(__name__)


class OutlookAuthController(http.Controller):

    @http.route("/outlook/auth/start", type="http", auth="user", methods=["GET"])
    def outlook_auth_start(self, **kw):
        _logger.info("🔐 Outlook OAuth flow started from /outlook/auth/start")

        config = request.env["outlook.mail.sync"].sudo().get_outlook_config()
        scope = "https://graph.microsoft.com/Mail.Read https://graph.microsoft.com/User.Read offline_access"

        params = {
            "client_id": config["client_id"],
            "response_type": "code",
            "redirect_uri": config["redirect_uri"],
            "response_mode": "query",
            "scope": scope,
            "prompt": "select_account",
        }

        auth_url = f"{config['auth_uri']}?{urllib.parse.urlencode(params)}"
        return werkzeug.utils.redirect(auth_url)

    @http.route("/odoo/outlook/auth/callback", type="http", auth="user")
    def outlook_callback(self, **kw):
        _logger.info("📥 Outlook callback received with params: %s", kw)

        code = kw.get("code")
        if not code:
            return """<script>window.opener.postMessage("outlook-auth-missing-code", "*");window.close();</script>"""

        config = request.env["outlook.mail.sync"].sudo().get_outlook_config()

        token_data = {
            "client_id": config["client_id"],
            "client_secret": config["client_secret"],
            "code": code,
            "redirect_uri": config["redirect_uri"],
            "grant_type": "authorization_code",
        }

        response = requests.post(config["token_uri"], data=token_data)
        token_info = response.json()

        if "access_token" not in token_info:
            return """<script>window.opener.postMessage("outlook-auth-token-failed", "*");window.close();</script>"""

        access_token = token_info.get("access_token")
        refresh_token = token_info.get("refresh_token")

        # Lấy email từ Microsoft Graph
        graph_headers = {"Authorization": f"Bearer {access_token}"}
        graph_response = requests.get(
            "https://graph.microsoft.com/v1.0/me", headers=graph_headers
        )

        email = None
        if graph_response.ok:
            user_info = graph_response.json()
            email = user_info.get("mail") or user_info.get("userPrincipalName")

        # Lưu vào res.users
        user = request.env.user.sudo()
        user.write(
            {
                "outlook_access_token": access_token,
                "outlook_refresh_token": refresh_token,
                "outlook_authenticated_email": email or False,
            }
        )

        # ✅ Tạo outlook.account nếu chưa có
        OutlookAccount = request.env["outlook.account"].sudo()
        existing = OutlookAccount.search(
            [
                ("email", "=", email),
                ("user_id", "=", user.id),
            ],
            limit=1,
        )

        if not existing:
            OutlookAccount.create(
                {
                    "email": email,
                    "user_id": user.id,
                }
            )

        return """<script>window.opener.postMessage("outlook-auth-success", "*");window.close();</script>"""

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

    @http.route("/outlook/messages", type="json", auth="user")
    def outlook_messages(self, **kw):
        user = request.env.user.sudo()
        access_token = user.outlook_access_token
        if not access_token:
            return {"status": "error", "message": "No Outlook access token found"}

        url = "https://graph.microsoft.com/v1.0/me/messages?$orderby=receivedDateTime desc&$top=20"
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            _logger.error(f"❌ Failed to fetch Outlook messages: {response.text}")
            return {"status": "error", "message": "Failed to fetch messages"}

        messages = response.json().get("value", [])
        return {
            "status": "ok",
            "messages": [
                {
                    "id": msg["id"],
                    "subject": msg["subject"],
                    "sender": msg.get("sender", {}).get("emailAddress", {}).get("name"),
                    "from": msg.get("from", {}).get("emailAddress", {}).get("address"),
                    "date": msg["receivedDateTime"],
                    "bodyPreview": msg["bodyPreview"],
                }
                for msg in messages
            ],
        }
