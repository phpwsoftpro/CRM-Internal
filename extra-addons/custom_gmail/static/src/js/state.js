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
        threads: {},
        showComposeModal: false,
        showDropdown: false,
        showDropdownVertical: false,
        showAccountDropdown: false,
        showAccounts: false,
    });
}
