// /** @odoo-module **/
// import { registry } from "@web/core/registry";
// import { patch } from "@web/core/utils/patch";

// patch(registry.category("views").get("mail.Chatter"), "chatter-filter", {
//     setup() {
//         this._super.apply(this, arguments);
//         this.message_filter = "all";
//     },

//     async onMessageFilterChange(ev) {
//         this.message_filter = ev.target.value;
//         await this.model.orm.call(
//             "project.task",
//             "onchange",
//             [this.model.localId],
//             { message_filter: this.message_filter }
//         );
//         this.render(); // 🚀 Cập nhật giao diện ngay sau khi lọc
//     },
// });
