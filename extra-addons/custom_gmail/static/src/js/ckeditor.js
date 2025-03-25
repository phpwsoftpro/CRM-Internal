/** @odoo-module **/

export function loadCKEditor() {
    if (!document.getElementById("ckeditor_script")) {
        let script = document.createElement("script");
        script.id = "ckeditor_script";
        script.src = "https://cdn.ckeditor.com/ckeditor5/39.0.0/classic/ckeditor.js";
        script.onload = () => {
            console.log("CKEditor Loaded!");
        };
        document.head.appendChild(script);
    }
}

export async function initCKEditor() {
    await loadCKEditor();

    setTimeout(() => {
        const el = document.querySelector("#compose_body");
        if (el && window.ClassicEditor) {
            ClassicEditor.create(el)
                .then(editor => {
                    window.editorInstance = editor; // ✅ Gán đúng
                })
                .catch(error => {
                    console.error("Error loading CKEditor:", error);
                });
        }
    }, 100);
}
