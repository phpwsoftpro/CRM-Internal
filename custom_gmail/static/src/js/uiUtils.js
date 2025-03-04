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
    console.log("Toggle dropdown clicked", this.state.showAccountDropdown);
    this.state.showAccountDropdown = !this.state.showAccountDropdown;
    console.log("After toggle:", this.state.showAccountDropdown);
}

export function toggleSelectAll(ev) {
    const isChecked = ev.target.checked;
    this.state.messages.forEach(msg => {
        msg.selected = isChecked;
    });
    this.render();
}

export function prevPage() {
    if (this.state.currentPage > 1) {
        this.state.currentPage--;
        this.loadEmails();
    }
}

export function nextPage() {
    if (this.state.currentPage < this.state.totalPages) {
        this.state.currentPage++;
        this.loadEmails();
    }
}

export function onRefresh() {
    this.loadEmails();
}

export function onMoreActions() {
    console.log("Show more actions menu");
}

export function showIcons(msg) {
    msg.showIcons = true;
    this.render();
}

export function hideIcons(msg) {
    msg.showIcons = false;
    this.render();
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