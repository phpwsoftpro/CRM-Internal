/** @odoo-module **/

import { registry } from "@web/core/registry";
import { KanbanRecord } from "@web/views/kanban/kanban_record";

export class TaskKanbanRecord extends KanbanRecord {
    setup() {
        super.setup();
        if (this.el && this.props && this.props.record?.create_date?.raw_value) {
            console.log("✅ Injected date:", this.props.record?.create_date?.raw_value)
            this.el.dataset.createDate = this.props.record.create_date.raw_value;
        }
    }
}

registry.category("views").add("task_kanban_sort", {
    ...registry.category("views").get("kanban"),
    Record: TaskKanbanRecord,
});
