# import requests
# import json
# import logging
# from datetime import datetime
# from odoo import models, fields, api, _
# from odoo.http import request, Controller, route
# import pytz 

# _logger = logging.getLogger(__name__)

# import requests
# import json
# import logging
# from datetime import datetime
# from odoo import models, fields, api, _

# _logger = logging.getLogger(__name__)


# class GmailMessage(models.Model):
#     _inherit = 'mail.message'

#     gmail_id = fields.Char(string="Gmail ID", index=True)
#     gmail_body = fields.Text(string="Body")
#     is_gmail = fields.Boolean(string="Is Gmail Message", default=False)
#     date_received = fields.Datetime(string="Date Received")
#     email_sender = fields.Char(string="Email Sender")
#     email_receiver = fields.Char(string="Email Receiver")
#     email_cc = fields.Char(string="Email CC")
#     last_fetched_email_id = fields.Char(string="Last Fetched Email ID", help="Stores the last fetched Gmail ID to optimize fetching new emails.")


#     @api.model
#     def get_google_config(self):
#         """
#         Load Google API configuration for OAuth2.
#         """
#         _logger.debug("Loading Google API configuration.")
#         return {
#             "client_id": "934598997197-13d2tluslcltooi7253r1s1rkafj601h.apps.googleusercontent.com",
#             "client_secret": "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",
#             "auth_uri": "https://accounts.google.com/o/oauth2/auth",
#             "token_uri": "https://oauth2.googleapis.com/token",
#             "redirect_uri": "http://localhost:8070/odoo/gmail/auth/callback",
#         }

#     @api.model

#     @api.model
#     def action_redirect_gmail_auth(self):
#         """
#         Fetch Gmail messages using the stored access token. If fetching fails, redirect
#         to Google's OAuth2 consent screen for authentication.
#         """
#         _logger.debug("Checking if a Gmail access token exists.")

#         config_params = self.env['ir.config_parameter'].sudo()
#         access_token = config_params.get_param('gmail_access_token')

#         if access_token:
#             _logger.info("Using existing Gmail access token: %s", access_token)
#             try:
#                 self.fetch_gmail_messages(access_token)
#                 return {'type': 'ir.actions.client', 'tag': 'reload'}  # Refresh the current view
#             except Exception as e:
#                 _logger.error("Failed to fetch Gmail messages with existing token: %s", str(e))

#         _logger.debug("No valid access token found or token failed. Redirecting to Google's OAuth2 consent screen.")
#         config = self.get_google_config()
#         scope = 'https://www.googleapis.com/auth/gmail.readonly'
#         auth_url = (
#             f"{config['auth_uri']}?response_type=code"
#             f"&client_id={config['client_id']}"
#             f"&redirect_uri={config['redirect_uri']}"
#             f"&scope={scope}"
#             f"&access_type=offline"
#         )
#         _logger.info("Redirect URL generated: %s", auth_url)
#         return {
#             'type': 'ir.actions.act_url',
#             'url': auth_url,
#             'target': 'new',
#         }

#     def parse_date(self, raw_date):
#         """
#         Attempt to parse a date string with multiple known formats.
#         """
#         # Remove any extra text like "(CST)" or "(UTC)"
#         cleaned_date = raw_date.split('(')[0].strip()

#         formats = [
#             '%a, %d %b %Y %H:%M:%S %z',  # Standard RFC 2822 with timezone offset
#             '%a, %d %b %Y %H:%M:%S %Z',  # Includes timezone abbreviation (e.g., CST)
#             '%d %b %Y %H:%M:%S %z',      # Date without day of the week
#             '%d %b %Y %H:%M:%S %Z',      # Date without day of the week, with timezone abbreviation
#             '%a, %d %b %Y %H:%M:%S GMT', # Date with GMT
#         ]

