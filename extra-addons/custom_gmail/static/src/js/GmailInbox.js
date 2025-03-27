/** @odoo-module **/

import { Component, onMounted } from "@odoo/owl";
import { rpc } from "@web/core/network/rpc";
import { registry } from "@web/core/registry";
import { initCKEditor, loadCKEditor } from "./ckeditor";
import { onForward, onReply, onReplyAll, toggleStar } from "./functions/index";
import { openComposeModal } from "./functions/openComposeModal";
import { initialState } from "./state";
import { loadStarredState, saveStarredState } from "./storageUtils";
import template from "./template";
import { getInitialBgColor, getInitialColor, getStatusText, hideIcons, nextPage, onMoreActions, onRefresh, prevPage, showIcons, toggleAccounts, toggleDropdown, toggleDropdownAccount, toggleDropdownVertical, toggleSelect, toggleSelectAll, toggleThreadMessage } from "./uiUtils";
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
    async loadMessages() {
        try {
            const messages = await rpc('/gmail/messages', {});
            this.state.messages = messages;
        } catch (error) {
            console.error("Error fetching Gmail messages:", error);
        }
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
        this.state.showComposeModal = !this.state.showComposeModal;
    
        if (this.state.showComposeModal) {
            setTimeout(() => initCKEditor(), 100);
        } else if (window.editorInstance) {
            window.editorInstance.destroy();
            window.editorInstance = null;
        }
    }

    onNewEmail(ev) {
        ev.stopPropagation();
        this.openComposeModal("new");
    }

    onSendEmail() {
        const to = document.querySelector('.compose-input.to').value;
        const subject = document.querySelector('.compose-input.subject').value;
        let body = window.editorInstance ? window.editorInstance.getData() : '';
    
        // Fix bảng không có border
        body = body.replace(/<table/g, '<table border="1" cellspacing="0" cellpadding="4" style="border-collapse:collapse;"');
    
        if (!to) {
            alert("Vui lòng nhập địa chỉ email.");
            return;
        }
    
        rpc('/web/dataset/call_kw/mail.mail/create_and_send_email', {
            model: 'mail.mail',
            method: 'create_and_send_email',
            args: [{
                email_to: to,
                subject: subject,
                body_html: body,
            }],
            kwargs: {},
        }).then(() => {
            alert("Đã gửi email thành công!");
            this.state.showComposeModal = false;
    
            if (window.editorInstance) {
                window.editorInstance.destroy();
                window.editorInstance = null;
            }
    
            document.querySelector('.compose-input.to').value = '';
            document.querySelector('.compose-input.subject').value = '';
        }).catch((err) => {
            console.error("Lỗi khi gửi RPC:", err);
            alert("Có lỗi xảy ra khi gửi email.");
        });
    }
    
    
    
}

GmailInbox.template = template;
registry.category("actions").add("gmail_inbox_ui", GmailInbox);
export default GmailInbox;