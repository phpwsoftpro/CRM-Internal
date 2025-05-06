/** @odoo-module **/
import { rpc } from "@web/core/network/rpc";

export function onTrashSelected() {
    // 1. Lấy danh sách các msg được tick
    const msgs = this.state.pagination.messages.filter(m => m.selected);
    if (!msgs.length) { return; }

    // 2. Chọn endpoint tuỳ folder
    const isTrashView = this.state.activeFolder === 'TRASH';
    const route       = isTrashView ? '/gmail/delete' : '/gmail/trash';

    // 3. Gọi API tương ứng
    Promise.all(msgs.map(m =>
        rpc(route, { message_id: m.id,
          account_id: m.account_id 
        })
          .then(() => {
            if (isTrashView) {
              // Remove khỏi state khi đã xóa hẳn
              this.state.pagination.messages =
                this.state.pagination.messages.filter(x => x.id !== m.id);
            } else {
              // đánh dấu trashed và reload nếu cần
              m.is_trashed = true;
            }
          })
    ))
    .then(() => {
        // Nếu không ở Trash, reload folder để ẩn các trashed mới
        const acc = this.state.accounts.find(a => a.id === this.state.activeTabId);
        if (!acc) return;
        this.loadMessages(acc.email);
    })
    .catch(err => console.error('Delete action failed', err));
}
