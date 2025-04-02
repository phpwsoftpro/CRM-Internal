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

    setTimeout(() => {

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
                <br><br>On ${msg.date_received}, ${msg.sender} wrote:<br>
                <blockquote>${msg.body.replace(/\n/g, "<br>")}</blockquote>
            `;
        } else if (mode === "forward") {
            body = `
                <br><br>---------- Forwarded message ---------<br>
                From: ${msg.sender} <${msg.email}><br>
                Date: ${msg.date_received}<br>
                Subject: ${msg.subject}<br><br>
                ${msg.body.replace(/\n/g, "<br>")}
            `;
        }

        fillComposeForm(msg.sender, subject, body, this.editorInstance);
    }, 100);
}