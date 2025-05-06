from odoo import models, fields, api
import requests
import logging
from datetime import datetime, timedelta


_logger = logging.getLogger(__name__)


class GmailAccount(models.Model):
    _name = "gmail.account"
    _description = "Gmail Account"

    user_id = fields.Many2one("res.users", string="User", required=True)
    email = fields.Char(string="Email", required=True)
    access_token = fields.Char("Access Token")
    refresh_token = fields.Char("Refresh Token")
    token_expiry = fields.Datetime("Token Expiry")
    last_fetch_at = fields.Datetime(string="Last Fetch At")

    @api.model
    def cron_fetch_gmail_accounts(self):
        accounts = self.sudo().search(
            [("access_token", "!=", False), ("refresh_token", "!=", False)]
        )
        for account in accounts:
            _logger.info(f"🔄 Cron: Fetch Gmail for {account.email}")
            self.env["mail.message"].sudo().fetch_gmail_for_account(account.id)

    def refresh_access_token(self, account):
        config = self.env["mail.message"].sudo().get_google_config()
        if not account.refresh_token:
            _logger.error(f"❌ No refresh token for account {account.email}")
            return False

        payload = {
            "client_id": config["client_id"],
            "client_secret": config["client_secret"],
            "refresh_token": account.refresh_token,
            "grant_type": "refresh_token",
        }

        response = requests.post(config["token_uri"], data=payload)
        if response.status_code == 200:
            tokens = response.json()
            new_access_token = tokens.get("access_token")
            expires_in = tokens.get("expires_in")

            if new_access_token:
                account.write(
                    {
                        "access_token": new_access_token,
                        "token_expiry": datetime.utcnow()
                        + timedelta(seconds=expires_in),
                    }
                )
                _logger.info(f"✅ Refreshed token for {account.email}")
                return True
            else:
                _logger.error(
                    f"❌ Failed to get access_token from refresh response: {response.text}"
                )
                return False
        else:
            _logger.error(
                f"❌ Failed to refresh token for {account.email}: {response.text}"
            )
            return False
