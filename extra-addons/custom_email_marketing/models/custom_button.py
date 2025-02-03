from odoo import models, fields, api
import xml.etree.ElementTree as ET


class MyCustomDiscuss(models.Model):
    _inherit = "mail.thread"

    def action_my_custom_button(self):
        return {
            "name": "My Custom Button",
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "my.custom.wizard",  # Thay thế bằng model wizard của bạn
            "target": "new",
        }

    def fields_view_get(
        self, view_id=None, view_type="form", toolbar=False, submenu=False
    ):
        res = super(MyCustomDiscuss, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu
        )
        if view_type == "form" and self._name == "mail.thread":
            doc = ET.fromstring(res["arch"])
            try:
                button = doc.xpath(
                    "//footer/button[contains(@name, 'action_my_custom_button')]"
                )
                if button:
                    new_button = ET.Element(
                        "button",
                        {"name": "action_my_custom_button", "string": "My Button"},
                    )
                    button.addnext(new_button)
                    res["arch"] = ET.tostring(doc)
            except Exception as e:
                print("Error adding button:", e)
        return res
