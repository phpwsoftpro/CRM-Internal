/** @odoo-module **/

let previousUrl = window.location.href;

function hasUrlChanged() {
    const currentUrl = window.location.href;
    if (currentUrl !== previousUrl) {
        previousUrl = currentUrl;
        return true;
    }
    return false;
}

function updateButtons() {
    const topbar = document.querySelector(".o-mail-Chatter-topbar");
    const sendBtn = document.querySelector(".o-mail-Chatter-sendMessage");
    const noteBtn = document.querySelector(".o-mail-Chatter-logNote");

    if (topbar && sendBtn && noteBtn) {
        // Đổi chỗ 2 nút
        if (noteBtn.nextElementSibling !== sendBtn) {
            topbar.insertBefore(noteBtn, sendBtn);
        }

        // Đổi style
        sendBtn.classList.remove("btn-primary");
        sendBtn.classList.add("btn-secondary");

        noteBtn.classList.remove("btn-secondary");
        noteBtn.classList.add("btn-primary");
        
        if (noteBtn.textContent.trim() === "Log note") {
            noteBtn.textContent = "Comment";
        }
        return true;
    }

    return false;
}

function waitAndApplyChanges() {
    const observer = new MutationObserver(() => {
        if (updateButtons()) {
            observer.disconnect();
        }
    });

    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
}

document.addEventListener("DOMContentLoaded", () => {
    waitAndApplyChanges();  // Apply lần đầu khi trang load

    // Theo dõi URL thay đổi (chuyển task, mở form mới, v.v.)
    setInterval(() => {
        if (hasUrlChanged()) {
            waitAndApplyChanges();
        }
    }, 1000); // Kiểm tra mỗi 1s
});
