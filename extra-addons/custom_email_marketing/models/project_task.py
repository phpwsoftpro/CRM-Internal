from odoo import models, fields, api
from datetime import datetime, timedelta

class ProjectTask(models.Model):
    _inherit = 'project.task'

    # remaining_days = fields.Char(string="Remaining Time", compute="_compute_remaining_days")
    # priority = fields.Selection([
    #     ('0', 'Low'),
    #     ('1', 'Normal'),
    #     ('2', 'Medium'),
    #     ('3', 'High')
    # ], string="Priority", default='1')
    has_new_log = fields.Boolean(string="New Log Note", default=False)
    new_log_count = fields.Integer(string="New Log Note Count", default=0)
    # @api.depends('date_deadline')
    # def _compute_remaining_days(self):
    #     for task in self:
    #         if task.date_deadline:
    #             # Chuyển đổi deadline sang datetime với timezone của hệ thống
    #             deadline = fields.Datetime.to_datetime(task.date_deadline)

    #             # Chuyển deadline sang timezone của user
    #             deadline = fields.Datetime.context_timestamp(task, deadline)

    #             # Lấy thời gian hiện tại theo timezone của user
    #             now = fields.Datetime.context_timestamp(task, fields.Datetime.now())

    #             # Tính khoảng cách thời gian
    #             remaining = deadline - now

    #             # Format lại hiển thị
    #             task.remaining_days = f"{remaining.days} days → {deadline.strftime('%I:%M%p %d/%m/%Y')}"
    #         else:
    #             task.remaining_days = "No Deadline"
    def action_move_to_project(self):
        return {
            'name': 'Move Task to Another Project',
            'type': 'ir.actions.act_window',
            'res_model': 'move.task.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_task_id': self.id},
        }
    def message_post(self, **kwargs):
        """Override message_post to track new log notes"""
        message = super().message_post(**kwargs)
        
        # Check if this is a note (not a regular comment)
        if (kwargs.get('message_type') == 'comment' and 
            kwargs.get('subtype_xmlid') == 'mail.mt_note'):
            
            # Update counter for other users
            other_users = self.message_follower_ids.mapped('partner_id.user_ids').filtered(
                lambda u: u.id != self.env.user.id
            )
            
            if other_users:
                self.sudo().write({
                    'has_new_log': True,
                    'new_log_count': self.new_log_count + 1
                })
        
        return message

    def action_view_task(self):
        """Action to view task and reset notification"""
        self.ensure_one()
        # Reset notification state
        self.write({
            'has_new_log': False,
            'new_log_count': 0
        })
        
        # Return form view action
        return {
            'name': self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'project.task',
            'res_id': self.id,
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'current',
        }
    def action_reply_email(self):
        """Mở form nhập nội dung và Message-ID khi reply email"""
        wizard_model = self.env['send.task.email.wizard']  # Import gián tiếp
        return {
            'type': 'ir.actions.act_window',
            'name': 'Reply Email',
            'res_model': wizard_model._name,  # Sử dụng model name từ Odoo ORM
            'view_mode': 'form',
            'target': 'new',
        }