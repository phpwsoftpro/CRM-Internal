/** @odoo-module **/
import { getThreadMessageById } from "./openComposeModal";
export function onReply(ev, selectedMessage) {
    ev.stopPropagation();
    
    // Nếu có thread_id, lấy đúng email đang được reply
    let actualMessage = selectedMessage;
    if (selectedMessage.thread_id) {
        actualMessage = getThreadMessageById(this.state, selectedMessage.id, selectedMessage.thread_id);
    }

    this.openComposeModal("reply", actualMessage);
}