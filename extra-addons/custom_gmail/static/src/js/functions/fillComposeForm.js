/** @odoo-module **/

export function fillComposeForm(to, subject, body, editorInstance) {
    document.querySelector(".compose-input.to").value = to;
    document.querySelector(".compose-input.subject").value = subject;

    // Kiểm tra nếu editorInstance hợp lệ (CKEditor)
    if (editorInstance && typeof editorInstance.setData === "function") {
        editorInstance.setData(body);
    } else {
        // Nếu CKEditor chưa khởi tạo, gán nội dung vào textarea
        const textarea = document.querySelector("#compose_body");
        if (textarea) {
            textarea.innerHTML = body; // Nếu CKEditor không hoạt động, fallback sang textarea
        }
    }
}

