/** @odoo-module **/

(function () {
    const STORAGE_KEY = "kanban_sort_order";

    function getSortOrder() {
        try {
            return JSON.parse(localStorage.getItem(STORAGE_KEY)) || {};
        } catch {
            return {};
        }
    }

    function setSortOrder(stageId, order) {
        const data = getSortOrder();
        data[stageId] = order;
        localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
    }

    function sortTasks(column, order) {
        const container = column.querySelector(".o_kanban_records");
        if (!container) return;
        const taskEls = [...container.querySelectorAll(".o_kanban_record")];

        taskEls.sort((a, b) => {
            const aDate = new Date(a.dataset.createDate || "2000-01-01");
            const bDate = new Date(b.dataset.createDate || "2000-01-01");
            return order === "asc" ? aDate - bDate : bDate - aDate;
        });

        taskEls.forEach(task => container.appendChild(task));
    }

    function buildHoverSort(stageId, column) {
        const hoverMenu = document.createElement("div");
        hoverMenu.innerHTML = `
            <div class="o_hover_sort_btn">⇅</div>
            <div class="o_hover_sort_dropdown d-none">
                <a href="#" data-sort="desc">Newest First</a>
                <a href="#" data-sort="asc">Oldest First</a>
            </div>
        `;
        hoverMenu.classList.add("o_stage_hover_sort");

        const header = column.querySelector(".o_kanban_header");
        if (!header) return;
        header.style.position = "relative";
        header.appendChild(hoverMenu);

        const dropdown = hoverMenu.querySelector(".o_hover_sort_dropdown");

        hoverMenu.addEventListener("mouseenter", () => dropdown.classList.remove("d-none"));
        hoverMenu.addEventListener("mouseleave", () => dropdown.classList.add("d-none"));

        dropdown.querySelectorAll("a").forEach(a => {
            a.addEventListener("click", e => {
                e.preventDefault();
                const order = a.dataset.sort;
                console.log("[📥] Clicked sort:", order, "in stage:", stageId);
                setSortOrder(stageId, order);
                sortTasks(column, order);
            });
        });

        const savedOrder = getSortOrder()[stageId];
        if (savedOrder) {
            console.log("[💾] Applying saved sort order:", savedOrder, "for stage:", stageId);
            sortTasks(column, savedOrder);
        }
    }

    function injectHoverSortToStages() {
        document.querySelectorAll(".o_kanban_group").forEach(column => {
            const stageId = column.dataset.id;
            if (!stageId || column.dataset.sortHoverInjected) return;
            column.dataset.sortHoverInjected = "1";
            buildHoverSort(stageId, column);
        });
    }

    document.addEventListener("DOMContentLoaded", () => {
        injectHoverSortToStages();
        new MutationObserver(injectHoverSortToStages).observe(document.body, {
            childList: true,
            subtree: true,
        });
    });
})();
