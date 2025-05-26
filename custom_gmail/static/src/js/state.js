/** @odoo-module **/
import { useState } from "@odoo/owl";
 
export function initialState() {
    return useState({
        accounts: [],
        activeTabId: null,
        email: "",
        selectedAccount: null,
        selectedMessage: null,
        currentThread: [],
        messages: [],
        messagesByEmail: {}, // ✅ THÊM DÒNG NÀY
        threads: {},
        showComposeModal: false,
        showDropdown: false,
        showDropdownVertical: false,
        showAccountDropdown: false,
        showAccounts: false,

        pagination: {
            currentPage: 1,
            pageSize: 15,
            totalPages: 1,
            total: 0,
        },
    });
}