#         for fmt in formats:
#             try:
#                 # Attempt parsing with the current format
#                 parsed_date = datetime.strptime(cleaned_date, fmt)
#                 # Ensure consistent UTC timezone
#                 if not parsed_date.tzinfo:
#                     parsed_date = pytz.utc.localize(parsed_date)
#                 return parsed_date.strftime('%Y-%m-%d %H:%M:%S')
#             except ValueError:
#                 continue

#         # Log an error if all formats fail
#         _logger.error("Failed to parse date: %s. Tried formats: %s", raw_date, formats)
#         return None

#     @api.model
#     def fetch_gmail_messages(self, access_token):
#         """
#         Fetch the latest 5 Gmail messages and process new emails only.
#         Avoids fetching beyond the last 5 messages for optimization.
#         """
#         _logger.debug("Fetching Gmail messages with access token.")
#         url = 'https://gmail.googleapis.com/gmail/v1/users/me/messages'
#         headers = {'Authorization': f'Bearer {access_token}'}
        
#         processed_messages = []
#         next_page_token = None
#         fetched_count = 0
#         batch_size = 15  # Fetch emails in batches of 5
#         max_messages = 15  # Fetch only the latest 5 messages
#         last_fetched_email_id = self.env['ir.config_parameter'].sudo().get_param('gmail_last_fetched_email_id')

#         # Retrieve only the last 5 Gmail IDs stored in Odoo for comparison
#         existing_gmail_ids = set(self.search([], order='create_date desc', limit=15).mapped('gmail_id'))
#         _logger.debug("Fetched latest 5 Gmail IDs from Odoo for quick lookup.")

#         while fetched_count < max_messages:
#             params = {'maxResults': batch_size}  # Fetch in batches of 5
#             if next_page_token:
#                 params['pageToken'] = next_page_token

#             response = requests.get(url, headers=headers, params=params)
#             _logger.debug("Gmail messages fetch response: %s", response.text)

#             if response.status_code != 200:
#                 _logger.error("Failed to fetch Gmail messages: %s", response.text)
#                 raise ValueError(f"Failed to fetch Gmail messages: {response.text}")

#             messages = response.json().get('messages', [])
#             next_page_token = response.json().get('nextPageToken')

#             if not messages:
#                 break  # Stop if there are no more messages

#             for msg in messages:
#                 if fetched_count >= max_messages:
#                     _logger.info("Reached maximum number of messages to fetch: %d", max_messages)
#                     break

#                 gmail_id = msg.get('id')

#                 # Stop if we already fetched this ID in a previous batch
#                 if gmail_id in existing_gmail_ids:
#                     _logger.info("Skipping already fetched Gmail ID: %s", gmail_id)
#                     continue  

#                 # Fetch email details
#                 message_url = f'https://gmail.googleapis.com/gmail/v1/users/me/messages/{gmail_id}?format=full'
#                 message_response = requests.get(message_url, headers=headers)

#                 _logger.info("Fetched raw email data for Gmail ID %s: %s", gmail_id, message_response.text)

#                 if message_response.status_code == 200:
#                     message_data = message_response.json()
#                     payload = message_data.get('payload', {})
#                     headers_list = payload.get('headers', [])

#                     # Extract required email fields
#                     subject = next((header.get('value') for header in headers_list if header.get('name') == 'Subject'), 'No Subject')
#                     sender = next((header.get('value') for header in headers_list if header.get('name') == 'From'), 'Unknown Sender')
#                     receiver = next((header.get('value') for header in headers_list if header.get('name') == 'To'), 'Unknown Receiver')
#                     cc = next((header.get('value') for header in headers_list if header.get('name') == 'Cc'), '')
#                     raw_date = next((header.get('value') for header in headers_list if header.get('name') == 'Date'), None)
#                     date_received = self.parse_date(raw_date) if raw_date else None

#                     # Extract full email body
#                     body = ''
#                     if 'parts' in payload:
#                         for part in payload['parts']:
#                             if part.get('mimeType') == 'text/plain':
#                                 body = part.get('body', {}).get('data', '')
#                                 break

