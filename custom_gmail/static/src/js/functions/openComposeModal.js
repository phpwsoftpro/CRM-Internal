/** @odoo-module **/
import { fillComposeForm } from "./fillComposeForm";
export function openComposeModal(mode, msg = null) {
    if (!msg) return;

    // Check if compose modal is already open, if so, close it first
    if (this.state.showComposeModal) {
        // Destroy existing editor instance if it exists
        if (this.editorInstance) {
            this.editorInstance.destroy();
            this.editorInstance = null;
        }
        // Reset state briefly to ensure clean initialization
        this.state.showComposeModal = false;
        // Small delay to ensure DOM updates
        setTimeout(() => {
            openComposeModalInternal.call(this, mode, msg);
        }, 50);
    } else {
        openComposeModalInternal.call(this, mode, msg);
    }
}

function openComposeModalInternal(mode, msg) {
    this.state.composeMode = mode;
    this.state.showComposeModal = true;

    const modalTitle = document.querySelector(".compose-modal-header h3");
    if (modalTitle) {
        switch (mode) {
            case "reply": modalTitle.textContent = "Reply"; break;
            case "replyAll": modalTitle.textContent = "Reply All"; break;
            case "forward": modalTitle.textContent = "Forward"; break;
            default: modalTitle.textContent = "New Message";
        }
    }

    // Khởi tạo nội dung email dựa trên mode (reply, forward, new)
    setTimeout(() => {
        if (this.editorInstance) {
            this.editorInstance.destroy();
            this.editorInstance = null;
        }

        this.editorInstance = this.initCKEditor();

        let subject = msg.subject;
        if (mode === "reply" && !msg.subject.startsWith("Re:")) {
            subject = `Re: ${msg.subject}`;
        } else if (mode === "forward" && !msg.subject.startsWith("Fwd:")) {
            subject = `Fwd: ${msg.subject}`;
        }

        let body = "";
        if (mode === "reply" || mode === "replyAll") {
            body = `
                <br><br>On ${msg.date_received}, ${msg.email_sender} <${msg.email}> wrote:<br>
                <blockquote>${msg.gmail_body.replace(/\n/g, "<br>")}</blockquote>
            `;
        } else if (mode === "forward") {
            body = `
                <br><br>---------- Forwarded message ---------<br>
                From: ${msg.email_sender} <${msg.email}><br>
                Date: ${msg.date_received}<br>
                Subject: ${msg.subject}<br><br>
                ${msg.gmail_body.replace(/\n/g, "<br>")}
            `;
        }

        // Gọi hàm điền nội dung email vào compose modal
        fillComposeForm(msg.email, subject, body, this.editorInstance);
    }, 100);
}

export function getThreadMessageById(state, messageId, threadId) {
    if (state.threads && state.threads[threadId]) {
        return state.threads[threadId].find(msg => msg.id === messageId) || null;
    }
    return null;
}