/** @odoo-module **/

export function fillComposeForm(sender, subject, body, editorInstance) {
    document.querySelector(".compose-input.to").value = sender;
    document.querySelector(".compose-input.subject").value = subject;

    if (editorInstance && typeof editorInstance.setData === "function") {
        editorInstance.setData(body);
    } else {
        const textarea = document.querySelector("#compose_body");
        if (textarea) {
            textarea.innerHTML = body; 
        }
    }
}

