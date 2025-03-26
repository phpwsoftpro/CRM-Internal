/** @odoo-module **/

export function loadCKEditor() {
    return new Promise((resolve, reject) => {
        if (!document.getElementById("ckeditor_script")) {
            let script = document.createElement("script");
            script.id = "ckeditor_script";
            script.src = "https://cdn.ckeditor.com/ckeditor5/39.0.0/classic/ckeditor.js";
            script.onload = () => {
                console.log("CKEditor Loaded!");
                resolve();
            };
            script.onerror = () => {
                reject(new Error("Failed to load CKEditor"));
            };
            document.head.appendChild(script);
        } else if (window.ClassicEditor) {
            // CKEditor đã tải rồi
            resolve();
        } else {
            // Nếu script đang được tải, chờ nó hoàn tất
            const existingScript = document.getElementById("ckeditor_script");
            existingScript.onload = () => {
                resolve();
            };
            existingScript.onerror = () => {
                reject(new Error("Failed to load CKEditor"));
            };
        }
    });
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
