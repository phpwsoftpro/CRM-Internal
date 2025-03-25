/** @odoo-module **/

let notifications = window.notifications || [];

function observeKanbanTaskMove() {
    const observer = new MutationObserver((mutationsList) => {
        for (const mutation of mutationsList) {
            if (mutation.type === "childList") {
                mutation.addedNodes.forEach((node) => {
                    if (node.classList && node.classList.contains("oe_kanban_global_click")) {
                        // Khi task được thêm vào cột mới
                        const dot = document.getElementById("notify_dot");
                        if (dot) dot.style.display = "block";
                        notifications.push("📝 A task was moved to another column.");
                        console.log("✅ Task moved!");
                    }
                });
            }
        }
    });

    const columns = document.querySelectorAll(".o_kanban_group");
    columns.forEach((col) => {
        observer.observe(col, { childList: true });
    });
    console.log("👀 Kanban task move observer attached.");
}

document.addEventListener("DOMContentLoaded", () => {
    const pageObserver = new MutationObserver(() => {
        if (document.querySelector(".o_kanban_view")) {
            observeKanbanTaskMove();
        }
    });
    pageObserver.observe(document.body, { childList: true, subtree: true });
});