#                     # Decode base64 content if available
#                     if body:
#                         import base64
#                         body = base64.urlsafe_b64decode(body).decode('utf-8')

#                     _logger.info("Creating a new mail.message record for Gmail ID: %s", gmail_id)
#                     created_message = self.create({
#                         'gmail_id': gmail_id,
#                         'is_gmail': True,
#                         'body': body,
#                         'subject': subject,
#                         'date_received': date_received,
#                         'message_type': 'email',
#                         'author_id': self.env.user.partner_id.id,
#                         'email_sender': sender,
#                         'email_receiver': receiver,
#                         'email_cc': cc,
#                     })
#                     processed_messages.append({
#                         'id': gmail_id,
#                         'subject': subject,
#                         'sender': sender,
#                         'receiver': receiver,
#                         'cc': cc,
#                         'date_received': date_received,
#                         'body': body,
#                     })
#                     fetched_count += 1

#                     # Create notification with full body content
#                     notification = self.env['mail.notification'].sudo().create({
#                         'mail_message_id': created_message.id,
#                         'res_partner_id': self.env.user.partner_id.id,
#                         'notification_type': 'inbox',
#                         'is_read': False,
#                     })
                    
#                     # Debugging: Print notification details
#                     _logger.info("Notification Created: ID=%s, Message ID=%s, Receiver ID=%s, Read Status=%s, Content=%s",
#                                 notification.id, notification.mail_message_id.id, notification.res_partner_id.id, notification.is_read, body)

#                     # Update last fetched email ID
#                     self.env['ir.config_parameter'].sudo().set_param('gmail_last_fetched_email_id', gmail_id)

#             if fetched_count >= max_messages or not next_page_token:
#                 break  # Stop after reaching max messages or no more pages

#         return processed_messages

#     @api.model
#     def scheduled_gmail_sync(self):
#         """
#         Scheduled action to fetch Gmail messages periodically.
#         Ensures the access token is valid or refreshes it if expired.
#         """
#         _logger.debug("Scheduled Gmail sync invoked.")

#         # Retrieve the stored access token
#         config = self.get_google_config()
#         access_token = self.env['ir.config_parameter'].sudo().get_param('gmail_access_token')

#         if not access_token:
#             _logger.error("Access token not available. Attempting to refresh token.")

#             # Try to refresh the access token using the refresh token
#             refresh_token = self.env['ir.config_parameter'].sudo().get_param('gmail_refresh_token')
#             if refresh_token:
#                 _logger.debug("Refreshing access token using refresh token.")
#                 payload = {
#                     'client_id': config['client_id'],
#                     'client_secret': config['client_secret'],
#                     'refresh_token': refresh_token,
#                     'grant_type': 'refresh_token',
#                 }
#                 response = requests.post(config['token_uri'], data=payload)
#                 _logger.debug("Refresh token response: %s", response.text)

#                 if response.status_code == 200:
#                     token_data = response.json()
#                     access_token = token_data.get('access_token')
#                     self.env['ir.config_parameter'].sudo().set_param('gmail_access_token', access_token)
#                     _logger.info("Access token refreshed successfully.")
#                 else:
#                     _logger.error("Failed to refresh access token: %s", response.text)
#                     return
#             else:
#                 _logger.error("Refresh token not available. Cannot sync Gmail messages.")
#                 return

#         try:
#             # Fetch Gmail messages using the stored token
#             gmail_messages = self.sudo().fetch_gmail_messages(access_token)

#             # Process Gmail messages
#             current_partner_id = self.env.user.partner_id.id
#             discuss_channel = self.env['discuss.channel'].sudo().search([('name', '=', 'Inbox')], limit=1)

#             if not discuss_channel:
#                 _logger.debug("Creating Discuss Inbox channel.")
#                 discuss_channel = self.env['discuss.channel'].sudo().create({
#                     'name': 'Inbox',
#                     'channel_type': 'chat',
#                     'channel_partner_ids': [(4, current_partner_id)],
#                 })

