/** @odoo-module **/

document.addEventListener("DOMContentLoaded", () => {
    const observer = new MutationObserver(() => {
        const topbar = document.querySelector(".o-mail-Chatter-topbar");
        const sendBtn = document.querySelector(".o-mail-Chatter-sendMessage");
        const noteBtn = document.querySelector(".o-mail-Chatter-logNote");

        if (topbar && sendBtn && noteBtn) {
            // Đổi vị trí nếu cần
            if (noteBtn.nextElementSibling !== sendBtn) {
                topbar.insertBefore(noteBtn, sendBtn);
            }

            // ❌ Xóa active ở Send Message
            sendBtn.classList.remove("active");

            // ✅ Thêm active cho Log Note
            noteBtn.classList.add("active");

            sendBtn.classList.remove("btn-primary");
            sendBtn.classList.add("btn-secondary");

            noteBtn.classList.remove("btn-secondary");
            noteBtn.classList.add("btn-primary");
            // 📌 Click để load nội dung Log Note
            noteBtn.click();

            // Ngắt observer sau khi hoàn tất
            observer.disconnect();
        }
    });

    observer.observe(document.body, {
        childList: true,
        subtree: true,
    });
});
