/** @odoo-module **/

export function fillComposeForm(to, subject, body, editorInstance) {
    const toField = document.querySelector(".compose-input[name='to']");
    const subjectField = document.querySelector(".compose-input[name='subject']");

    if (toField) toField.value = to;
    if (subjectField) subjectField.value = subject;
    
    if (editorInstance) {
        editorInstance.setData(body);
    } else if (document.querySelector("#compose_body")) {
        document.querySelector("#compose_body").value = body;
    }
}