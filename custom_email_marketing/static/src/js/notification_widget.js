/** @odoo-module **/

let notifications = [];

function injectNotificationBell() {
    if (document.getElementById("notify_bell")) return;

    const switchButtons = document.querySelector(".o_cp_switch_buttons");

    if (!switchButtons) return;

    const bell = document.createElement("div");
    bell.id = "notify_bell";
    bell.style = `
        display: inline-block;
        position: relative;
        cursor: pointer;
        margin-right: 8px;
        padding: 6px;
    `;
    bell.innerHTML = `
        <i class="fa fa-bell" style="font-size: 18px; color: #555;"></i>
        <span id="notify_dot" style="
            position: absolute;
            top: 2px;
            right: 2px;
            background: red;
            border-radius: 50%;
            width: 8px;
            height: 8px;
            display: none;"></span>
    `;

    bell.addEventListener("click", () => toggleNotificationPopup());
    switchButtons.parentNode.insertBefore(bell, switchButtons);
    console.log("✅ Notification bell injected");
}

function toggleNotificationPopup() {
    let popup = document.getElementById("notify_popup");
    if (popup) {
        popup.remove();
        return;
    }

    popup = document.createElement("div");
    popup.id = "notify_popup";
    popup.style = `
        position: absolute;
        top: 45px;
        right: 20px;
        background: white;
        border: 1px solid #ccc;
        border-radius: 8px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.2);
        z-index: 9999;
        min-width: 250px;
        max-width: 300px;
        padding: 10px;
    `;

    if (notifications.length === 0) {
        popup.innerHTML = "<p style='margin:0; color:#666;'>✅ No new notifications.</p>";
    } else {
        popup.innerHTML = `
            <strong>🔔 Notifications:</strong>
            <ul style="padding-left: 20px;">
                ${notifications.map(n => `<li>${n}</li>`).join("")}
            </ul>
        `;
    }

    document.body.appendChild(popup);   

    setTimeout(() => {
        const handler = (e) => {
            const bell = document.getElementById("notify_bell");
            const popup = document.getElementById("notify_popup");
            if (popup && !popup.contains(e.target) && !bell.contains(e.target)) {
                popup.remove();
                document.removeEventListener("click", handler);
            }
        };
        document.addEventListener("click", handler);
    }, 100);

    notifications = [];
    const dot = document.getElementById("notify_dot");
    if (dot) dot.style.display = "none";
}

window.addEventListener("load", () => {
    const observer = new MutationObserver(() => {
        const controlPanel = document.querySelector(".o_control_panel");
        if (controlPanel && !document.getElementById("notify_bell")) {
            injectNotificationBell();
        }
    });

    // ✅ Gọi observe sau khi DOM đã sẵn sàng
    observer.observe(document.body, { childList: true, subtree: true });
});

export default {};  // Quan trọng để không bị lỗi module
