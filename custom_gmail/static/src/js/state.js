/** @odoo-module **/

import { useState } from "@odoo/owl";

export function initialState() {
    return useState({
        messages: [],
        selectedMessage: null,
        showComposeModal: false,
        emails: [],
        currentPage: 1,
        totalPages: 1,
        allSelected: false,
        range_display: "1-50 of 137",
        showDropdown: false,
        showDropdownVertical: false,
        composeMode: "new", // 'new', 'reply', 'replyAll', 'forward'
        accounts: [
            { id: 1, name: "Robert", email: "robert@wsoftpro.com", status: "active", initial: "R", managed: "Managed by wsoftpro.com" },
            { id: 2, name: "Vanessa Ha", email: "vanessa@wsoftpro.com", status: "expired", initial: "V" },
            { id: 3, name: "Trung Duc", email: "trung@wsoftpro.com", status: "signed-out", initial: "T" },
            { id: 4, name: "Wsp Dev", email: "wspdev@gmail.com", status: "signed-out", initial: "W" },
            { id: 5, name: "Trung Dao Duc", email: "trungdd.m23sa@usth.edu.vn", status: "signed-out", initial: "T" },
        ],
        selectedAccount: null,
        showAccounts: true,
        showAccountDropdown: false
    });
}