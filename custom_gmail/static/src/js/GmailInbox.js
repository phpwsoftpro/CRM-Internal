/** @odoo-module **/

import { Component, onMounted } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { initialState } from "./state";
import { loadMessages, toggleStar, onReply, onReplyAll, onForward } from "./functions/index";
import { toggleDropdown, toggleDropdownVertical, toggleAccounts, toggleDropdownAccount, toggleSelectAll, prevPage, nextPage, onRefresh, onMoreActions, showIcons, hideIcons, getInitialBgColor, getInitialColor, getStatusText, toggleSelect, toggleThreadMessage } from "./uiUtils";
import { saveStarredState, loadStarredState } from "./storageUtils";
import { initCKEditor, loadCKEditor } from "./ckeditor";
import { openComposeModal } from "./functions/openComposeModal";
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
        this.toggleSelect = toggleSelect.bind(this);
        this.openComposeModal = openComposeModal.bind(this);
        this.toggleThreadMessage = toggleThreadMessage.bind(this);
        onMounted(() => {
            this.loadMessages();
            this.state.selectedAccount = this.state.accounts[0];
        });
    }

    onMessageClick(msg) {
        // Set the selected message
        this.state.selectedMessage = msg;
        
        // If message has a thread_id, load the thread
        if (msg.thread_id && this.state.threads[msg.thread_id]) {
            this.state.currentThread = this.state.threads[msg.thread_id];
        } else {
            // If no thread, just show the single message
            this.state.currentThread = [msg];
        }
        
        // Mark message as read
        if (msg.unread) {
            msg.unread = false;
            this.updateMessage(msg);
        }
    }
    updateMessage(msg) {
        // Find message in main messages list and update it
        const index = this.state.messages.findIndex(m => m.id === msg.id);
        if (index !== -1) {
            this.state.messages[index] = {...msg};
        }
        
        // Also update in threads if present
        if (msg.thread_id && this.state.threads[msg.thread_id]) {
            const threadIndex = this.state.threads[msg.thread_id].findIndex(m => m.id === msg.id);
            if (threadIndex !== -1) {
                this.state.threads[msg.thread_id][threadIndex] = {...msg};
            }
        }
        
        // If this is the selected message, update that too
        if (this.state.selectedMessage && this.state.selectedMessage.id === msg.id) {
            this.state.selectedMessage = {...msg};
        }
        
        // Persist starred state if necessary
        if ('starred' in msg) {
            this.saveStarredState();
        }
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