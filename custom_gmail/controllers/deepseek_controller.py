from odoo import http
from odoo.http import request

class DeepSeekAnalyzeController(http.Controller):

    @http.route('/deepseek/analyze_gmail_body', type='json', auth='user', csrf=False)
    def analyze_gmail_body(self, body=None, **kwargs):
        if not body:
            return {"status": "fail", "message": "Missing email body"}

        # Gọi lại hàm đã có trong model mail.channel
        try:
            channel = request.env['discuss.channel'].sudo()
            ai_response = channel._get_deepseek_r1_response(prompt=body)
            return {
                "status": "ok",
                "ai_summary": ai_response,
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
            }
