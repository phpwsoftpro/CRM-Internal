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
    
        // Các method binding
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
        this.addOutlookAccount = this._addOutlookAccount;
        this.switchTab = this._switchTab.bind(this);


        this.state.messagesByEmail = {};
    
        // 👇 Khôi phục tài khoản từ localStorage (nếu chưa có database)
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
    
            // Fetch accounts từ server
            const gmailAccounts = await rpc("/gmail/my_accounts");
            const outlookAccounts = await rpc("/outlook/my_accounts");
    
            const mergedAccounts = [...gmailAccounts, ...outlookAccounts];
    
            if (mergedAccounts.length > 0) {
                this.state.accounts = mergedAccounts;
                this.state.activeTabId = mergedAccounts[0].id;
                this.loadMessages(mergedAccounts[0].email);
            } else {
                // Nếu không có thì fallback localStorage
                const savedAccounts = localStorage.getItem(`gmail_accounts_user_${currentUserId}`);
                if (savedAccounts) {
                    this.state.accounts = JSON.parse(savedAccounts);
                    if (this.state.accounts.length > 0) {
                        this.state.activeTabId = this.state.accounts[0].id;
                        this.loadMessages(this.state.accounts[0].email);
                    }
                }
            }
    
            // Gọi các hàm load authenticated email
            await this.loadAuthenticatedEmail();
            await this.loadOutlookAuthenticatedEmail();
        });
    }
    
    async loadGmailMessages(email) {
        const messages = await rpc("/gmail/messages", { email });
        this.state.messagesByEmail[email] = messages;
        this.state.messages = messages;
    }
    
    async loadOutlookMessages(email) {
        const res = await rpc("/outlook/messages");
        // console.log("📬 Outlook messages res:", res);
        if (res.status === "ok") {
            const messages = res.messages.map((msg) => ({ ...msg, type: "outlook" }));
            this.state.messagesByEmail[email] = messages;
            this.state.messages = messages;
        } else {
            console.warn("⚠️ Outlook fetch failed:", res.message);
            this.state.messages = [];
        }
    }
    
    
    async loadMessages(email) {
        this.state.messages = [];
    
        const acc = this.state.accounts.find(a => a.email === email);
        if (!acc) {
            console.warn("⚠️ Không tìm thấy account với email", email);
            return;
        }
    
        if (this.state.messagesByEmail[email]) {
            this.state.messages = this.state.messagesByEmail[email];
            return;
        }
    
        if (acc.type === 'outlook') {
            await this.loadOutlookMessages(email);
        } else if (acc.type === 'gmail') {
            await this.loadGmailMessages(email);
        } else {
            console.warn("⚠️ Unknown account type:", acc.type);
        }
    }
    
    
    async loadAuthenticatedEmail() {
        try {
            const result = await rpc("/gmail/user_email", {});
            this.state.gmail_email = result.email || "No Email"; // <-- gmail_email riêng
        } catch (error) {
            this.state.gmail_email = "Error loading Gmail";
        }
    }
    async loadOutlookAuthenticatedEmail() {
        try {
            const result = await rpc("/outlook/user_email", {});
            this.state.outlook_email = result.email || "No Email"; // <-- outlook_email riêng
        } catch (error) {
            this.state.outlook_email = "Error loading Outlook";
        }
    }
    
    async onMessageClick(msg) {
        if (!msg) return;
    
        this.state.selectedMessage = msg;
        const threadId = msg.thread_id;
        const thread = threadId ? this.state.threads?.[threadId] : null;
        this.state.currentThread = Array.isArray(thread) && thread.length ? thread : [msg];
    
        // ✅ Log để debug
        // console.log("💬 Clicked message:", msg);
    
        // ✅ Nếu là Outlook và body chưa có
        if (
            (msg.type === "outlook" || (msg.from && msg.from.includes("@outlook"))) &&
            (!msg.body || msg.body === "No Content")
        ) {
            // console.log("📩 Fetching full body for Outlook:", msg.id);
            try {
                const res = await rpc("/outlook/message_detail", { message_id: msg.id });
                if (res.status === "ok") {
                    msg.body = res.body || "No Content";
                    this.updateMessage(msg);
                } else {
                    console.warn("⚠️ Không lấy được nội dung chi tiết:", res.message);
                }
            } catch (err) {
                console.error("❌ Lỗi khi lấy chi tiết email Outlook:", err);
            }
        }
    
        if (msg.unread) {
            msg.unread = false;
            this.updateMessage(msg);
        }
    }
    
    
    updateMessage(msg) {
        const index = this.state.messages.findIndex((m) => m.id === msg.id);
        if (index !== -1) {
            this.state.messages[index] = { ...msg };
        }
    
        if (msg.thread_id && this.state.threads[msg.thread_id]) {
            const threadIndex = this.state.threads[msg.thread_id].findIndex((m) => m.id === msg.id);
            if (threadIndex !== -1) {
                this.state.threads[msg.thread_id][threadIndex] = { ...msg };
            }
        }
    
        if (this.state.selectedMessage?.id === msg.id) {
            this.state.selectedMessage = { ...msg };
        }
    
        this.state.currentThread = this.state.currentThread.map(m =>
            m.id === msg.id ? { ...msg } : m
        );
        
        if ("starred" in msg) {
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
                                type: "gmail",
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
    
    _addOutlookAccount = async () => {
        const currentUserId = await getCurrentUserId();
        const popup = window.open("", "_blank", "width=700,height=800");
        popup.location.href = "/outlook/auth/start";
    
        if (!popup) {
            console.error("❌ Không thể mở popup xác thực Outlook.");
            return;
        }
    
        const handleMessage = async (event) => {
            if (event.data === "outlook-auth-success") {
                console.log("📩 Đã nhận outlook-auth-success từ popup");
    
                try {
                    const res = await fetch("/outlook/current_user_info", {
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
                    // console.log("📬 Outlook current_user_info:", json);
    
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
                                type: "outlook", 
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
                    console.error("❌ Lỗi khi lấy outlook current_user_info:", error);
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
    
        const acc = this.state.accounts.find(a => a.id === accountId);
        if (!acc) {
            console.warn(`⚠️ Account ID ${accountId} not found.`);
            return;
        }
    
        try {
            if (acc.type === 'gmail') {
                await rpc("/gmail/delete_account", { account_id: accountId });
            } else if (acc.type === 'outlook') {
                await rpc("/outlook/delete_account", { account_id: accountId });
            }
        } catch (error) {
            console.error("❌ Error deleting account:", error);
        }
    
        const index = this.state.accounts.findIndex(a => a.id === accountId);
        if (index !== -1) {
            this.state.accounts.splice(index, 1);
    
            if (this.state.activeTabId === accountId) {
                const firstAccount = this.state.accounts[0];
                this.state.activeTabId = firstAccount ? firstAccount.id : null;
                if (firstAccount) {
                    await this.loadMessages(firstAccount.email);
                } else {
                    this.state.messages = [];
                }
            }
    
            // ✅ Update localStorage chính xác theo user
            localStorage.setItem(
                `gmail_accounts_user_${currentUserId}`,
                JSON.stringify(this.state.accounts)
            );
        }
    };  
}

GmailInbox.template = template;
registry.category("actions").add("gmail_inbox_ui", GmailInbox);
export default GmailInbox;