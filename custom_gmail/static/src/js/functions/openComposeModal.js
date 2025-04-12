/** @odoo-module **/
import { fillComposeForm } from "./fillComposeForm";
export function openComposeModal(mode, msg = null) {
    if (!msg) return;

    if (this.state.showComposeModal) {
        this.state.showComposeModal = false;
        setTimeout(() => {
            openComposeModalInternal.call(this, mode, msg);
        }, 50);
    } else {
        openComposeModalInternal.call(this, mode, msg);
    }
}

async function openComposeModalInternal(mode, msg) {
    this.state.composeMode = mode;
    this.state.showComposeModal = true;

    this.state.composeData = {
        thread_id: msg.thread_id || null,
        message_id: msg.message_id || null,
        original_sender: msg.sender || "",
    };

    const modalTitle = document.querySelector(".compose-modal-header h3");
    if (modalTitle) {
        switch (mode) {
            case "reply": modalTitle.textContent = "Reply"; break;
            case "replyAll": modalTitle.textContent = "Reply All"; break;
            case "forward": modalTitle.textContent = "Forward"; break;
            default: modalTitle.textContent = "New Message";
        }
    }

    setTimeout(async () => {
        this.editorInstance = await this.initCKEditor();

        let subject = msg.subject;
        if (mode === "reply") {
            subject = `${msg.subject}`;
        } else if (mode === "forward") {
            subject = `${msg.subject}`;
        }
        fillComposeForm(msg.sender, subject, this.editorInstance, mode);
    }, 100);
}
