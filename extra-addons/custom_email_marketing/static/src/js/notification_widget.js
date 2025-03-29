/** @odoo-module **/

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
    bell.style.cssText = `
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
            display: ${notifications.length > 0 ? 'block' : 'none'};
        "></span>
    `;

    bell.addEventListener("click", () => toggleNotificationPopup());
    switchButtons.parentNode.insertBefore(bell, switchButtons);
}

function createNotificationHTML({ title, stage, user, deadline }) {
    return `
        <div style="
            background-color: #f4f5f7;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            padding: 10px;
            margin-bottom: 10px;
            max-width: 350px;
            font-family: 'Segoe UI', sans-serif;
        ">
            <div style="background-color: #dfe1e6; border-radius: 10px 10px 0 0; padding: 10px;">
                <div style="font-weight: bold; font-size: 15px; color: #172b4d;">${title}</div>
                <div style="font-size: 13px; color: #5e6c84; margin-top: 5px;">
                    🕒 Deadline: ${deadline || 'No deadline'}
                </div>
            </div>
            <div style="padding: 8px 10px; background: #bfbfbf; color: white; font-weight: bold;">
                DEVELOPMENT TEAM: ${stage}
            </div>
            <div style="padding: 10px; background: white; display: flex; align-items: center; border-radius: 0 0 10px 10px;">
                <img src="#" 
                     style="width: 32px; height: 32px; border-radius: 50%; margin-right: 10px;">
                <div>
                    <strong style="color: #172b4d;"></strong><br/>
                    <span style="color: #5e6c84; font-size: 13px;">Moved to list ${stage}</span>
                </div>
            </div>
        </div>
    `;
}

function toggleNotificationPopup() {
    let popup = document.getElementById("notify_popup");
    if (popup) {
        popup.remove();
        return;
    }

    popup = document.createElement("div");
    popup.id = "notify_popup";
    popup.style.cssText = `
        position: absolute;
        top: 45px;
        right: 20px;
        background: white;
        border: 1px solid #ccc;
        border-radius: 8px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.2);
        z-index: 9999;
        min-width: 250px;
        max-width: 350px;
        padding: 10px;
    `;

    if (notifications.length === 0) {
        popup.innerHTML = "<p style='margin:0; color:#666;'>✅ No new notifications.</p>";
    } else {
        popup.innerHTML = notifications.map(n => createNotificationHTML(n)).join("");
    }

    document.body.appendChild(popup);

    setTimeout(() => {
        const handler = (e) => {
            const bell = document.getElementById("notify_bell");
            const popup = document.getElementById("notify_popup");
            if (popup && !popup.contains(e.target) && !bell.contains(e.target)) {
                popup.remove();
                notifications = [];
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
    const seen = new Set();  // theo dõi task+stage đã thông báo

    kanbanGroups.forEach(group => {
        const observer = new MutationObserver((mutations) => {
            for (const mutation of mutations) {
                mutation.addedNodes.forEach(node => {
                    if (node.classList && node.classList.contains("o_kanban_record")) {
                        const taskTitle = node.querySelector(".o_kanban_record_title")?.innerText || "Task";
                        const stageName = group.querySelector(".o_kanban_header")?.innerText.trim() || "Unknown";
                        const taskKey = taskTitle + "::" + stageName;

                        if (seen.has(taskKey)) return;
                        seen.add(taskKey);

                        const deadline = node.querySelector(".oe_kanban_date")?.innerText || "N/A";
                        const userName = document.querySelector(".oe_topbar_name")?.innerText || "User";
                        const uid = odoo?.session_info?.uid || 0;
                        const user = {
                            name: userName,
                            avatar: `/web/image/res.users/${uid}/image_128`
                        };

                        const data = { title: taskTitle, stage: stageName, deadline, user };

                        if (!notifications.find(n => n.title === taskTitle && n.stage === stageName)) {
                            notifications.push(data);
                            saveNotifications();

                            const dot = document.getElementById("notify_dot");
                            if (dot) dot.style.display = "block";

                            console.log("📌 New notification added:", data);
                        }
                    }
                });
            }
        });

        observer.observe(group, { childList: true, subtree: false });
    });
}

function initializeNotifications() {
    const dot = document.getElementById("notify_dot");
    if (notifications.length > 0 && dot) {
        dot.style.display = "block";
    }
}

window.addEventListener("load", () => {
    const mainObserver = new MutationObserver(() => {
        const controlPanel = document.querySelector(".o_control_panel");
        if (controlPanel && !document.getElementById("notify_bell")) {
            injectNotificationBell();
            initializeNotifications();
        }

        const kanbanReady = document.querySelector(".o_kanban_group");
        if (kanbanReady && !kanbanReady.dataset.notifyObserved) {
            observeKanbanMoves();
            kanbanReady.dataset.notifyObserved = "true";
        }
    });

    mainObserver.observe(document.body, { childList: true, subtree: true });
});

export default {};
