/** @odoo-module **/
document.addEventListener("DOMContentLoaded", () => {
    const observer = new MutationObserver((mutations) => {
        // Kiểm tra xem chatter đã được load chưa
        if (document.querySelector(".o-mail-Chatter-content") &&
            document.getElementById("chatter_filter_select")) {
            setupChatterFilter();
        }
    });
    
    observer.observe(document.body, { childList: true, subtree: true });
    
    // Thử thiết lập ngay lập tức trong trường hợp đã load xong
    setupChatterFilter();
});

function setupChatterFilter() {
    const filterSelect = document.getElementById("chatter_filter_select");
    if (!filterSelect) return;
    
    filterSelect.value = "message";
    
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