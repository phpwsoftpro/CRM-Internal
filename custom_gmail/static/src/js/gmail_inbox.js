/** @odoo-module **/

import { Component, onMounted, useState, xml } from "@odoo/owl";
import { registry } from "@web/core/registry";

export class GmailInbox extends Component {
    setup() {
        this.state = useState({
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

        onMounted(() => {
            this.loadMessages();
            this.state.selectedAccount = this.state.accounts[0];
        });
    }

    async loadMessages() {
        this.state.messages = [
            {
                id: 1,
                email_sender: "Tony Aasen",
                email: "tony.aasen@example.com",
                subject: "World map 🌎",
                preview: "Hi Robert, I think, but I really don't remember...",
                date_received: "Feb 20",
                gmail_body: `Hi again Robert,

I think, but I really don't remember if I asked you about it earlier, but we are looking for a map solution for our webpages, where we can tag/mark all KTV Working Drone partners all around the world.

Do you know about a fairly simple solution for a taggable map like this?`,
                unread: true,
                starred: false
            },
            {
                id: 2,
                email_sender: "Hoàng Đức Tài",
                email: "taivip@gmail.com",
                subject: "Hâyyyyy",
                preview: "Hi Robert, I think, but I really don't remember...",
                date_received: "Feb 20",
                gmail_body: `Hi again Robert,

I think, but I really don't remember if I asked you about it earlier, but we are looking for a map solution for our webpages, where we can tag/mark all KTV Working Drone partners all around the world.

Do you know about a fairly simple solution for a taggable map like this?`,
                unread: true,
                starred: false
            },
        ];
        this.loadStarredState();
    }
    toggleAccounts() {
        this.state.showAccounts = !this.state.showAccounts;
    }
    toggleDropdownAccount() {
        console.log("Toggle dropdown clicked", this.state.showAccountDropdown);
        this.state.showAccountDropdown = !this.state.showAccountDropdown;
        console.log("After toggle:", this.state.showAccountDropdown);
    }

    getStatusText(status) {
        switch (status) {
            case 'expired': return 'Session expired';
            case 'signed-out': return 'Signed out';
            default: return '';
        }
    }

    getInitialColor(initial) {
        const colors = {
            'R': '#5f6368',
            'V': '#1a73e8',
            'T': '#9c27b0',
            'W': '#673ab7'
        };
        return colors[initial] || '#5f6368';
    }

    getInitialBgColor(initial) {
        const colors = {
            'R': '#e8eaed',
            'V': '#e8f0fe',
            'T': '#f3e5f5',
            'W': '#ede7f6'
        };
        return colors[initial] || '#e8eaed';
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
    toggleDropdown(ev) {
        ev.stopPropagation();
        this.state.showDropdown = !this.state.showDropdown;
        this.render();
        if (this.state.showDropdown) {
            document.addEventListener("click", this.closeDropdown);
        }
    }
    closeDropdown = (ev) => {
        if (!ev.target.closest(".dropdown-menu-caret") && !ev.target.closest(".icon-btn-option")) {
            this.state.showDropdown = false;
            this.render();
            document.removeEventListener("click", this.closeDropdown);
        }
    }
    toggleDropdownVertical() {
        this.state.showDropdownVertical = !this.state.showDropdownVertical;
    }
    selectFilter(filterType) {
        this.state.showDropdown = false;
    }
    selectFilterVertical(filterType) {
        this.state.showDropdownVertical = false;
    }
    toggleSelectAll(ev) {
        const isChecked = ev.target.checked;
        this.state.messages.forEach(msg => {
            msg.selected = isChecked;
        });
        this.render();
    }
    
    onRefresh() {
        this.loadEmails();
    }
    
    onMoreActions() {
        console.log("Show more actions menu");
    }

    prevPage() {
        if (this.state.currentPage > 1) {
            this.state.currentPage--;
            this.loadEmails();
        }
    }
    
    nextPage() {
        if (this.state.currentPage < this.state.totalPages) {
            this.state.currentPage++;
            this.loadEmails();
        }
    }
    
    
    toggleSelect(msg) {
        msg.selected = !msg.selected;
        this.render();
    }
    // action star
    toggleStar(msg) {
        msg.starred = !msg.starred;
        this.saveStarredState()
        this.render();
    }
    saveStarredState() {
        const starredEmails = this.state.messages
            .filter(msg => msg.starred)
            .map(msg => msg.id)
        localStorage.setItem("starredEmails", JSON.stringify(starredEmails));
    }
    loadStarredState() {
        const starredEmails = JSON.parse(localStorage.getItem("starredEmails")) || [];
        this.state.messages.forEach(msg => {
            msg.starred = starredEmails.includes(msg.id)
        });
    }
    onReply(ev, msg) {
        ev.stopPropagation();
        this.openComposeModal("reply", msg);
    }
    
    onReplyAll(ev, msg) {
        ev.stopPropagation();
        this.openComposeModal("replyAll", msg);
    }
    
    onForward(ev, msg) {
        ev.stopPropagation();
        this.openComposeModal("forward", msg);
    }
    showIcons(msg) {
        msg.showIcons = true;
        this.render();
    }
    
    hideIcons(msg) {
        msg.showIcons = false;
        this.render();
    }
    fillComposeForm(to, subject, body) {
        const toField = document.querySelector(".compose-input[name='to']");
        const subjectField = document.querySelector(".compose-input[name='subject']");
        const bodyEditor = this.editorInstance;
    
        if (toField) toField.value = to;
        if (subjectField) subjectField.value = subject;
        if (bodyEditor) {
            bodyEditor.setData(body);
        } else if (document.querySelector("#compose_body")) {
            document.querySelector("#compose_body").value = body;
        }
    }
    
    onSendEmail() {
        console.log("Email Content:", this.state.emailBody);
        alert("Email Sent!");
        this.state.showComposeModal = false;
    }
    loadCKEditor() {
        if (!document.getElementById("ckeditor_script")) {
            let script = document.createElement("script");
            script.id = "ckeditor_script";
            script.src = "https://cdn.ckeditor.com/ckeditor5/39.0.0/classic/ckeditor.js";
            script.onload = () => {
                console.log("CKEditor Loaded!");
            };
            document.head.appendChild(script);
        }
    }

    async initCKEditor() {
        await this.loadCKEditor();
        setTimeout(() => {
            if (window.ClassicEditor) {
                ClassicEditor.create(document.querySelector("#compose_body"))
                    .then(editor => {
                        this.editorInstance = editor;
                    })
                    .catch(error => {
                        console.error("Error loading CKEditor:", error);
                    });
            }
        }, 1000);
    }
    
    openComposeModal(mode, msg = null) {
        if (!msg) return;
        
        this.state.composeMode = mode;
        this.state.showComposeModal = true;
    
        // Set modal title based on mode
        const modalTitle = document.querySelector(".compose-modal-header h3");
        if (modalTitle) {
            switch (mode) {
                case "reply":
                    modalTitle.textContent = "Reply";
                    break;
                case "replyAll":
                    modalTitle.textContent = "Reply All";
                    break;
                case "forward":
                    modalTitle.textContent = "Forward";
                    break;
                default:
                    modalTitle.textContent = "New Message";
            }
        }
    
        setTimeout(() => {
            this.initCKEditor();
            
            // Time to wait for CKEditor to initialize
            setTimeout(() => {
                switch (mode) {
                    case "reply":
                        // Only include the sender's email
                        const replySubject = msg.subject.startsWith("Re:") ? msg.subject : `Re: ${msg.subject}`;
                        this.fillComposeForm(msg.email, replySubject, `<br><br>On ${msg.date_received}, ${msg.email_sender} <${msg.email}> wrote:<br><blockquote>${msg.gmail_body.replace(/\n/g, '<br>')}</blockquote>`);
                        break;
                    case "replyAll":
                        // In a real app, this would include all recipients
                        const replyAllSubject = msg.subject.startsWith("Re:") ? msg.subject : `Re: ${msg.subject}`;
                        this.fillComposeForm(msg.email, replyAllSubject, `<br><br>On ${msg.date_received}, ${msg.email_sender} <${msg.email}> wrote:<br><blockquote>${msg.gmail_body.replace(/\n/g, '<br>')}</blockquote>`);
                        break;
                    case "forward":
                        const fwdSubject = msg.subject.startsWith("Fwd:") ? msg.subject : `Fwd: ${msg.subject}`;
                        this.fillComposeForm("", fwdSubject, `<br><br>---------- Forwarded message ---------<br>From: ${msg.email_sender} <${msg.email}><br>Date: ${msg.date_received}<br>Subject: ${msg.subject}<br><br>${msg.gmail_body.replace(/\n/g, '<br>')}`);
                        break;
                    default:
                        this.fillComposeForm("", "", "");
                }
            }, 1200);
        }, 100);
    }
    
    onNewEmail(ev) {
        ev.stopPropagation();
        this.openComposeModal("new");
    }
}
GmailInbox.template = xml`
    <div class="gmail-root">
        <!-- Top Bar -->
        <div class="gmail-topbar">
            <div class="gmail-logo">
                <span class="gmail-logo-icon"><i class="fa fa-google"></i></span>
                <span class="gmail-logo-text">Gmail</span>
            </div>
            <div class="gmail-search">
                <input type="text" placeholder="Search mail" />
                <button><i class="fa fa-search"></i></button>
            </div>
            <div class="gmail-inbox-container">
                <div class="gmail-profile" t-on-click="() => this.toggleDropdownAccount()">
                    <span class="user-icon"><i class="fa fa-user-circle"></i></span>
                </div>
                <div t-if="state.showAccountDropdown" class="account-dropdown-container">
                    <div class="selected-account">
                        <div class="account-header">
                            <div class="email-info">
                                <div t-esc="state.selectedAccount.email" class="email-address"/>
                                <div t-if="state.selectedAccount.managed" t-esc="state.selectedAccount.managed" class="managed-by"/>
                            </div>
                            <button class="close-button" t-on-click="() => this.toggleDropdownAccount()">x</button>
                        </div>

                        <div class="account-greeting">
                            <div class="avatar-circle" t-attf-style="background-color: {{ this.getInitialBgColor(state.selectedAccount.initial) }}">
                                <span t-esc="state.selectedAccount.initial" t-attf-style="color: {{ this.getInitialColor(state.selectedAccount.initial) }}"/>
                            </div>
                            <div class="greeting-text">Hi, Robert!</div>
                        </div>

                        <button class="manage-account-btn">Manage your Google Account</button>

                        <div class="toggle-accounts" t-on-click="toggleAccounts">
                            <span t-if="state.showAccounts">Hide more accounts</span>
                            <span t-else="">Show more accounts</span>
                            <i t-if="state.showAccounts" class="fa fa-chevron-up"></i>
                            <i t-else="" class="fa fa-chevron-down"></i>
                        </div>

                        <!-- Other accounts list -->
                        <div t-if="state.showAccounts" class="accounts-list">
                            <t t-foreach="state.accounts.slice(1)" t-as="account" t-key="account.id">
                                <div class="account-item">
                                    <div class="account-info">
                                        <div class="avatar-circle small" t-attf-style="background-color: {{ this.getInitialBgColor(account.initial) }}">
                                            <span t-esc="account.initial" t-attf-style="color: {{ this.getInitialColor(account.initial) }}"/>
                                        </div>
                                        <div class="account-details">
                                            <div class="account-name" t-esc="account.name"/>
                                            <div class="account-email" t-esc="account.email"/>
                                        </div>
                                    </div>
                                    <div class="account-status" t-esc="this.getStatusText(account.status)"/>
                                </div>
                                
                                <div t-if="account.status === 'signed-out'" class="account-actions">
                                    <button class="btn-sign-in">Sign in</button>
                                    <button class="btn-remove">Remove</button>
                                </div>
                            </t>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="gmail-body">
            <!-- Left Sidebar -->
            <div class="gmail-sidebar">
                <button class="compose-btn" t-on-click="onComposeClick">
                    <span class="compose-icon">✚</span>
                    <span class="compose-text">Compose</span>
                </button>
                <ul class="gmail-menu">
                    <li class="active">Inbox</li>
                    <li>Starred</li>
                    <li>Snoozed</li>
                    <li>Sent</li>
                    <li>Drafts</li>
                    <li>More</li>
                </ul>
            </div>

            <!-- Main Content (Message List) -->
            <div class="gmail-content">
                <div class="gmail-content-header">Inbox</div>
                <table class="gmail-table">
                    <thead>
                        <tr>
                            <th class="email-checkbox">
                                <input type="checkbox" id="selectAll" t-on-click="toggleSelectAll"/>
                            </th>
                            <div class="dropdown-caret">
                                <button class="dropdown-icon" t-on-click="toggleDropdown">
                                    <i class="fa fa-caret-down"></i>
                                </button>
                                <ul class="dropdown-menu-caret" t-attf-class="{{ state.showDropdown ? 'visible' : 'hidden' }}">
                                    <li t-on-click="() => this.selectFilter('all')">All</li>
                                    <li t-on-click="() => this.selectFilter('none')">None</li>
                                    <li t-on-click="() => this.selectFilter('read')">Read</li>
                                    <li t-on-click="() => this.selectFilter('unread')">Unread</li>
                                    <li t-on-click="() => this.selectFilter('starred')">Starred</li>
                                    <li t-on-click="() => this.selectFilter('unstarred')">Unstarred</li>
                                </ul>
                            </div>
                            <div class="dropdown-vertical">
                                <button class="icon-btn-option" t-on-click="toggleDropdownVertical">
                                    <i class="fa fa-ellipsis-v"></i>
                                </button>
                                
                                <div class="dropdown-menu-vertical" t-attf-class="{{ state.showDropdownVertical ? 'visible' : 'hidden' }}">
                                    <div class="dropdown-item">
                                        <i class="fa fa-envelope-open-o"></i> Mark all as read
                                    </div>
                                    <div class="dropdown-item disabled">
                                        <em>Select messages to see more actions</em>
                                    </div>
                                </div>
                            </div>
                            <div class="email-actions">
                                <button class="icon-btn-reload" t-on-click="onRefresh" ><i class="fa fa-refresh"></i></button>
                            </div>
                            <th class="email-pagination" colspan="6">
                                <span><t t-esc="state.range_display"/></span>
                                <button class="icon-btn" t-on-click="prevPage" t-att-disabled="state.currentPage === 1">◀</button>
                                <button class="icon-btn" t-on-click="nextPage" t-att-disabled="state.currentPage === state.totalPages">▶</button>
                            </th>
                        </tr>
                    </thead>
                    <tbody>
                        <t t-foreach="state.messages" t-as="msg" t-key="msg.id">
                            <tr t-att-class="msg.unread ? 'email-row unread' : 'email-row'"
                                t-on-click="() => this.onMessageClick(msg)"
                                t-on-mouseenter="() => this.showIcons(msg)"
                                t-on-mouseleave="() => this.hideIcons(msg)">
                                
                                <td class="email-checkbox">
                                    <input type="checkbox" t-att-checked="msg.selected"
                                        t-on-click.stop="() => this.toggleSelect(msg)" />
                                </td>

                                <td class="email-star">
                                    <span t-on-click.stop="() => this.toggleStar(msg)">
                                        <t t-if="msg.starred">
                                            <i class="fa fa-star" style="color: #e8e832;"></i>
                                        </t>
                                        <t t-else="">
                                            <i class="fa fa-star-o"></i>
                                        </t>
                                    </span>
                                </td>
                                <td class="email-icon">📩</td>

                                <td class="email-from"><t t-esc="msg.email_sender"/></td>

                                <td class="email-subject">
                                    <b><t t-esc="msg.subject"/></b> - 
                                    <span class="email-preview"><t t-esc="msg.preview"/></span>
                                </td>

                                <td class="email-date"><t t-esc="msg.date_received"/></td>

                                <!-- Các icon hiển thị khi hover -->
                                <td class="email-actions">
                                    <div class="icon-group" t-attf-class="{{msg.showIcons ? 'visible' : 'hidden'}}">
                                        <span class="icon archive" title="Archive"><i class="fa fa-archive"></i></span>
                                        <span class="icon delete" title="Delete"><i class="fa fa-trash"></i></span>
                                        <span class="icon mark-read" title="Mark as Read"><i class="fa fa-envelope"></i></span>
                                        <span class="icon reply" title="Reply"><i class="fa fa-clock-o"></i></span>
                                    </div>
                                </td>
                            </tr>
                        </t>
                    </tbody>
                </table>
            </div>

            <!-- Right Pane (Message Detail) -->
            <t t-if="state.selectedMessage">
                <div class="gmail-message-detail">
                    <div class="detail-header">
                        <h2><t t-esc="state.selectedMessage.subject"/></h2>
                        <div class="detail-actions">
                            <button class="action-btn" t-on-click="(ev) => this.onReply(ev, state.selectedMessage)">
                                <span class="action-icon">↩</span> Reply
                            </button>
                            <button class="action-btn" t-on-click="(ev) => this.onReplyAll(ev, state.selectedMessage)">
                                <span class="action-icon">↩↩</span>
                                Reply All
                            </button>
                            <button class="action-btn" t-on-click="(ev) => this.onForward(ev, state.selectedMessage)">
                                <span class="action-icon">↪</span> Forward
                            </button>
                        </div>
                        <div class="detail-meta">
                            <span class="detail-from">From: <t t-esc="state.selectedMessage.email_sender"/> &lt;<t t-esc="state.selectedMessage.email"/>&gt;</span>
                            <span class="detail-date">Date: <t t-esc="state.selectedMessage.date_received"/></span>
                        </div>
                    </div>
                    <div class="detail-body">
                        <p><t t-esc="state.selectedMessage.gmail_body"/></p>
                    </div>
                </div>
            </t>
        </div>

        <!-- Compose Modal -->
        <t t-if="state.showComposeModal">
            <div class="compose-modal">
                <div class="compose-modal-content">
                    <div class="compose-modal-header">
                        <h3>New Message</h3>
                        <button class="close-btn" t-on-click="onCloseCompose">×</button>
                    </div>
                    <div class="compose-modal-body">
                        <div class="compose-field">
                            <label>To:</label>
                            <input type="text" class="compose-input to" name="to"/>
                        </div>
                        <div class="compose-field">
                            <label>Subject:</label>
                            <input type="text" class="compose-input subject" name="subject"/>
                        </div>
                        <div class="compose-field">
                            <label>Body:</label>
                            <textarea id="compose_body" class="compose-textarea"></textarea>
                        </div>
                    </div>
                    <div class="compose-modal-footer">
                        <button class="send-btn" t-on-click="onSendEmail">Send</button>
                    </div>
                </div>
            </div>
        </t>
    </div>
`;

registry.category("actions").add("gmail_inbox_ui", GmailInbox);
export default GmailInbox;