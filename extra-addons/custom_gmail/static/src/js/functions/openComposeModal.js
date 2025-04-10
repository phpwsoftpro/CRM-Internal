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

    // 👉 Lưu thread_id và message_id để gửi đúng reply
    this.state.composeData = {
        thread_id: msg.thread_id || null,
        parent_message_id: msg.message_id || null,
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

    setTimeout(() => {
        this.editorInstance = this.initCKEditor();

        let subject = msg.subject;
        if (mode === "reply") {
            subject = `${msg.subject}`;
        } else if (mode === "forward") {
            subject = `${msg.subject}`;
        }

        // let body = "";
        // let quote = "";

        // if (mode === "reply" || mode === "replyAll") {
        //     quote = `
        //         <div class="reply-quote" style="margin-top:20px; padding-top:10px; border-top:1px solid #ccc;">
        //             <p style="color:gray;">On ${msg.date_received}, "${msg.sender}" wrote:</p>
        //             <blockquote style="margin:0; padding-left:10px; border-left:2px solid #ccc;">
        //                 ${msg.body.replace(/\n/g, "<br>")}
        //             </blockquote>
        //         </div>
        //     `;
        // } else if (mode === "forward") {
        //     quote = `
        //         <br><br>---------- Forwarded message ---------<br>
        //         From: ${msg.sender} &lt;${msg.email}&gt;<br>
        //         Date: ${msg.date_received}<br>
        //         Subject: ${msg.subject}<br><br>
        //         ${msg.body.replace(/\n/g, "<br>")}
        //     `;
        // }

        // ✅ Set only empty body + quote. Khi gửi sẽ bỏ quote
        fillComposeForm(msg.sender, subject, this.editorInstance);
    }, 100);
}
