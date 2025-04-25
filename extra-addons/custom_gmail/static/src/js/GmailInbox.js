/** @odoo-module **/
import { Component, onMounted } from "@odoo/owl";
import { rpc } from "@web/core/network/rpc";
import { registry } from "@web/core/registry";
import { initCKEditor, loadCKEditor } from "./ckeditor";
import { onForward, onReply, onReplyAll, onSendEmail, toggleStar } from "./functions/index";
import { openComposeModal } from "./functions/openComposeModal";
import { initialState } from "./state";
import { loadStarredState, saveStarredState } from "./storageUtils";
import template from "./template";
import {
    getInitialBgColor,
    getInitialColor,
    getStatusText,
    onCloseCompose,
    onRefresh,
    openFilePreview,
    toggleAccounts,
    toggleDropdown,
    toggleDropdownAccount,
    toggleDropdownVertical,
    toggleSelect,
    toggleSelectAll,
    toggleThreadMessage,
} from "./uiUtils";

async function getCurrentUserId() {
    const result = await rpc("/web/session/get_session_info");
    return result.uid;
}
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
        this.addGmailAccount = this._addGmailAccount;
        this.switchTab = this._switchTab.bind(this);
        this.state.messagesByEmail = {};
        this.state.currentPage = 1;
        this.state.pageSize = 15;
        this.state.pagination = {
            email: "",
            pageToken: null,
            nextPageToken: null,
            previousPageToken: null,
            messages: [],
        };
        // 👇 Khôi phục các tab tài khoản đã lưu trong localStorage
        const savedAccounts = localStorage.getItem("gmail_accounts");
        if (savedAccounts) {
            this.state.accounts = JSON.parse(savedAccounts);
            if (this.state.accounts.length > 0) {
                this.state.activeTabId = this.state.accounts[0].id;
                this.loadMessages(this.state.accounts[0].email);
            }
        }
        onMounted(async () => {
            const currentUserId = await getCurrentUserId();
        
            // Ưu tiên lấy từ DB
            const dbAccounts = await rpc("/gmail/my_accounts");
            if (dbAccounts.length > 0) {
                this.state.accounts = dbAccounts;
                this.state.activeTabId = dbAccounts[0].id;
                this.loadMessages(dbAccounts[0].email);
            } else {
                // Nếu DB không có → lấy từ localStorage theo user
                const savedAccounts = localStorage.getItem(`gmail_accounts_user_${currentUserId}`);
                if (savedAccounts) {
                    this.state.accounts = JSON.parse(savedAccounts);
                    if (this.state.accounts.length > 0) {
                        this.state.activeTabId = this.state.accounts[0].id;
                        this.loadMessages(this.state.accounts[0].email);
                    }
                }
            }
        
            this.loadAuthenticatedEmail();
        });
        
        
        
    }
    
    async loadMessages(email, pageToken = null) {
        this.state.loading = true;
        const result = await rpc("/gmail/messages", {
            email,
            page_token: pageToken,
        });
    
        this.state.pagination = {
            email,
            pageToken,
            messages: result.messages || [],
            nextPageToken: result.next_page_token || null,
            previousPageToken: result.previous_page_token || null,
            startIndex: result.start_index || 0,
            total: result.total || 0,
        };
        this.state.loading = false
    }
    
    
    

    
    async loadAuthenticatedEmail() {
        try {
            const result = await rpc("/gmail/user_email", {});
            this.state.email = result.email || "No Email";
        } catch (error) {
            this.state.email = "Error loading email";
        }
    }

    onMessageClick(msg) {
        if (!msg) return;
        this.state.selectedMessage = msg;
        const threadId = msg.thread_id;
        const thread = threadId ? this.state.threads?.[threadId] : null;
        this.state.currentThread = Array.isArray(thread) && thread.length ? thread : [msg];

        if (msg.unread) {
            msg.unread = false;
            this.updateMessage(msg);
        }
    }

    updateMessage(msg) {
        const index = this.state.messages.findIndex((m) => m.id === msg.id);
        if (index !== -1) this.state.messages[index] = { ...msg };

        if (msg.thread_id && this.state.threads[msg.thread_id]) {
            const threadIndex = this.state.threads[msg.thread_id].findIndex((m) => m.id === msg.id);
            if (threadIndex !== -1) {
                this.state.threads[msg.thread_id][threadIndex] = { ...msg };
            }
        }

        if (this.state.selectedMessage?.id === msg.id) {
            this.state.selectedMessage = { ...msg };
        }

        if ("starred" in msg) this.saveStarredState();
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

    _addGmailAccount = async () => {
        const currentUserId = await getCurrentUserId();
        const popup = window.open("", "_blank", "width=700,height=800");
        popup.location.href = "/gmail/auth/start";
    
        if (!popup) {
            console.error("❌ Không thể mở popup xác thực Gmail.");
            return;
        }
    
        const handleMessage = async (event) => {
            if (event.data === "gmail-auth-success") {
                console.log("📩 Đã nhận gmail-auth-success từ popup");
    
                try {
                    const res = await fetch("/gmail/current_user_info", {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json",
                            "X-Requested-With": "XMLHttpRequest",
                        },
                        body: JSON.stringify({
                            jsonrpc: "2.0",
                            method: "call",
                            params: {},
                        }),
                    });
    
                    const json = await res.json();
                    console.log("📬 Gmail current_user_info:", json);
    
                    if (json.result?.status === "success" && typeof json.result.email === "string") {
                        const email = json.result.email;
    
                        const exists = this.state.accounts.some((acc) => acc.email === email);
                        if (!exists) {
                            const newId = Date.now() + Math.floor(Math.random() * 1000);
                            const newAccount = {
                                id: newId,
                                email,
                                name: email.split("@")[0],
                                initial: email[0].toUpperCase(),
                                status: "active",
                                messages: [],
                                selectedMessage: null,
                                currentThread: [],
                            };
                            this.state.accounts.push(newAccount);
                            this.state.activeTabId = newId;
                            this.loadMessages(email);
    
                            // ✅ Lưu localStorage theo user
                            localStorage.setItem(
                                `gmail_accounts_user_${currentUserId}`,
                                JSON.stringify(this.state.accounts)
                            );
                        } else {
                            const existing = this.state.accounts.find((acc) => acc.email === email);
                            this.state.activeTabId = existing.id;
                        }
                    }
    
                } catch (error) {
                    console.error("❌ Lỗi khi lấy current_user_info:", error);
                }
    
                window.removeEventListener("message", handleMessage);
            }
        };
    
        window.addEventListener("message", handleMessage);
    };
    
    
    
    _switchTab = (accountId) => {
        this.state.activeTabId = accountId;
        const acc = this.state.accounts.find((a) => a.id === accountId);
        if (acc) {
            this.loadMessages(acc.email);
        }
    };
    

    closeTab = async (accountId) => {
        const currentUserId = await getCurrentUserId();
    
        await rpc("/gmail/delete_account", {
            account_id: accountId,
        });
    
        const index = this.state.accounts.findIndex(acc => acc.id === accountId);
        if (index !== -1) {
            this.state.accounts.splice(index, 1);
    
            if (this.state.activeTabId === accountId) {
                this.state.activeTabId = this.state.accounts[0]?.id || null;
                if (this.state.activeTabId) {
                    const acc = this.state.accounts.find(a => a.id === this.state.activeTabId);
                    if (acc) {
                        this.loadMessages(acc.email);
                    }
                } else {
                    this.state.messages = [];
                }
            }
    
            // ✅ Cập nhật localStorage theo user
            localStorage.setItem(
                `gmail_accounts_user_${currentUserId}`,
                JSON.stringify(this.state.accounts)
            );
        }
    };
    
    getPaginatedMessages(email) {
        return this.state.pagination.messages || [];
    }
    
    
    getPaginationInfo(email) {
        const { startIndex, messages, total } = this.state.pagination;
        const start = (startIndex || 0) + 1;
        const end = start + (messages?.length || 0) - 1;
    
        return { start, end, total };
    }
    
    
    
    nextPage() {
        const email = this.getActiveEmail();
        const nextToken = this.state.pagination.nextPageToken;
        if (nextToken) {
            this.loadMessages(email, nextToken);
        }
    }
    
    prevPage() {
        const email = this.getActiveEmail();
        const prevToken = this.state.pagination.previousPageToken;
        if (prevToken) {
            this.loadMessages(email, prevToken);
        }
    }
    
    
    getActiveEmail() {
        const activeAccount = this.state.accounts.find(acc => acc.id === this.state.activeTabId);
        return activeAccount ? activeAccount.email : "";
    }
    prevPageToken() {
        const token = parseInt(this.state.pagination.pageToken || 0);
        return Math.max(token - 15, 0);
    } 
    
    
    
}

GmailInbox.template = template;
registry.category("actions").add("gmail_inbox_ui", GmailInbox);
export default GmailInbox;
