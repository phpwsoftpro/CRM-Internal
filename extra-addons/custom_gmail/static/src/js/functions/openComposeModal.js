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

    // Use a single timeout for initializing editor
    setTimeout(() => {
        // Check if editor already exists and destroy it
        if (this.editorInstance) {
            this.editorInstance.destroy();
            this.editorInstance = null;
        }
        
        // Initialize editor and store the instance
        this.editorInstance = this.initCKEditor();
        
        // Fill the form after editor is ready
        const editorContent = {
            "reply": {
                subject: msg.subject.startsWith("Re:") ? msg.subject : `Re: ${msg.subject}`,
                to: msg.email,
                body: `<br><br>On ${msg.date_received}, ${msg.email_sender} <${msg.email}> wrote:<br><blockquote>${msg.gmail_body.replace(/\n/g, '<br>')}</blockquote>`
            },
            "replyAll": {
                subject: msg.subject.startsWith("Re:") ? msg.subject : `Re: ${msg.subject}`,
                to: msg.email,
                body: `<br><br>On ${msg.date_received}, ${msg.email_sender} <${msg.email}> wrote:<br><blockquote>${msg.gmail_body.replace(/\n/g, '<br>')}</blockquote>`
            },
            "forward": {
                subject: msg.subject.startsWith("Fwd:") ? msg.subject : `Fwd: ${msg.subject}`,
                to: "",
                body: `<br><br>---------- Forwarded message ---------<br>From: ${msg.email_sender} <${msg.email}><br>Date: ${msg.date_received}<br>Subject: ${msg.subject}<br><br>${msg.gmail_body.replace(/\n/g, '<br>')}`
            },
            "new": {
                subject: "",
                to: "",
                body: ""
            }
        };
        
        const contentType = mode in editorContent ? mode : "new";
        fillComposeForm(
            editorContent[contentType].to,
            editorContent[contentType].subject,
            editorContent[contentType].body,
            this.editorInstance
        );
    }, 100);
}