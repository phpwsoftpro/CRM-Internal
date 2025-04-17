/** @odoo-module **/

import { KanbanRecord } from "@web/views/kanban/kanban_record";

export class CustomKanbanRecord extends KanbanRecord {
    setup() {
        super.setup();
        const createDate = this.props.record.data.create_date;
        if (createDate) {
            this.el.dataset.createDate = new Date(createDate).getTime();
        }
    }
}