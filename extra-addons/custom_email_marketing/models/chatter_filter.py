# from odoo import models, fields, api


# class ProjectTask(models.Model):
#     _inherit = "project.task"

#     message_filter = fields.Selection(
#         [
#             ("all", "Tất cả"),
#             ("message", "Send Message"),
#             ("note", "Log Note"),
#             ("activity", "Activities"),
#         ],
#         string="Lọc tin nhắn",
#         default="all",
#         tracking=False,  # Ngăn việc tự động ghi log
#     )

#     filtered_message_ids = fields.Many2many(
#         "mail.message", compute="_compute_filtered_messages", store=False, readonly=True
#     )

#     @api.depends("message_filter")
#     def _compute_filtered_messages(self):
#         """🚀 Cập nhật danh sách tin nhắn hiển thị theo bộ lọc"""
#         for record in self:
#             domain = [("res_id", "=", record.id), ("model", "=", "project.task")]

#             if record.message_filter == "message":
#                 domain.append(("message_type", "=", "comment"))  # Chỉ Send Message
#             elif record.message_filter == "note":
#                 domain.append(("message_type", "=", "notification"))  # Chỉ Log Note
#             elif record.message_filter == "activity":
#                 domain.append(
#                     ("subtype_id.name", "ilike", "Activity")
#                 )  # Chỉ Activities

#             record.filtered_message_ids = self.env["mail.message"].search(domain)

#     @api.onchange("message_filter")
#     def _onchange_message_filter(self):
#         """🚀 Gọi hàm cập nhật danh sách tin nhắn khi người dùng chọn bộ lọc"""
#         self._compute_filtered_messages()