#             for message in gmail_messages:
#                 try:
#                     _logger.info("Creating Discuss message for Gmail ID: %s", message['id'])
#                     created_message = self.sudo().create({
#                         'gmail_id': message['id'],
#                         'subject': message['subject'] or "No Subject",
#                         'body': message['body'] or "No Body",
#                         'message_type': 'email',
#                         'model': 'discuss.channel',
#                         'res_id': discuss_channel.id,
#                         'author_id': current_partner_id,
#                     })

#                     # Create notification
#                     _logger.info("Creating notification for Gmail ID: %s", message['id'])
#                     self.env['mail.notification'].sudo().create({
#                         'mail_message_id': created_message.id,
#                         'res_partner_id': current_partner_id,
#                         'notification_type': 'inbox',
#                         'is_read': False,
#                     })
#                 except Exception as e:
#                     _logger.error("Failed to create Discuss message or notification for Gmail ID: %s. Error: %s", message['id'], str(e))
#         except Exception as e:
#             _logger.error("Error during scheduled Gmail sync: %s", str(e))

# class GmailAuthController(Controller):
#     @route('/odoo/gmail/auth/callback', type='http', auth='user', csrf=False)
#     def gmail_auth_callback(self, **kwargs):
#         """
#         Handle Google OAuth2 callback and extract the access token.
#         """
#         _logger.debug("Google OAuth2 callback invoked.")
#         code = kwargs.get('code')
#         if not code:
#             _logger.error("Authorization code not provided.")
#             return request.render('custom_gmail.gmail_auth_error', {'error': 'Authorization code not provided'})

#         # Get Google API credentials
#         _logger.debug("Fetching Google API configuration.")
#         config = request.env['mail.message'].sudo().get_google_config()

#         # Exchange the authorization code for an access token
#         _logger.debug("Exchanging authorization code for access token.")
#         token_url = config['token_uri']
#         payload = {
#             'code': code,
#             'client_id': config['client_id'],
#             'client_secret': config['client_secret'],
#             'redirect_uri': config['redirect_uri'],
#             'grant_type': 'authorization_code',
#         }
#         headers = {'Content-Type': 'application/x-www-form-urlencoded'}

#         response = requests.post(token_url, data=payload, headers=headers)
#         _logger.debug("Token exchange response: %s", response.text)

#         if response.status_code == 200:
#             _logger.debug("Token exchange successful.")
#             token_data = response.json()
#             access_token = token_data.get('access_token')
#             refresh_token = token_data.get('refresh_token')  # Save the refresh token if provided
#             expires_in = token_data.get('expires_in')

#             _logger.info("Access token successfully obtained.")

#             # Store the token and other data securely in `ir.config_parameter`
#             config_params = request.env['ir.config_parameter'].sudo()
#             _logger.debug("Storing access token in ir.config_parameter.")
#             config_params.set_param('gmail_access_token', access_token)
#             if refresh_token:
#                 _logger.debug("Storing refresh token in ir.config_parameter.")
#                 config_params.set_param('gmail_refresh_token', refresh_token)
#             if expires_in:
#                 _logger.debug("Storing token expiry in ir.config_parameter.")
#                 config_params.set_param('gmail_token_expiry', expires_in)

#             # Refresh token logic: Check expiry and refresh as needed
#             def refresh_access_token():
#                 """Refresh the access token using the refresh token."""
#                 _logger.debug("Refreshing access token.")
#                 refresh_payload = {
#                     'client_id': config['client_id'],
#                     'client_secret': config['client_secret'],
#                     'refresh_token': refresh_token,
#                     'grant_type': 'refresh_token',
#                 }
#                 refresh_response = requests.post(token_url, data=refresh_payload, headers=headers)
#                 _logger.debug("Refresh token response: %s", refresh_response.text)
#                 if refresh_response.status_code == 200:
#                     refresh_data = refresh_response.json()
#                     new_access_token = refresh_data.get('access_token')
#                     _logger.info("Access token refreshed successfully.")
#                     config_params.set_param('gmail_access_token', new_access_token)
#                     return new_access_token
#                 else:
#                     _logger.error("Failed to refresh access token: %s", refresh_response.text)
#                     return None

