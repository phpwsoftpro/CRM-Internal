/* @odoo-module */

import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { patch } from "@web/core/utils/patch";
import { KanbanHeader } from "@web/views/kanban/kanban_header";

patch(KanbanHeader.prototype, {
    setup() {
        super.setup();
        window.KanbanHeader = this;
    },

    sortByStartDateNow() {
        const allGroups = this.group.model.root.groups;

        for (const group of allGroups) {
            const records = group.list?.records || [];

            records.sort((a, b) => {
                const dA = a.data.start_date_now ? new Date(a.data.start_date_now) : new Date(0);
                const dB = b.data.start_date_now ? new Date(b.data.start_date_now) : new Date(0);
                return dB - dA; // mới nhất đến cũ nhất
            });

            group.list.model.notify(); // cập nhật lại giao diện
            console.log(`✅ Đã sort group "${group.displayName}" theo start_date_now`);
        }
    },

    get permissions() {
        const permissions = super.permissions;
        Object.defineProperty(permissions, "canEditAutomations", {
            get: () => true,
            configurable: true,
        });
        return permissions;
    },
});

// 👇 Đăng ký nút sort vào menu Kanban header
registry.category("kanban_header_config_items").add(
    "start_date_now_sort",
    {
        label: "Sort by Start Date",
        method: "sortByStartDateNow",
        isVisible: ({ permissions, props }) =>
            permissions.canEditAutomations &&
            props.list.model.config.resModel === "project.task",
        class: "o_column_sort_by_start_date_now",
    },
    { sequence: 61 }
);
