/** @odoo-module **/

export function toggleDropdown(ev) {
    ev.stopPropagation();
    this.state.showDropdown = !this.state.showDropdown;
    this.render();
    if (this.state.showDropdown) {
        document.addEventListener("click", this.closeDropdown);
    }
}

export function closeDropdown(ev) {
    if (!ev.target.closest(".dropdown-menu-caret") && !ev.target.closest(".icon-btn-option")) {
        this.state.showDropdown = false;
        this.render();
        document.removeEventListener("click", this.closeDropdown);
    }
}

export function toggleDropdownVertical() {
    this.state.showDropdownVertical = !this.state.showDropdownVertical;
}

export function toggleAccounts() {
    this.state.showAccounts = !this.state.showAccounts;
}

export function toggleDropdownAccount() {
    this.state.showAccountDropdown = !this.state.showAccountDropdown;
}

export function toggleSelectAll(ev) {
    const isChecked = ev.target.checked;
    this.state.pagination.messages.forEach(msg => {
        msg.selected = isChecked;
    });
    this.render();
}
export function toggleSelect(msg) {
    msg.selected = !msg.selected;
    this.render();
}
export function toggleThreadMessage(threadMsg) {
    if (threadMsg) {
        threadMsg.collapsed = !threadMsg.collapsed;
        this.render();
    }
}

export function onRefresh() {
    this.loadEmails();
}


export function getStatusText(status) {
    switch (status) {
        case 'expired': return 'Session expired';
        case 'signed-out': return 'Signed out';
        default: return '';
    }
}

export function getInitialColor(initial) {
    const colors = {
        'R': '#5f6368',
        'V': '#1a73e8',
        'T': '#9c27b0',
        'W': '#673ab7'
    };
    return colors[initial] || '#5f6368';
}

export function getInitialBgColor(initial) {
    const colors = {
        'R': '#e8eaed',
        'V': '#e8f0fe',
        'T': '#f3e5f5',
        'W': '#ede7f6'
    };
    return colors[initial] || '#e8eaed';
}
export function onCloseCompose() {
    this.state.showComposeModal = false;
    if (this.editorInstance) {
        this.editorInstance = null;
    }
}
export function openFilePreview(ev) {
    const link = ev.currentTarget;
    const url = link.getAttribute("data-url");
    const modal = document.getElementById("filePreviewModal");
    const iframe = document.getElementById("filePreviewFrame");

    // Đảm bảo không có ?download=true ở URL
    iframe.src = url; // hoặc `${url}?inline=1`
    modal.style.display = "block";
}