#             # Trigger Gmail sync using the retrieved token
#             try:
#                 _logger.debug("Initiating Gmail sync.")
#                 gmail_messages = request.env['mail.message'].sudo().fetch_gmail_messages(access_token)
#                 _logger.info("Gmail sync completed successfully.")

#                 # Sync messages and notifications (existing logic)
#                 self.sync_messages_and_notifications(gmail_messages)
#             except Exception as e:
#                 _logger.error("Error during Gmail sync: %s", str(e))
#                 return request.render('custom_gmail.gmail_auth_error', {'error': str(e)})

#             # Redirect to Discuss page after successful sync
#             _logger.info("Redirecting to Discuss after successful Gmail sync.")
#             return request.redirect('/web#menu_id=mail.menu_root_discuss')
#         else:
#             # Log the error and render the error template
#             error_message = response.json()
#             _logger.error("Failed to obtain access token: %s", error_message)
#             request.env['ir.logging'].create({
#                 'name': "Gmail OAuth2 Error",
#                 'type': 'server',
#                 'level': 'error',
#                 'dbname': request.env.cr.dbname,
#                 'message': json.dumps(error_message),
#             })
#             return request.render('custom_gmail.gmail_auth_error', {'error': error_message})

#     def sync_messages_and_notifications(self, gmail_messages):
#         """
#         Sync Gmail messages and create notifications.
#         """
#         current_partner_id = request.env.user.partner_id.id
#         discuss_channel = request.env['discuss.channel'].sudo().search([('name', '=', 'Inbox')], limit=1)

#         if not discuss_channel:
#             _logger.debug("Creating Discuss Inbox channel.")
#             discuss_channel = request.env['discuss.channel'].sudo().create({
#                 'name': 'Inbox',
#                 'channel_type': 'chat',
#                 'channel_partner_ids': [(4, current_partner_id)],
#             })

#         all_created = True
#         for message in gmail_messages:
#             try:
#                 _logger.info("Creating Discuss message for Gmail ID: %s", message['id'])
#                 created_message = request.env['mail.message'].sudo().create({
#                     'gmail_id': message['id'],
#                     'subject': message['subject'] or "No Subject",
#                     'body': message['body'] or "No Body",
#                     'message_type': 'email',
#                     'model': 'discuss.channel',
#                     'res_id': discuss_channel.id,
#                     'author_id': current_partner_id,
#                 })

#                 # Create notification for the created message
#                 _logger.info("Creating notification for Gmail ID: %s", message['id'])
#                 request.env['mail.notification'].sudo().create({
#                     'mail_message_id': created_message.id,
#                     'res_partner_id': current_partner_id,
#                     'notification_type': 'inbox',
#                     'is_read': False,
#                 })
#             except Exception as e:
#                 _logger.error("Failed to create Discuss message or notification for Gmail ID: %s. Error: %s", message['id'], str(e))
#                 all_created = False

#         if not all_created:
#             raise Exception("Failed to create all Discuss messages or notifications.")
import logging
from odoo import models, fields, api

_logger = logging.getLogger(__name__)

class GmailMessage(models.Model):
    _inherit = 'mail.message'

    gmail_id = fields.Char(string="Gmail ID", index=True)
    gmail_body = fields.Text(string="Body")
    is_gmail = fields.Boolean(string="Is Gmail Message", default=False)
    date_received = fields.Datetime(string="Date Received")
    email_sender = fields.Char(string="Email Sender")
    email_receiver = fields.Char(string="Email Receiver")
    email_cc = fields.Char(string="Email CC")
    last_fetched_email_id = fields.Char(string="Last Fetched Email ID", help="Stores the last fetched Gmail ID to optimize fetching new emails.")