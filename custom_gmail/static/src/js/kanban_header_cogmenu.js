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

    dateDeadlineSort() {
        const allGroups = this.group.model.root.groups;

        for (const group of allGroups) {
            const records = group.list?.records || [];

            console.log(`📦 Group "${group.displayName}" có ${records.length} record(s):`);

            records.sort((a, b) => {
                const dateA = this._getDeadlineDate(a);
                const dateB = this._getDeadlineDate(b);
                return dateB - dateA;
            });

            // Optional: log 1 sample record
            if (records.length) {
                console.log("🔍 Sample record after sort:", records[0]);
            }
        }

        console.log("✅ Đã sort tất cả group theo date_deadline (hoặc remaining_days nếu thiếu)");
    },

    _getDeadlineDate(record) {
        const dateDeadline = record.data?.date_deadline;
        if (dateDeadline) {
            return new Date(dateDeadline);
        }

        const remainingStr = record.data?.remaining_days;
        const timeStr = remainingStr?.split("→")[1]?.trim();
        if (timeStr) {
            return new Date(this._parseDateString(timeStr));
        }

        return new Date(0); // fallback nếu không có gì
    },

    _parseDateString(dateStr) {
        const [time, date] = dateStr.split(" ");
        if (!time || !date) return "1970-01-01T00:00:00";

        const [day, month, year] = date.split("/");
        return `${year}-${month}-${day}T${this._convertTo24H(time)}`;
    },

    _convertTo24H(timeStr) {
        const match = timeStr.match(/(\d{1,2}):(\d{2})(AM|PM)/i);
        if (!match) return "00:00:00";
        let [_, h, m, meridiem] = match;
        h = parseInt(h);
        if (meridiem.toUpperCase() === "PM" && h < 12) h += 12;
        if (meridiem.toUpperCase() === "AM" && h === 12) h = 0;
        return `${String(h).padStart(2, "0")}:${m}:00`;
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

// 👇 Thêm vào menu sort
registry.category("kanban_header_config_items").add(
    "start_date_sort",
    {
        label: "Sort by Deadline Task",
        method: "dateDeadlineSort",
        isVisible: ({ permissions, props }) =>
            permissions.canEditAutomations && props.list.model.config.resModel === "project.task",
        class: "o_column_test",
    },
    { sequence: 60 }
);
