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

function activateCommentTab() {
    const noteBtn = document.querySelector(".o-mail-Chatter-logNote");
    const composer = document.querySelector(".o-mail-Composer");
    if (noteBtn && (!composer || composer.classList.contains("d-none"))) {
        noteBtn.click();
    }
}

function updateChatterButtons() {
    const topbar = document.querySelector(".o-mail-Chatter-topbar");
    const sendBtn = document.querySelector(".o-mail-Chatter-sendMessage");
    const noteBtn = document.querySelector(".o-mail-Chatter-logNote");

    if (topbar && sendBtn && noteBtn) {
        // Hoán đổi vị trí
        if (noteBtn.nextElementSibling !== sendBtn) {
            topbar.insertBefore(noteBtn, sendBtn);
        }

        // Đổi màu
        sendBtn.classList.remove("btn-primary");
        sendBtn.classList.add("btn-secondary");

        noteBtn.classList.remove("btn-secondary");
        noteBtn.classList.add("btn-primary");

        // Đổi text
        if (noteBtn.textContent.trim() === "Log note") {
            noteBtn.textContent = "Comment";
        }
        if (sendBtn.textContent.trim() === "Send message") {
            sendBtn.textContent = "Send Email";
        }

        activateCommentTab();  // tự mở tab Comment
        return true;
    }
    return false;
}

function observeChatter() {
    const target = document.body;
    const observer = new MutationObserver(() => {
        setTimeout(() => {
            updateChatterButtons();
        }, 200);
    });

    observer.observe(target, {
        childList: true,
        subtree: true,
    });
}

function observeComposerVisibility() {
    const chatter = document.querySelector(".o-mail-Chatter");
    if (!chatter) return;

    const observer = new MutationObserver(() => {
        const composer = document.querySelector(".o-mail-Composer");
        if (composer && composer.classList.contains("d-none")) {
            activateCommentTab();  // tự mở lại khi vừa gửi
        }
    });

    observer.observe(chatter, {
        childList: true,
        subtree: true,
        attributes: true,
        attributeFilter: ["class"],
    });
}

document.addEventListener("DOMContentLoaded", () => {
    observeChatter();

    // Khi đổi URL (form mới, task khác...)
    setInterval(() => {
        if (hasUrlChanged()) {
            observeChatter();
            setTimeout(updateChatterButtons, 1000);
            setTimeout(observeComposerVisibility, 1500);
        }
    }, 1000);

    // Fallback
    setTimeout(() => {
        updateChatterButtons();
        observeComposerVisibility();
    }, 2000);
});
