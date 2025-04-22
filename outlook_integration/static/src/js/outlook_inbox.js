/** @odoo-module **/
import { Component, markup, onMounted } from "@odoo/owl";
import { rpc } from "@web/core/network/rpc";
import { registry } from "@web/core/registry";
import { initCKEditor, loadCKEditor } from "./ckeditor";
import { onForward, onReply, onReplyAll, toggleStar } from "./functions/index";
import { openComposeModal } from "./functions/openComposeModal";
import { initialState } from "./state";
import { loadStarredState, saveStarredState } from "./storageUtils";
import template from "./template";
import { getInitialBgColor, getInitialColor, getStatusText, onRefresh,toggleAccounts, toggleDropdown, toggleDropdownAccount, toggleDropdownVertical, toggleSelect, toggleSelectAll, toggleThreadMessage, onCloseCompose, openFilePreview } from "./uiUtils";
import { onSendEmail } from "./functions/index";
export class GmailInbox extends Component {
    setup() {
        this.state = initialState();

        this.toggleStar = toggleStar.bind(this);
        this.onReply = onReply.bind(this);
        this.onReplyAll = onReplyAll.bind(this);
        this.onForward = onForward.bind(this);
        this.toggleDropdown = toggleDropdown.bind(this);
        this.toggleDropdownVertical = toggleDropdownVertical.bind(this);
        this.toggleAccounts = toggleAccounts.bind(this);
        this.toggleDropdownAccount = toggleDropdownAccount.bind(this);
        this.toggleSelectAll = toggleSelectAll.bind(this);
        this.onRefresh = onRefresh.bind(this);
        this.saveStarredState = saveStarredState.bind(this);
        this.loadStarredState = loadStarredState.bind(this);
        this.initCKEditor = initCKEditor.bind(this);
        this.loadCKEditor = loadCKEditor.bind(this);
        this.getInitialColor = getInitialColor.bind(this); 
        this.getInitialBgColor = getInitialBgColor.bind(this);
        this.getStatusText = getStatusText.bind(this);
        this.toggleSelect = toggleSelect.bind(this);
        this.openComposeModal = openComposeModal.bind(this);
        this.toggleThreadMessage = toggleThreadMessage.bind(this);
        this.onCloseCompose = onCloseCompose.bind(this);
        this.onSendEmail = onSendEmail.bind(this);
        this.openFilePreview = openFilePreview;
        onMounted(() => {
            this.loadMessages();
            this.loadAuthenticatedEmail();
            this.state.selectedAccount = this.state.accounts[0];
        });
    }
    async loadMessages() {
        try {
            const messages = await rpc('/gmail/messages', {});
            this.state.messages = messages.map(msg => ({
                ...msg,
                body: markup(msg.body),  // ✅ Đánh dấu HTML là an toàn để t-raw dùng
            }));
        } catch (error) {
            console.error("Error fetching Gmail messages:", error);
        }
    }
    async loadAuthenticatedEmail() {
        try {
            const result = await rpc('/gmail/user_email', {});
            this.state.email = result.email || "No Email";
        } catch (error) {
            this.state.email = "Error loading email";
        }
    }
    onMessageClick(msg) {
        if (!msg) {
            console.warn("No message provided to onMessageClick");
            return;
        }
    
        // Set selected message
        this.state.selectedMessage = msg;
    
        // Load thread if available
        const threadId = msg.thread_id;
        const thread = threadId ? this.state.threads?.[threadId] : null;
    
        if (Array.isArray(thread) && thread.length > 0) {
            this.state.currentThread = thread;
        } else {
            // Fallback: single message only
            this.state.currentThread = [msg];
        }
    
        // Mark as read if unread
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
        this.state.showComposeModal = !this.state.showComposeModal;
    
        if (this.state.showComposeModal) {
            setTimeout(() => initCKEditor(), 100);
        } else if (window.editorInstance) {
            window.editorInstance.destroy();
            window.editorInstance = null;
        }
    }
}

GmailInbox.template = template;
registry.category("actions").add("gmail_inbox_ui", GmailInbox);
export default GmailInbox;