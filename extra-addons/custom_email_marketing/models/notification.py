# from odoo import models, fields
# import logging

# _logger = logging.getLogger(__name__)


# class ProjectTask(models.Model):
#     _inherit = "project.task"

#     def write(self, vals):
#         _logger.info(f"[TASK WRITE] Called with vals: {vals} for task(s): {self.ids}")
#         stage_before = {rec.id: rec.stage_id.name for rec in self}
#         result = super().write(vals)

#         for rec in self:
#             if "stage_id" in vals:
#                 old_stage = stage_before.get(rec.id)
#                 new_stage = self.env["project.task.type"].browse(vals["stage_id"]).name
#                 user = self.env.user

#                 body = (
#                     f"<b>📌 {rec.name}</b> was moved by <b>{user.name}</b><br>"
#                     f"Stage: <i>{old_stage}</i> → <i>{new_stage}</i>"
#                 )

#                 try:
#                     # Tìm hoặc tạo channel công khai 'All Users'
#                     channel = self.env["mail.channel"].search(
#                         [("name", "=", "All Users")], limit=1
#                     )
#                     if not channel:
#                         partners = (
#                             self.env["res.users"]
#                             .search([("active", "=", True)])
#                             .mapped("partner_id")
#                         )
#                         channel = self.env["mail.channel"].create(
#                             {
#                                 "name": "All Users",
#                                 "channel_type": "channel",
#                                 "public": "public",
#                                 "channel_partner_ids": [(6, 0, partners.ids)],
#                             }
#                         )
#                         _logger.info(
#                             f"[CHANNEL CREATED] 'All Users' with {len(partners)} partners"
#                         )

#                     # Gửi tin nhắn vào channel
#                     channel.message_post(
#                         body=body,
#                         author_id=user.partner_id.id,
#                         message_type="comment",
#                         subtype_xmlid="mail.mt_comment",
#                     )
#                     _logger.info(f"[DISCUSS POPUP] Message sent to channel: All Users")

#                 except Exception as e:
#                     _logger.error(f"[ERROR] Could not post to Discuss: {str(e)}")

#         return result
