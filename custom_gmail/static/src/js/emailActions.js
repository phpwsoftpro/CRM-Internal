/** @odoo-module **/

export async function loadMessages() {
    this.state.messages = [
        {
            id: 1,
            email_sender: "Tony Aasen",
            email: "tony.aasen@example.com",
            subject: "World map 🌎",
            preview: "Hi Robert, I think, but I really don't remember...",
            date_received: "4:30",
            gmail_body: `Hi again Robert,

I think, but I really don't remember if I asked you about it earlier, but we are looking for a map solution for our webpages, where we can tag/mark all KTV Working Drone partners all around the world.

Do you know about a fairly simple solution for a taggable map like this?`,
            unread: true,
            starred: false
        },
        {
            id: 2,
            email_sender: "Hoàng Đức Tài",
            email: "taivip@gmail.com",
            subject: "Hâyyyyy",
            preview: "Hi Robert, I think, but I really don't remember...",
            date_received: "4:30",
            gmail_body: `Hi again Robert,

I think, but I really don't remember if I asked you about it earlier, but we are looking for a map solution for our webpages, where we can tag/mark all KTV Working Drone partners all around the world.

Do you know about a fairly simple solution for a taggable map like this?`,
            unread: true,
            starred: false
        },
    ];
    this.loadStarredState();
}

export function toggleStar(msg) {
    msg.starred = !msg.starred;
    this.saveStarredState();
    this.render();
}

export function onReply(ev, msg) {
    ev.stopPropagation();
    this.openComposeModal("reply", msg);
}

export function onReplyAll(ev, msg) {
    ev.stopPropagation();
    this.openComposeModal("replyAll", msg);
}

export function onForward(ev, msg) {
    ev.stopPropagation();
    this.openComposeModal("forward", msg);
}

export function openComposeModal(mode, msg = null) {
    if (!msg) return;

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
        this.initCKEditor();
        setTimeout(() => {
            switch (mode) {
                case "reply":
                    const replySubject = msg.subject.startsWith("Re:") ? msg.subject : `Re: ${msg.subject}`;
                    this.fillComposeForm(msg.email, replySubject, `<br><br>On ${msg.date_received}, ${msg.email_sender} <${msg.email}> wrote:<br><blockquote>${msg.gmail_body.replace(/\n/g, '<br>')}</blockquote>`);
                    break;
                case "replyAll":
                    const replyAllSubject = msg.subject.startsWith("Re:") ? msg.subject : `Re: ${msg.subject}`;
                    this.fillComposeForm(msg.email, replyAllSubject, `<br><br>On ${msg.date_received}, ${msg.email_sender} <${msg.email}> wrote:<br><blockquote>${msg.gmail_body.replace(/\n/g, '<br>')}</blockquote>`);
                    break;
                case "forward":
                    const fwdSubject = msg.subject.startsWith("Fwd:") ? msg.subject : `Fwd: ${msg.subject}`;
                    this.fillComposeForm("", fwdSubject, `<br><br>---------- Forwarded message ---------<br>From: ${msg.email_sender} <${msg.email}><br>Date: ${msg.date_received}<br>Subject: ${msg.subject}<br><br>${msg.gmail_body.replace(/\n/g, '<br>')}`);
                    break;
                default:
                    this.fillComposeForm("", "", "");
            }
        }, 1200);
    }, 100);
}

export function fillComposeForm(to, subject, body) {
    const toField = document.querySelector(".compose-input[name='to']");
    const subjectField = document.querySelector(".compose-input[name='subject']");
    const bodyEditor = this.editorInstance;

    if (toField) toField.value = to;
    if (subjectField) subjectField.value = subject;
    if (bodyEditor) {
        bodyEditor.setData(body);
    } else if (document.querySelector("#compose_body")) {
        document.querySelector("#compose_body").value = body;
    }
}

export function onSendEmail() {
    console.log("Email Content:", this.state.emailBody);
    alert("Email Sent!");
    this.state.showComposeModal = false;
}