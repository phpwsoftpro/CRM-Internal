from odoo import http
from odoo.http import request

class DeepSeekController(http.Controller):

    @http.route('/deepseek/analyze_gmail_body', type='json', auth='user', csrf=False)
    def analyze_gmail_body(self, body=None, **kwargs):
        if not body:
            return {'status': 'fail', 'message': 'Missing email body'}

        try:
            # ✅ Gọi AI thật sự (ở đây dùng Discuss channel làm ví dụ bạn nói)
            channel = request.env['discuss.channel'].sudo()
            ai_summary = channel._get_deepseek_r1_response(prompt=body)

            # ✅ Lấy thông tin từ frontend
            subject = kwargs.get("subject", "không có tiêu")
            email = kwargs.get("email_from") or kwargs.get("email", "")
            body_html = kwargs.get("body_html") or kwargs.get("body", "")

            task_name = f"{email} - {subject}"
            deepseek_text = f"{body_html}\n\n📌 AI Phân Tích:\n{ai_summary}"

            # ✅ Tạo task
            task = request.env['project.task'].sudo().create({
                'name': task_name,
                'deepseek_text': deepseek_text,
                'project_id': 955, # nhấn nút phân tích nó sẽ thay tạo task mới project_id là id của bản ghi đó nếu
                # kiểm tra trong project có id nào
            })

            return {
                'status': 'ok',
                'task_id': task.id,
                'ai_summary': ai_summary,
                'message': 'Task created successfully'
            }

        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
