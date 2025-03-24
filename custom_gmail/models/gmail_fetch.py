import requests
import logging
from odoo import models, api

_logger = logging.getLogger(__name__)

class GmailFetch(models.Model):
    _inherit = 'mail.message'

    @api.model
    def action_redirect_gmail_auth(self):
        """
        Fetch Gmail messages using the stored access token. If fetching fails, redirect
        to Google's OAuth2 consent screen for authentication.
        """
        _logger.debug("Checking if a Gmail access token exists.")

        config_params = self.env['ir.config_parameter'].sudo()
        access_token = config_params.get_param('gmail_access_token')

        if access_token:
            _logger.info("Using existing Gmail access token: %s", access_token)
            try:
                self.fetch_gmail_messages(access_token)
                return {'type': 'ir.actions.client', 'tag': 'reload'}
            except Exception as e:
                _logger.error("Failed to fetch Gmail messages with existing token: %s", str(e))

        _logger.debug("No valid access token found or token failed. Redirecting to Google's OAuth2 consent screen.")
        config = self.get_google_config()
        scope = 'https://www.googleapis.com/auth/gmail.readonly'
        auth_url = (
            f"{config['auth_uri']}?response_type=code"
            f"&client_id={config['client_id']}"
            f"&redirect_uri={config['redirect_uri']}"
            f"&scope={scope}"
            f"&access_type=offline"
        )
        _logger.info("Redirect URL generated: %s", auth_url)
        return {
            'type': 'ir.actions.act_url',
            'url': str(auth_url),
            'target': 'new',
        }

    @api.model
    def fetch_gmail_messages(self, access_token):
        """
        Fetch the latest 15 Gmail messages and process new emails only.
        Avoids fetching beyond the last 15 messages for optimization.
        """
        _logger.debug("Fetching Gmail messages with access token.")
        url = 'https://gmail.googleapis.com/gmail/v1/users/me/messages'
        headers = {'Authorization': f'Bearer {access_token}'}
        
        processed_messages = []
        next_page_token = None
        fetched_count = 0
        batch_size = 15  # Fetch emails in batches of 15
        max_messages = 15  # Fetch only the latest 15 messages
        last_fetched_email_id = self.env['ir.config_parameter'].sudo().get_param('gmail_last_fetched_email_id')

        existing_gmail_ids = set(self.search([], order='create_date desc', limit=15).mapped('gmail_id'))
        _logger.debug("Fetched latest 15 Gmail IDs from Odoo for quick lookup.")

        while fetched_count < max_messages:
            params = {'maxResults': batch_size}
            if next_page_token:
                params['pageToken'] = next_page_token

            response = requests.get(url, headers=headers, params=params)
            _logger.debug("Gmail messages fetch response: %s", response.text)

            if response.status_code != 200:
                _logger.error("Failed to fetch Gmail messages: %s", response.text)
                raise ValueError(f"Failed to fetch Gmail messages: {response.text}")

            messages = response.json().get('messages', [])
            next_page_token = response.json().get('nextPageToken')

            if not messages:
                break

            for msg in messages:
                if fetched_count >= max_messages:
                    _logger.info("Reached maximum number of messages to fetch: %d", max_messages)
                    break

                gmail_id = msg.get('id')
                if gmail_id in existing_gmail_ids:
                    _logger.info("Skipping already fetched Gmail ID: %s", gmail_id)
                    continue  

                message_url = f'https://gmail.googleapis.com/gmail/v1/users/me/messages/{gmail_id}?format=full'
                message_response = requests.get(message_url, headers=headers)

                _logger.info("Fetched raw email data for Gmail ID %s: %s", gmail_id, message_response.text)

                if message_response.status_code == 200:
                    message_data = message_response.json()
                    payload = message_data.get('payload', {})
                    headers_list = payload.get('headers', [])

                    subject = next((header.get('value') for header in headers_list if header.get('name') == 'Subject'), 'No Subject')
                    sender = next((header.get('value') for header in headers_list if header.get('name') == 'From'), 'Unknown Sender')
                    receiver = next((header.get('value') for header in headers_list if header.get('name') == 'To'), 'Unknown Receiver')
                    cc = next((header.get('value') for header in headers_list if header.get('name') == 'Cc'), '')
                    raw_date = next((header.get('value') for header in headers_list if header.get('name') == 'Date'), None)
                    date_received = self.parse_date(raw_date) if raw_date else None

                    body = ''
                    if 'parts' in payload:
                        for part in payload['parts']:
                            if part.get('mimeType') == 'text/plain':
                                body = part.get('body', {}).get('data', '')
                                break

                    if body:
                        import base64
                        body = base64.urlsafe_b64decode(body).decode('utf-8')

                    _logger.info("Creating a new mail.message record for Gmail ID: %s", gmail_id)
                    created_message = self.create({
                        'gmail_id': gmail_id,
                        'is_gmail': True,
                        'body': body,
                        'subject': subject,
                        'date_received': date_received,
                        'message_type': 'email',
                        'author_id': self.env.user.partner_id.id,
                        'email_sender': sender,
                        'email_receiver': receiver,
                        'email_cc': cc,
                    })
                    processed_messages.append({
                        'id': gmail_id,
                        'subject': subject,
                        'sender': sender,
                        'receiver': receiver,
                        'cc': cc,
                        'date_received': date_received,
                        'body': body,
                    })
                    fetched_count += 1

                    notification = self.env['mail.notification'].sudo().create({
                        'mail_message_id': created_message.id,
                        'res_partner_id': self.env.user.partner_id.id,
                        'notification_type': 'inbox',
                        'is_read': False,
                    })
                    
                    _logger.info("Notification Created: ID=%s, Message ID=%s, Receiver ID=%s, Read Status=%s, Content=%s",
                                notification.id, notification.mail_message_id.id, notification.res_partner_id.id, notification.is_read, body)

                    self.env['ir.config_parameter'].sudo().set_param('gmail_last_fetched_email_id', gmail_id)

            if fetched_count >= max_messages or not next_page_token:
                break

        return processed_messages