/** @odoo-module **/

import { KanbanColumn } from "@web/views/kanban/kanban_column";

const CustomTaskKanbanColumn = {
    ...KanbanColumn,
    async setup() {
        await this._super(...arguments);
        this.sortOrder = null;
    },
    onSortChange(order) {
        this.sortOrder = order;
        this.env.config.context.kanban_sort_order = order;

        // Force reload current column with updated context
        this.model.root.load();
    },
};

export const registerTaskKanbanSort = () => {
    owl.Component.extend(CustomTaskKanbanColumn);
};
