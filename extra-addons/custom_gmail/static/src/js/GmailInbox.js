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
        this.state.isLoading = false;
        this.onRefresh = this.onRefresh.bind(this);
        this.showHeaderPopup = this.showHeaderPopup.bind(this);
        this.closeHeaderPopup = this.closeHeaderPopup.bind(this);
        this.state.showHeaderPopup = false;
        this.state.popupMessage = null;

        this.state.messagesByEmail = {};
    
        // 🛑 Khôi phục từ localStorage (ban đầu)
        const savedAccounts = localStorage.getItem("gmail_accounts");
        if (savedAccounts) {
            this.state.accounts = JSON.parse(savedAccounts);
            if (this.state.accounts.length > 0) {
                this.state.activeTabId = this.state.accounts[0].id;
                this.loadMessages(this.state.accounts[0].email);
            }
        }

        // 🔁 Mount chính: Load account
        onMounted(async () => {
            const currentUserId = await getCurrentUserId();
            const gmailAccounts = await rpc("/gmail/my_accounts");
            const outlookAccounts = await rpc("/outlook/my_accounts");
            const mergedAccounts = [...gmailAccounts, ...outlookAccounts];

            if (mergedAccounts.length > 0) {
                this.state.accounts = mergedAccounts;
                this.state.activeTabId = mergedAccounts[0].id;
                this.loadMessages(mergedAccounts[0].email);
            } else {
                const savedAccounts = localStorage.getItem(`gmail_accounts_user_${currentUserId}`);
                if (savedAccounts) {
                    this.state.accounts = JSON.parse(savedAccounts);
                    if (this.state.accounts.length > 0) {
                        this.state.activeTabId = this.state.accounts[0].id;
                        this.loadMessages(this.state.accounts[0].email);
                    }
                }
            }

            // Xác thực email
            await this.loadAuthenticatedEmail();
            await this.loadOutlookAuthenticatedEmail();
            setInterval(() => {
                if (!document.hidden) {
                    for (const account of this.state.accounts) {
                        if (account.type === "gmail") {
                            rpc("/gmail/session/ping", { account_id: parseInt(account.id) })
                                .then((res) => {
                                    if (res.has_new_mail) {
                                        this.state.loading = true;  // 🟡 Bắt đầu loading
                                        this.loadMessages(account.email, true).then(() => {
                                            this.state.loading = false;  // ✅ Kết thúc loading
                                            rpc("/gmail/clear_new_mail_flag", {
                                                account_id: parseInt(account.id),
                                            });
                                        });
                                    }
                                });
                        }
                    }
                }
            }, 30000);

        });
    }

    async onRefresh() {
        if (this.state.isRefreshing) {
            console.warn("🔄 Đang refresh, vui lòng chờ...");
            return;
        }

        const accountId = this.state.activeTabId;
        if (!accountId) {
            console.warn("❌ Không có account được chọn");
            return;
        }

        this.state.isRefreshing = true;
        try {
            const result = await rpc("/gmail/refresh_mail", {
                account_id: accountId,
            });

            if (result.status === "ok") {
                console.log("📬 Đã đồng bộ Gmail!");
                const account = this.state.accounts.find(a => a.id === accountId);
                if (account) {
                    await this.loadMessages(account.email, true);
                }
            } else {
                console.warn("❌ Lỗi khi refresh:", result.error);
            }
        } catch (error) {
            console.error("❌ Lỗi khi gọi API refresh_mail:", error);
        } finally {
            this.state.isRefreshing = false;
        }
    }






    async goNextPage() {
        if (this.state.pagination.currentPage < this.state.pagination.totalPages) {
            const acc = this.state.accounts.find(a => a.id === this.state.activeTabId);
            if (acc) await this.loadGmailMessages(acc.email, this.state.pagination.currentPage + 1);
        }
    }
    
    async goPrevPage() {
        if (this.state.pagination.currentPage > 1) {
            const acc = this.state.accounts.find(a => a.id === this.state.activeTabId);
            if (acc) await this.loadGmailMessages(acc.email, this.state.pagination.currentPage - 1);
        }
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
    
    async loadGmailMessages(email, page = 1) {
    const account = this.state.accounts.find(acc => acc.email === email);
    if (!account) return;

    const res = await rpc("/gmail/messages", {
        account_id: parseInt(account.id),
        page: page,
        limit: this.state.pagination.pageSize,
    });

    // ✅ Gom message theo thread_id
    this.state.threads = {};
    for (const msg of res.messages) {
        // ✅ Làm sạch nội dung để hiển thị
        msg.body_cleaned = msg.body?.split('<div class="gmail_quote">')[0]
                        || msg.body?.replace(/<blockquote[\s\S]*?<\/blockquote>/gi, "")
                        || msg.body;

        // ✅ Bổ sung các trường cần thiết
        msg.sender = msg.sender || msg.email_sender || "Unknown Sender";
        msg.email_receiver = msg.email_receiver || '';
        msg.email_cc = msg.email_cc || '';

        if (msg.thread_id) {
            if (!this.state.threads[msg.thread_id]) {
                this.state.threads[msg.thread_id] = [];
            }
            this.state.threads[msg.thread_id].push(msg);
        }
    }

        // ✅ Sắp xếp mỗi thread theo thời gian tăng dần
        for (const thread_id in this.state.threads) {
            this.state.threads[thread_id].sort((a, b) => new Date(a.date_received) - new Date(b.date_received));
        }

        // ✅ Lấy email mới nhất trong mỗi thread để hiển thị danh sách
        const latestMessagesPerThread = Object.values(this.state.threads).map(threadMsgs => {
            return threadMsgs[threadMsgs.length - 1];  // cuối cùng = mới nhất
        });

        this.state.messagesByEmail[email] = latestMessagesPerThread;
        this.state.messages = latestMessagesPerThread;

        // Phân trang
        this.state.pagination.currentPage = page;
        this.state.pagination.total = res.total;
        this.state.pagination.totalPages = Math.ceil(res.total / this.state.pagination.pageSize);
    }

    async loadMessages(email, forceReload = false) {
        const acc = this.state.accounts.find(a => a.email === email);
        if (!acc) {
            console.warn("⚠️ Không tìm thấy account với email", email);
            return;
        }

        if (forceReload) {
            delete this.state.messagesByEmail[email];
        }

        if (!forceReload && this.state.messagesByEmail[email]) {
            const messages = this.state.messagesByEmail[email];

            // ✅ Re-patch toàn bộ để đảm bảo dữ liệu đủ cho template
            const patchedMessages = messages.map(msg => ({
                ...msg,
                body_cleaned: msg.body?.split('<div class="gmail_quote">')[0]
                            || msg.body?.replace(/<blockquote[\s\S]*?<\/blockquote>/gi, "")
                            || msg.body,
                sender: msg.sender || msg.email_sender || "Unknown Sender",
                email_receiver: msg.email_receiver || '',
                email_cc: msg.email_cc || '',
            }));

            this.state.messages = patchedMessages;

            // ✅ Khôi phục lại threads
            this.state.threads = {};
            for (const msg of patchedMessages) {
                if (msg.thread_id) {
                    if (!this.state.threads[msg.thread_id]) {
                        this.state.threads[msg.thread_id] = [];
                    }
                    this.state.threads[msg.thread_id].push(msg);
                }
            }

            // ✅ Sắp xếp lại thread
            for (const thread_id in this.state.threads) {
                this.state.threads[thread_id].sort((a, b) => new Date(a.date_received) - new Date(b.date_received));
            }

            return;
        }

        

        this.state.loading = true;
        try {
            if (acc.type === 'gmail') {
                await this.loadGmailMessages(email);
            } else if (acc.type === 'outlook') {
                await this.loadOutlookMessages(email);
            }
        } finally {
            this.state.loading = false;
        }
    }
 
    
    async loadAuthenticatedEmail() {
        try {
            const accountId = this.state.activeTabId;
            const result = await rpc("/gmail/user_email", {
                account_id: accountId
            });
            this.state.gmail_email = result.email || "No Email";
            console.log("✅ Gmail email loaded:", this.state.gmail_email);
        } catch (error) {
            console.error("❌ Lỗi khi gọi /gmail/user_email:", error);
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
        console.log("📥 Clicked message:", msg);
        console.log("📨 currentUserEmail:", this.state.gmail_email || this.state.outlook_email);
        console.log("📨 email_receiver:", msg.email_receiver);
        this.state.selectedMessage = msg;
        const threadId = msg.thread_id;
        const thread = threadId ? this.state.threads?.[threadId] : null;

        // ✅ Làm sạch body cho từng email trong thread
        this.state.currentThread = Array.isArray(thread) && thread.length
            ? thread.map(m => ({
                ...m,
                body_cleaned: m.body?.split('<div class="gmail_quote">')[0]
                        || m.body?.replace(/<blockquote[\s\S]*?<\/blockquote>/gi, "")
                        || m.body,
                sender: m.sender || m.email_sender || "Unknown Sender",  // ✅ Dòng quan trọng
                email_receiver: m.email_receiver || '',
                email_cc: m.email_cc || '',
            }))
            : [{
                ...msg,
                body_cleaned: msg.body,
                sender: msg.sender || msg.email_sender || "Unknown Sender",  // ✅ Dòng quan trọng
                email_receiver: msg.email_receiver || '',
                email_cc: msg.email_cc || '',
            }];



        // ✅ Nếu là Outlook và chưa có nội dung chi tiết
        if (
            (msg.type === "outlook" || (msg.from && msg.from.includes("@outlook"))) &&
            (!msg.body || msg.body === "No Content")
        ) {
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

        // ✅ Đánh dấu đã đọc nếu cần
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
                    // Gọi lại danh sách account sau khi xác thực
                    const gmailAccounts = await rpc("/gmail/my_accounts");
                    this.state.accounts = [...gmailAccounts, ...this.state.accounts.filter(a => a.type === "outlook")];
                    const newAccount = gmailAccounts[gmailAccounts.length - 1];
                    this.state.activeTabId = newAccount.id;
                    this.loadMessages(newAccount.email);

                    // ✅ Cập nhật localStorage
                    const currentUserId = await getCurrentUserId();
                    localStorage.setItem(
                        `gmail_accounts_user_${currentUserId}`,
                        JSON.stringify(this.state.accounts)
                    );
                } catch (error) {
                    console.error("❌ Lỗi khi lấy danh sách Gmail sau xác thực:", error);
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
            this.loadAuthenticatedEmail(); // 👈 gọi lại để cập nhật gmail_email
            this.loadMessages(acc.email);
        }
    };
    closeTab = async (accountId) => {
        const currentUserId = await getCurrentUserId();
    
        // Tìm account trong state
        const acc = this.state.accounts.find(a => a.id === accountId);
        if (!acc) {
            console.warn(`⚠️ Account ID ${accountId} not found.`);
            return;
        }
    
        try {
            // Ép accountId về số nguyên để tránh lỗi truy vấn
            const numericAccountId = parseInt(accountId);
    
            if (acc.type === 'gmail') {
                await rpc("/gmail/delete_account", { account_id: numericAccountId });
            } else if (acc.type === 'outlook') {
                await rpc("/outlook/delete_account", { account_id: numericAccountId });
            }
        } catch (error) {
            console.error("❌ Error deleting account:", error);
        }
    
        // Xoá account khỏi danh sách tab (state)
        const index = this.state.accounts.findIndex(a => a.id === accountId);
        if (index !== -1) {
            this.state.accounts.splice(index, 1);
    
            // Nếu tab active vừa bị đóng → chuyển sang tab đầu
            if (this.state.activeTabId === accountId) {
                const firstAccount = this.state.accounts[0];
                this.state.activeTabId = firstAccount ? firstAccount.id : null;
                if (firstAccount) {
                    await this.loadMessages(firstAccount.email);
                } else {
                    this.state.messages = [];
                }
            }
    
            // ✅ Cập nhật lại localStorage: lọc bỏ account bị xoá
            const savedKey = `gmail_accounts_user_${currentUserId}`;
            const savedAccounts = JSON.parse(localStorage.getItem(savedKey)) || [];
            const updatedAccounts = savedAccounts.filter(acc => acc.id !== accountId);
            localStorage.setItem(savedKey, JSON.stringify(updatedAccounts));
        }
    
        // ✅ Nếu là Gmail ping đang bật → clear interval
        if (this.gmailPingIntervalId) {
            clearInterval(this.gmailPingIntervalId);
            this.gmailPingIntervalId = null;
        }
    };
    toggleCcDetail(threadMsg) {
    if (!("showCcDetail" in threadMsg)) {
        threadMsg.showCcDetail = true;
    } else {
        threadMsg.showCcDetail = !threadMsg.showCcDetail;
    }
    this.render(); // Cập nhật lại template
    }

    getCCSummary(ccString) {
        if (!ccString) return "";
        const emails = ccString.split(',').map(e => e.trim());
        if (emails.length <= 2) return emails.join(', ');
        return `${emails[0]}, ${emails[1]}, ...`;
    }

    getToSummaryPlusCC(toString, ccString, currentUserEmail) {
    const toNames = this.getDisplayNamesFromList(toString, currentUserEmail, true);  // true = allow "tôi"
    const ccNames = this.getDisplayNamesFromList(ccString, currentUserEmail, false);

    const allNames = [...toNames, ...ccNames];
    if (allNames.length === 0) return "";
    if (allNames.length <= 2) return allNames.join(", ");
    return `${allNames[0]}, ${allNames[1]}, ...`;
    }

    getToSummary(addressString, currentUserEmail) {
        if (!addressString) return "";

        const addresses = addressString.split(",").map(a => a.trim());
        const normalizedCurrent = (currentUserEmail || "").trim().toLowerCase();

        const includesMe = addresses.some(email => email.toLowerCase().includes(normalizedCurrent));
        const others = addresses.filter(email => !email.toLowerCase().includes(normalizedCurrent));

        if (includesMe) {
            if (others.length === 0) return "tôi";
            if (others.length === 1) return `tôi, ${this.extractDisplayName(others[0])}`;
            return `tôi và ${others.length} người khác`;
        } else {
            if (addresses.length === 1) return this.extractDisplayName(addresses[0]);
            return `${this.extractDisplayName(addresses[0])} và ${addresses.length - 1} người khác`;
        }
    }

    extractDisplayName(emailString) {
        const match = emailString.match(/"?(.*?)"?\s*<(.+?)>/);
        if (match) {
            return match[1] || match[2].split("@")[0];
        }
        return emailString.split("@")[0];
    }
    getDisplayNamesFromList(addressString, currentUserEmail, allowToi = true) {
    if (!addressString) return [];
    const addresses = addressString.split(",").map(a => a.trim());
    const normalizedCurrent = (currentUserEmail || "").trim().toLowerCase();

    return addresses.map(addr => {
        if (allowToi && addr.toLowerCase().includes(normalizedCurrent)) {
            return "tôi";
        }
        const match = addr.match(/"?(.*?)"?\s*<(.+?)>/);
        return match ? (match[1] || match[2].split("@")[0]) : addr.split("@")[0];
    });
    }



    showHeaderPopup(threadMsg) {
    this.state.popupMessage = threadMsg;
    this.state.showHeaderPopup = true;
    }

    closeHeaderPopup() {
        this.state.showHeaderPopup = false;
    }



    
}    

GmailInbox.template = template;
registry.category("actions").add("gmail_inbox_ui", GmailInbox);
export default GmailInbox;