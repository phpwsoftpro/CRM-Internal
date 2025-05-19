from odoo import models, fields, api
import requests
import logging
import json
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError
import time
import psycopg2

_logger = logging.getLogger(__name__)


class GmailAccount(models.Model):
    _name = "gmail.account"
    _description = "Gmail Account"

    user_id = fields.Many2one("res.users", string="User", required=True)
    email = fields.Char(string="Email", required=True)
    access_token = fields.Char("Access Token")
    refresh_token = fields.Char("Refresh Token")
    token_expiry = fields.Datetime("Token Expiry")
    last_ui_ping = fields.Datetime("Last UI Ping")


class GmailAccountSyncState(models.Model):
    _name = "gmail.account.sync.state"
    _description = "Gmail Account Sync Metadata"
    _rec_name = "gmail_account_id"

    gmail_account_id = fields.Many2one(
        "gmail.account", required=True, ondelete="cascade", index=True
    )
    last_fetch_at = fields.Datetime(string="Last Fetched At")
    gmail_ids_30_days = fields.Text(string="Gmail IDs in 30 Days (JSON)")


class GmailAccountCron(models.Model):
    _inherit = "gmail.account"

    @api.model
    def cron_fetch_gmail_accounts(self):
        """
        Cron này sẽ fetch các Gmail account có UI đang mở trong 5 phút gần đây.
        Dùng SELECT FOR UPDATE SKIP LOCKED để tránh conflict đồng thời.
        """
        self.env.cr.execute(
            """
            SELECT id FROM gmail_account
            WHERE last_ui_ping IS NOT NULL
            AND last_ui_ping >= NOW() - interval '5 minutes'
            AND access_token IS NOT NULL
            AND refresh_token IS NOT NULL
            ORDER BY id
            FOR UPDATE SKIP LOCKED
        """
        )
        rows = self.env.cr.fetchall()
        account_ids = [row[0] for row in rows]

        if not account_ids:
            _logger.info("⏸ Không có tài khoản Gmail nào cần đồng bộ.")
            return

        for account in self.browse(account_ids):
            try:
                _logger.info(f"🔄 Cron: Fetch Gmail for {account.email}")
                self.env["mail.message"].fetch_gmail_for_account(account)
            except Exception as e:
                _logger.warning(f"⚠️ Lỗi khi đồng bộ Gmail cho {account.email}: {e}")

    def update_last_ui_ping_safe(self, account_id, uid):
        """
        Ghi `last_ui_ping` với retry logic, rollback rõ ràng sau mỗi lỗi transaction.
        """
        retries = 3
        for attempt in range(retries):
            try:
                self.env.cr.execute(
                    """
                    UPDATE gmail_account
                    SET last_ui_ping = NOW(), write_date = NOW(), write_uid = %s
                    WHERE id = %s
                """,
                    (uid, account_id),
                )
                self.env.cr.commit()
                _logger.info(f"✅ Cập nhật last_ui_ping cho account ID {account_id}")
                break

            except psycopg2.errors.SerializationFailure:
                _logger.warning(
                    f"🔁 Conflict khi cập nhật, thử lại ({attempt + 1}/{retries})..."
                )
                self.env.cr.rollback()
                time.sleep(0.3 * (attempt + 1))

            except Exception as e:
                _logger.error(f"❌ Lỗi không thể cập nhật last_ui_ping: {e}")
                self.env.cr.rollback()
                break

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
                try:
                    account.write(
                        {
                            "access_token": new_access_token,
                            "token_expiry": fields.Datetime.to_string(
                                fields.Datetime.now() + timedelta(seconds=expires_in)
                            ),
                        }
                    )
                    _logger.info(f"✅ Refreshed token for {account.email}")
                    return True
                except Exception as e:
                    _logger.warning(f"⚠️ Ghi access_token thất bại (xung đột ghi): {e}")
                    return False
            else:
                _logger.error(
                    f"❌ Không nhận được access_token từ phản hồi: {response.text}"
                )
                return False
        else:
            _logger.error(
                f"❌ Failed to refresh token for {account.email}: {response.text}"
            )
            return False
