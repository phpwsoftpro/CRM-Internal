/** @odoo-module **/

import { KanbanRenderer } from "@web/views/kanban/kanban_renderer";

export class CustomKanbanRenderer extends KanbanRenderer {
    setup() {
        super.setup();
        setTimeout(() => this._addSortButtons(), 0);
    }

    _addSortButtons() {
        this.el.querySelectorAll(".o_kanban_group").forEach(group => {
            const header = group.querySelector(".o_kanban_group_header_title");
            if (!header || header.querySelector(".sort-control")) return;

            const btn = document.createElement("span");
            btn.className = "sort-control";
            btn.innerText = "⇅";
            btn.style.cursor = "pointer";
            btn.style.marginLeft = "6px";

            btn.onclick = () => this._sortGroup(group);
            header.appendChild(btn);
        });
    }

    _sortGroup(groupEl) {
        const records = Array.from(groupEl.querySelectorAll(".o_kanban_record"));
        const ascending = groupEl.dataset.sortOrder !== "asc";

        const sorted = records.sort((a, b) => {
            const dateA = parseInt(a.dataset.createDate || 0);
            const dateB = parseInt(b.dataset.createDate || 0);
            return ascending ? dateA - dateB : dateB - dateA;
        });

        const container = groupEl.querySelector(".o_kanban_records");
        sorted.forEach(el => container.appendChild(el));
        groupEl.dataset.sortOrder = ascending ? "asc" : "desc";
    }
}
