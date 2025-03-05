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
    await this.loadCKEditor();
    setTimeout(() => {
        if (window.ClassicEditor) {
            ClassicEditor.create(document.querySelector("#compose_body"))
                .then(editor => {
                    this.editorInstance = editor;
                })
                .catch(error => {
                    console.error("Error loading CKEditor:", error);
                });
        }
    }, 1000);
}