/** @odoo-module **/
import { registry } from "@web/core/registry";
import { useEffect, useRef, onMounted } from "@odoo/owl";

const { Component } = owl;

/**
 * Hook để xử lý bộ lọc chatter
 */
export function useChatterFilter() {
    const filterRef = useRef("chatterFilter");
    
    useEffect(() => {
        const setupFilter = () => {
            const filterSelect = document.getElementById("chatter_filter_select");
            if (!filterSelect) return;
            
            // Xóa event listener cũ để tránh trùng lặp
            filterSelect.removeEventListener("change", applyFilter);
            // Thêm event listener mới
            filterSelect.addEventListener("change", applyFilter);
            
            // Áp dụng bộ lọc ban đầu
            applyFilter();
        };
        
        const applyFilter = () => {
            const filterSelect = document.getElementById("chatter_filter_select");
            if (!filterSelect) return;
            
            const filterType = filterSelect.value;
            const chatter = document.querySelector(".o-mail-Chatter-content");
            if (!chatter) return;
            
            console.log("Đang lọc theo:", filterType);
            
            // Lấy các phần tử cần lọc
            const messages = chatter.querySelectorAll('.o-mail-Message[aria-label="Message"]');
            const notes = chatter.querySelectorAll('.o-mail-Message[aria-label="Note"]');
            const activities = chatter.querySelectorAll(".o-mail-ActivityList");
            
            // Ẩn tất cả trước
            chatter.querySelectorAll(".o-mail-Message, .o-mail-ActivityList").forEach(el => {
                el.style.display = "none";
            });
            
            // Áp dụng bộ lọc
            switch (filterType) {
                case "all":
                    messages.forEach(el => el.style.display = "");
                    notes.forEach(el => el.style.display = "");
                    activities.forEach(el => el.style.display = "");
                    break;
                case "message":
                    messages.forEach(el => el.style.display = "");
                    break;
                case "note":
                    notes.forEach(el => el.style.display = "");
                    break;
                case "activity":
                    activities.forEach(el => el.style.display = "");
                    break;
            }
        };
        
        // Thiết lập MutationObserver để phát hiện khi DOM thay đổi
        const observer = new MutationObserver((mutations) => {
            for (const mutation of mutations) {
                if (mutation.addedNodes.length > 0) {
                    // Kiểm tra xem chatter có được thêm vào không
                    if (document.querySelector(".o-mail-Chatter-content") &&
                        document.getElementById("chatter_filter_select")) {
                        setupFilter();
                        break;
                    }
                }
            }
        });
        
        // Bắt đầu quan sát DOM
        observer.observe(document.body, { childList: true, subtree: true });
        
        // Thử thiết lập ngay lập tức trong trường hợp các phần tử đã tồn tại
        setupFilter();
        
        // Dọn dẹp khi component bị hủy
        return () => {
            observer.disconnect();
            const filterSelect = document.getElementById("chatter_filter_select");
            if (filterSelect) {
                filterSelect.removeEventListener("change", applyFilter);
            }
        };
    });
}

/**
 * Patch cho ChatterContainer để thêm tính năng lọc
 */
export class ChatterFilterPatch extends Component {
    setup() {
        super.setup();
        useChatterFilter();
    }
}

// Đăng ký hook để sử dụng với các component khác
registry.category("hooks").add("useChatterFilter", useChatterFilter);

// Hoặc sử dụng trực tiếp bằng cách lắng nghe sự kiện trang web
document.addEventListener("DOMContentLoaded", () => {
    // Thiết lập quan sát DOM cho trường hợp Odoo load xong
    const observer = new MutationObserver((mutations) => {
        // Kiểm tra xem chatter đã được load chưa
        if (document.querySelector(".o-mail-Chatter-content") &&
            document.getElementById("chatter_filter_select")) {
            setupChatterFilter();
            // Có thể ngừng quan sát sau khi đã thiết lập
            // observer.disconnect();
        }
    });
    
    observer.observe(document.body, { childList: true, subtree: true });
    
    // Thử thiết lập ngay lập tức trong trường hợp đã load xong
    setupChatterFilter();
});

function setupChatterFilter() {
    const filterSelect = document.getElementById("chatter_filter_select");
    if (!filterSelect) return;
    
    // Xóa event listener cũ để tránh trùng lặp
    filterSelect.removeEventListener("change", applyFilter);
    // Thêm event listener mới
    filterSelect.addEventListener("change", applyFilter);
    
    // Áp dụng bộ lọc ban đầu nếu cần
    applyFilter();
}

function applyFilter() {
    const filterSelect = document.getElementById("chatter_filter_select");
    if (!filterSelect) return;
    
    const filterType = filterSelect.value;
    const chatter = document.querySelector(".o-mail-Chatter-content");
    if (!chatter) return;
    
    // Lấy các phần tử cần lọc
    const messages = chatter.querySelectorAll('.o-mail-Message[aria-label="Message"]');
    const notes = chatter.querySelectorAll('.o-mail-Message[aria-label="Note"]');
    const systemNotifications = chatter.querySelectorAll('.o-mail-Message[aria-label="System notification"]');
    const activities = chatter.querySelectorAll(".o-mail-ActivityList");
    
    // Ẩn tất cả trước
    chatter.querySelectorAll(".o-mail-Message, .o-mail-ActivityList").forEach(el => {
        el.style.display = "none";
    });
    
    // Áp dụng bộ lọc
    switch (filterType) {
        case "all":
            messages.forEach(el => el.style.display = "");
            notes.forEach(el => el.style.display = "");
            activities.forEach(el => el.style.display = "");
            systemNotifications.forEach(el => el.style.display = "");
            break;
        case "message":
            messages.forEach(el => el.style.display = "");
            break;
        case "note":
            notes.forEach(el => el.style.display = "");
            break;
        case "activity":
            activities.forEach(el => el.style.display = "");
            break;
    }
}