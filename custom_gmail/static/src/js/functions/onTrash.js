/** @odoo-module **/
import { rpc } from "@web/core/network/rpc";

export function onTrash(msg) {
    // Gọi backend để đánh dấu is_trashed = true
    const accountId = this.state.activeTabId;  // gmail.account.id của tab hiện tại
    if (!accountId) {
      return console.log("Chưa chọn Gmail account!");
    }
    console.log(accountId)
    rpc('/gmail/trash', {
      message_id: msg.id,
      account_id: msg.account_id,
    })
      .then(() => {
        // Cập nhật state và re-render
        msg.is_trashed = true;
        const acc = this.state.accounts.find(a => a.id === this.state.activeTabId);
        if (!acc) return;
        this.loadMessages(acc.email);
      })
      .catch(err => console.error("Move to Trash failed:", err));
}
