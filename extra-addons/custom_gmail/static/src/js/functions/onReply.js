export function onReply(ev, selectedMessage) {
    ev.stopPropagation();

    const message = selectedMessage.thread_id ? selectedMessage : "";
    this.openComposeModal("reply", {
        ...message,
        thread_id: message.thread_id, 
        message_id: message.message_id,
    });
}
