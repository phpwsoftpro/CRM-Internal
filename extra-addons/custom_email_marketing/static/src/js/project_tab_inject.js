/** @odoo-module **/

(function () {
    const STORAGE_KEY = 'project_read_notifications';

    function formatLocalDate(utcDateStr) {
        const date = new Date(utcDateStr);
        return date.toLocaleString();
    }

    function getReadIds() {
        try {
            return JSON.parse(localStorage.getItem(STORAGE_KEY)) || [];
        } catch {
            return [];
        }
    }

    function markAsRead(id) {
        const readIds = getReadIds();
        if (!readIds.includes(id)) {
            readIds.push(id);
            localStorage.setItem(STORAGE_KEY, JSON.stringify(readIds));
        }
    }

    function countUnread(notifications) {
        const readIds = getReadIds();
        return notifications.filter(msg => !readIds.includes(msg.id)).length;
    }

    function updateBadge(unreadCount) {
        const badge = document.querySelector('.o-project-tab-badge');
        if (badge) {
            badge.textContent = unreadCount;
            badge.classList.toggle('d-none', unreadCount === 0);
        }
    }

    async function loadProjectNotifications(contentEl) {
        contentEl.innerHTML = "";
        try {
            const response = await fetch("/project/notifications", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({}),
            });

            const data = await response.json();
            const notifications = data.result?.result || [];

            const projectNotifications = notifications.filter(notification => {
                const subject = typeof notification.subject === 'string' ? notification.subject : '';
                const body = typeof notification.body === 'string' ? notification.body : '';
            
                return (
                    subject.includes('moved') ||
                    subject.includes('created') ||
                    body.includes('@') ||
                    (!subject && body)
                );
            });

            
            

            updateBadge(countUnread(projectNotifications));

            for (const msg of projectNotifications) {
                let taskName = `Task #${msg.res_id}`;
                try {
                    const taskResp = await fetch("/web/dataset/call_kw/project.task/read", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({
                            jsonrpc: "2.0",
                            method: "call",
                            params: {
                                model: "project.task",
                                method: "read",
                                args: [[msg.res_id], ["name"]],
                                kwargs: {},
                            },
                        }),
                    });
                    const taskData = await taskResp.json();
                    if (taskData.result?.[0]) taskName = taskData.result[0].name;
                } catch (err) {
                    console.warn("Không lấy được tên task:", err);
                }

                const link = document.createElement("a");
                link.href = `/web#id=${msg.res_id}&model=project.task&view_type=form`;
                // link.target = "_blank"; // ❌ XÓA DÒNG NÀY
                link.className = "list-group-item text-reset text-decoration-none d-block";
                link.dataset.notificationId = msg.id;


                const readIds = getReadIds();
                if (!readIds.includes(msg.id)) {
                    link.classList.add("fw-bold");
                }

                let icon = '';
                    const subject = typeof msg.subject === 'string' ? msg.subject : '';
                    const body = typeof msg.body === 'string' ? msg.body : '';

                    if (subject.includes("moved")) {
                        icon = '<i class="icon fa fa-arrow-right text-primary me-2"></i>';
                    } else if (body.includes("@") || !subject) {
                        icon = '<i class="icon fa fa-comment text-success me-2"></i>';
                    }


                link.innerHTML = `
                    <div class="d-flex align-items-center mb-1">${icon}<div><strong>${taskName}</strong></div></div>
                    <div class="body mb-1">${msg.body || 'No body content'}</div>
                    <div><small>${formatLocalDate(msg.date)} - ${msg.author}</small></div>
                `;

                link.addEventListener("click", () => {
                    markAsRead(msg.id);
                    link.classList.remove("fw-bold");
                    updateBadge(countUnread(projectNotifications));
                });

                contentEl.appendChild(link);
            }

            if (projectNotifications.length === 0) {
                contentEl.innerHTML = `<div class="text-center text-muted p-3">Không có thông báo về task project.</div>`;
            }

        } catch (err) {
            console.error("Lỗi khi load project notifications:", err);
            contentEl.innerHTML = `<div class="text-center text-danger p-3">Lỗi khi tải thông báo.</div>`;
        }
    }

    function injectProjectTab() {
        const tabHeader = document.querySelector(".o-mail-MessagingMenu-header");
        const contentWrapper = document.querySelector(".o-mail-MessagingMenu-list");
    
        if (!tabHeader || !contentWrapper) return;
        if (tabHeader.querySelector('[data-project-tab="true"]')) return;
    
        const projectTab = document.createElement("button");
        projectTab.className = "o-mail-MessagingMenu-headerFilter btn btn-link px-2 py-1";
        projectTab.setAttribute("type", "button");
        projectTab.setAttribute("role", "tab");
        projectTab.setAttribute("data-project-tab", "true");
        projectTab.innerHTML = `Project <span class="badge bg-danger rounded-pill ms-1 o-project-tab-badge d-none"></span>`;
    
        const projectContent = document.createElement("div");
        projectContent.className = "o-project-MessagingMenu-list d-none";
        projectContent.style.minHeight = "300px";
        projectContent.style.overflowY = "auto";
    
        contentWrapper.parentNode.insertBefore(projectContent, contentWrapper.nextSibling);
    
        const channelsTab = Array.from(tabHeader.children).find(btn => btn.textContent.includes("Channels"));
        if (channelsTab) {
            tabHeader.insertBefore(projectTab, channelsTab.nextSibling);
        } else {
            tabHeader.appendChild(projectTab);
        }
    
        // Tab Project click
        projectTab.addEventListener("click", async () => {
            tabHeader.querySelectorAll("button").forEach(btn => btn.classList.remove("o-active"));
            projectTab.classList.add("o-active");
    
            contentWrapper.classList.add("d-none");
            projectContent.classList.remove("d-none");
    
            await loadProjectNotifications(projectContent);
        });
    
        // Các tab khác
        tabHeader.querySelectorAll("button.o-mail-MessagingMenu-headerFilter:not([data-project-tab='true'])")
            .forEach((btn) => {
                btn.addEventListener("click", () => {
                    // Remove active from project tab nếu đang được bật
                    projectTab.classList.remove("o-active");
    
                    // Show lại content chính
                    contentWrapper.classList.remove("d-none");
                    projectContent.classList.add("d-none");
                });
            });
    
        // Mặc định mở tab Project
        projectTab.click();
    }
    
    

    function setupObserver() {
        const target = document.body;
        const observer = new MutationObserver(() => {
            const menu = document.querySelector(".o-mail-MessagingMenu");
            if (menu) {
                injectProjectTab();
            }
        });
        observer.observe(target, { childList: true, subtree: true });
    }

    document.addEventListener("DOMContentLoaded", () => {
        setupObserver();
    });
})();
