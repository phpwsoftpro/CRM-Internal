/** @odoo-module **/

// Use localStorage to persist notifications between page loads
let notifications = JSON.parse(localStorage.getItem('odooNotifications') || '[]');

function saveNotifications() {
    localStorage.setItem('odooNotifications', JSON.stringify(notifications));
}

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
            display: ${notifications.length > 0 ? 'block' : 'none'};">
        </span>
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
                notifications = []; // Clear notifications when popup is closed
                saveNotifications();
                const dot = document.getElementById("notify_dot");
                if (dot) dot.style.display = "none";
                document.removeEventListener("click", handler);
            }
        };
        document.addEventListener("click", handler);
    }, 100);
}

function observeKanbanMoves() {
    const kanbanGroups = document.querySelectorAll(".o_kanban_group");
    kanbanGroups.forEach(group => {
        const observer = new MutationObserver((mutations) => {
            for (const mutation of mutations) {
                mutation.addedNodes.forEach(node => {
                    if (node.classList && node.classList.contains("o_kanban_record")) {
                        const taskTitle = node.querySelector(".o_kanban_record_title")?.innerText || "Task";
                        const stageName = group.querySelector(".o_kanban_header")?.innerText.trim();
                        const message = `📌 ${taskTitle} was moved to "${stageName}"`;
                        
                        // Only add unique notifications
                        if (!notifications.includes(message)) {
                            notifications.push(message);
                            saveNotifications();
                        }

                        const dot = document.getElementById("notify_dot");
                        if (dot) dot.style.display = "block";
                        console.log("📌 New notification added:", message);
                    }
                });
            }
        });

        observer.observe(group, { childList: true, subtree: false });
    });
}

function initializeNotifications() {
    // On page load, check if there are any stored notifications
    const dot = document.getElementById("notify_dot");
    if (notifications.length > 0 && dot) {
        dot.style.display = "block";
    }
}

window.addEventListener("load", () => {
    const mainObserver = new MutationObserver(() => {
        const controlPanel = document.querySelector(".o_control_panel");
        const kanbanReady = document.querySelector(".o_kanban_group");

        if (controlPanel && !document.getElementById("notify_bell")) {
            injectNotificationBell();
            initializeNotifications();
        }

        if (kanbanReady) {
            observeKanbanMoves();
            mainObserver.disconnect(); // Avoid attaching observer multiple times
        }
    });

    mainObserver.observe(document.body, { childList: true, subtree: true });
});

export default {};