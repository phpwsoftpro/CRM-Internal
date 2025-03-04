/** @odoo-module **/

import { Component, onMounted } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { initialState } from "./state";
import { loadMessages, toggleStar, onReply, onReplyAll, onForward } from "./emailActions";
import { toggleDropdown, toggleDropdownVertical, toggleAccounts, toggleDropdownAccount, toggleSelectAll, prevPage, nextPage, onRefresh, onMoreActions, showIcons, hideIcons, getInitialBgColor, getInitialColor, getStatusText } from "./uiUtils";
import { saveStarredState, loadStarredState } from "./storageUtils";
import { initCKEditor, loadCKEditor } from "./ckeditor";
import template from "./template";
export class GmailInbox extends Component {
    setup() {
        this.state = initialState();

        this.loadMessages = loadMessages.bind(this);
        this.toggleStar = toggleStar.bind(this);
        this.onReply = onReply.bind(this);
        this.onReplyAll = onReplyAll.bind(this);
        this.onForward = onForward.bind(this);
        this.toggleDropdown = toggleDropdown.bind(this);
        this.toggleDropdownVertical = toggleDropdownVertical.bind(this);
        this.toggleAccounts = toggleAccounts.bind(this);
        this.toggleDropdownAccount = toggleDropdownAccount.bind(this);
        this.toggleSelectAll = toggleSelectAll.bind(this);
        this.prevPage = prevPage.bind(this);
        this.nextPage = nextPage.bind(this);
        this.onRefresh = onRefresh.bind(this);
        this.onMoreActions = onMoreActions.bind(this);
        this.saveStarredState = saveStarredState.bind(this);
        this.loadStarredState = loadStarredState.bind(this);
        this.showIcons = showIcons.bind(this);
        this.hideIcons = hideIcons.bind(this);
        this.initCKEditor = initCKEditor.bind(this);
        this.loadCKEditor = loadCKEditor.bind(this);
        this.getInitialColor = getInitialColor.bind(this); 
        this.getInitialBgColor = getInitialBgColor.bind(this);
        this.getStatusText = getStatusText.bind(this);
        onMounted(() => {
            this.loadMessages();
            this.state.selectedAccount = this.state.accounts[0];
        });
    }

    onMessageClick(msg) {
        this.state.selectedMessage = msg;
    }

    onComposeClick() {
        this.state.showComposeModal = true;
        setTimeout(() => this.initCKEditor(), 100);
    }

    onCloseCompose() {
        this.state.showComposeModal = false;
        if (this.editorInstance) {
            this.editorInstance.destroy();
            this.editorInstance = null;
        }
    }

    onNewEmail(ev) {
        ev.stopPropagation();
        this.openComposeModal("new");
    }
}

GmailInbox.template = template;
registry.category("actions").add("gmail_inbox_ui", GmailInbox);
export default GmailInbox;