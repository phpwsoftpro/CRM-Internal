/** @odoo-module **/

import { xml } from "@odoo/owl";

export default xml`
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
                    <i class="fa fa-pencil"></i> <span>Soạn thư</span>
                </button>
                <ul class="gmail-menu">
                    <li><i class="fa fa-inbox"></i> <span>Hộp thư đến</span></li>
                    <li><i class="fa fa-star-o"></i> <span>Có gắn dấu sao</span></li>
                    <li><i class="fa fa-clock-o"></i> <span>Đã tạm ẩn</span></li>
                    <li><i class="fa fa-paper-plane"></i> <span>Đã gửi</span></li>
                    <li><i class="fa fa-file"></i> <span>Thư nháp</span></li>
                    <li><i class="fa fa-chevron-down"></i> <span>Hiện thêm</span></li>
                </ul>
            </div>
            <div class="gmail-header">
                <!-- Filters & Actions -->
                <div class="header-actions">
                    <div class="email-checkbox-all"> <input type="checkbox" id="selectAll" t-on-click="toggleSelectAll" style="cursor: pointer;"/></div>
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

                    <button class="icon-btn-reload" t-on-click="onRefresh">
                        <i class="fa fa-refresh"></i>
                    </button>

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

               <!-- Tabs -->
                <div class="gmail-tabs">
                    <!-- Các tab account đang có -->
                    <t t-foreach="state.accounts" t-as="acc" t-key="acc.id">
                        <div class="tab" t-att-class="acc.id === state.activeTabId ? 'tab active' : 'tab'" 
                            t-att-data-email="acc.email"
                            t-on-click="() => this.switchTab(acc.id)">
                            <i class="fa fa-inbox"></i> 
                            <t t-esc="acc.email"/>
                            <i class="fa fa-times close-tab"
                            title="Đóng"
                            style="margin-left: 8px; cursor: pointer;"
                            t-on-click.stop="() => this.closeTab(acc.id)"></i>
                        </div>
                    </t>

                    <!-- Nút login Gmail -->
                    <div class="tab login-tab" t-on-click="() => this.addGmailAccount()">
                        <img src="/custom_gmail/static/src/img/gmail_1.svg" alt="Gmail" class="icon-svg"/>
                    </div>

                    <!-- Nút login Outlook -->
                    <div class="tab login-tab" t-on-click="() => this.addOutlookAccount()">
                        <img src="/custom_gmail/static/src/img/outlook.svg" alt="Outlook" class="icon-svg"/>
                    </div>
                </div>
                    <div class="tab-content">
                            <div class="gmail-content" >
                                <div class="content-container">
                                    <div class="email-list">
                                        <t t-set="activeAccount" t-value="state.accounts.find(acc => acc.id === state.activeTabId)"/>
                                        <t t-set="activeEmail" t-value="activeAccount ? activeAccount.email : ''"/>
                                        <t t-set="activeMessages" t-value="(state.messagesByEmail[activeEmail]) or []"/>

                                        <t t-foreach="activeMessages" t-as="msg" t-key="msg.id">
                                            <div class="email-item"
                                                t-att-class="msg.unread ? 'email-row unread' : 'email-row'"
                                                t-on-click="() => this.onMessageClick(msg)">

                                                <!-- Checkbox -->
                                                <div class="email-checkbox">
                                                    <input type="checkbox" t-att-checked="msg.selected" t-on-click.stop="() => this.toggleSelect(msg)" />
                                                </div>

                                                <!-- Email Info -->
                                                <div class="email-info">
                                                    <div class="email-header">
                                                        <div class="email-from"><t t-esc="msg.sender"/></div>
                                                        <div class="email-date"><t t-esc="msg.date_received"/></div>
                                                    </div>
                                                    <div class="email-content">
                                                        <div class="email-subject"><b><t t-esc="msg.subject"/></b></div>
                                                        <div class="email-preview"><t t-esc="msg.preview"/></div>
                                                    </div>
                                                </div>
                                                <!-- Star & Actions -->
                                                <div class="email-star-actions">
                                                    <div class="email-star" t-on-click.stop="() => this.toggleStar(msg)">
                                                        <t t-if="msg.starred">
                                                            <i class="fa fa-star" style="color: #e8e832;"></i>
                                                        </t>
                                                        <t t-else="">
                                                            <i class="fa fa-star-o"></i>
                                                        </t>
                                                    </div>
                                                </div>
                                            </div>
                                        </t>
                                    </div>

                                    <div class="email-detail">
                                        <t t-if="state.selectedMessage">
                                            <div class="detail-header">
                                                <h1 class="detail-subject">
                                                    <t t-esc="state.selectedMessage.subject"/>
                                                </h1>
                                            </div>
                                            <div class="thread-container">
                                                <t t-foreach="state.currentThread" t-as="threadMsg" t-key="threadMsg.id">
                                                    <div class="thread-message" 
                                                        t-att-class="{'current-message': threadMsg.id === state.selectedMessage.id, 'collapsed': threadMsg.collapsed}">
                                                        <div class="message-header">
                                                            <div class="sender-info">
                                                                <img class="sender-avatar" t-att-src="threadMsg.avatar || '/path/to/default-avatar.png'" alt="avatar" />
                                                                <div class="sender-details">
                                                                    <div class="sender-line">
                                                                        <strong class="sender-name"><t t-esc="threadMsg.sender"/></strong>
                                                                    </div>
                                                                    <div class="recipient-line">
                                                                        đến tôi <span class="dropdown-arrow"><i class="fa fa-caret-down"></i></span>
                                                                    </div>
                                                                </div>
                                                            </div>
                                                            <div class="header-actions">
                                                                <span class="email-date">
                                                                    <t t-esc="threadMsg.date_received"/>
                                                                </span>
                                                                <button class="icon-btn star-btn" aria-label="Đánh dấu sao" t-on-click.stop="() => this.toggleStar(threadMsg)">
                                                                    <i t-att-class="threadMsg.starred ? 'fa fa-star' : 'fa fa-star-o'"></i>
                                                                </button>
                                                                <button class="icon-btn reply" aria-label="Phản hồi" t-on-click="(ev) => this.onReply(ev, threadMsg)">
                                                                    <i class="fa fa-reply"></i>
                                                                </button>
                                                                <button class="icon-btn more-btn" aria-label="Thêm tùy chọn">
                                                                    <i class="fa fa-ellipsis-v"></i>
                                                                </button>
                                                            </div>
                                                        </div>

                                                        <div class="message-content" t-att-style="threadMsg.collapsed ? 'display: none;' : 'display: block;'">
                                                            <t t-esc="threadMsg.body"/>
                                                        </div>
                                                        
                                                        <div class="email-attachments" t-if="threadMsg.attachments and threadMsg.attachments.length">
                                                            <h3 class="attachments-title">Tệp đính kèm</h3>
                                                            <div class="attachments-grid">
                                                                <div t-foreach="threadMsg.attachments" t-as="attachment" t-key="attachment.id || attachment_index" class="attachment-item">

                                                                    <!-- 🖼️ Preview ảnh -->
                                                                    <t t-if="attachment.mimetype and attachment.mimetype.startsWith('image/')">
                                                                        <a t-att-href="attachment.url" target="_blank">
                                                                            <img t-att-src="attachment.url"
                                                                                style="max-width: 150px; max-height: 150px; border-radius: 6px; border: 1px solid #ccc;" />
                                                                        </a>
                                                                        <div class="attachment-name"><t t-esc="attachment.name"/></div>
                                                                    </t>

                                                                    <!-- 📄 Preview PDF -->
                                                                    <t t-elif="attachment.mimetype === 'application/pdf'">
                                                                        <div class="attachment-box" t-on-click="(ev) => this.openFilePreview(ev)" t-att-data-url="attachment.url">
                                                                            <iframe t-att-src="attachment.url" style="width: 100%; height: 150px; border: none;"></iframe>
                                                                            <div class="attachment-name"><t t-esc="attachment.name"/></div>
                                                                            <!-- Nút tải xuống -->
                                                                            <a t-att-href="'/web/content/' + attachment.id + '?download=true'"
                                                                            t-att-download="attachment.name"
                                                                            t-on-click="(ev) => { ev.stopPropagation(); }"
                                                                            class="attachment-download"
                                                                            title="Tải xuống">
                                                                                <i class="fa fa-download"></i>
                                                                            </a>
                                                                        </div>
                                                                    </t>
                                                                    <!-- 📎 Các file khác -->
                                                                <t t-else="">
                                                                        <div class="attachment-box">
                                                                            <!-- Icon động theo loại file -->
                                                                            <div class="attachment-icon">
                                                                                <i t-att-class="'fa ' + (
                                                                                    attachment.mimetype.includes('word') ? 'fa-file-word-o' :
                                                                                    attachment.mimetype.includes('excel') || attachment.name.endsWith('.csv') || attachment.name.endsWith('.xlsx') || attachment.name.endsWith('.xls') ? 'fa-file-excel-o' :
                                                                                    attachment.mimetype.includes('powerpoint') ? 'fa-file-powerpoint-o' :
                                                                                    attachment.mimetype.includes('zip') || attachment.name.endsWith('.zip') ? 'fa-file-archive-o' :
                                                                                    'fa-file-o')"></i>
                                                                            </div>

                                                                            <!-- Tên file -->
                                                                            <div class="attachment-name">
                                                                                <span t-esc="attachment.name" />
                                                                            </div>

                                                                            <!-- Nút tải xuống -->
                                                                            <div class="attachment-actions">
                                                                                <a t-att-href="'/web/content/' + attachment.id + '?download=true'"
                                                                                    t-att-download="attachment.name"
                                                                                    t-on-click="(ev) => { ev.stopPropagation(); }"
                                                                                    class="attachment-download"
                                                                                    title="Tải xuống">
                                                                                        <i class="fa fa-download"></i>
                                                                                </a>
                                                                            </div>
                                                                        </div>
                                                                    </t>
                                                                </div>
                                                            </div>
                                                        <div id="filePreviewModal" class="modal">
                                                                <div class="modal-content">
                                                                <span class="close" t-attf-onclick="this.parentElement.parentElement.style.display='none'">×</span>
                                                                    <iframe id="filePreviewFrame" style="width:100%; height:80vh; border:none;"></iframe>
                                                                </div>
                                                            </div>
                                                        </div>
                                                    </div>
                                                </t>
                                            </div>
                                            <div class="detail-actions">
                                                <button class="action-btn reply"  t-on-click="(ev) => this.onReply(ev, threadMsg)" style="margin-left: 60px;">
                                                    <i class="fa fa-reply"></i> Trả lời
                                                </button>
                                                <button class="action-btn reply-all" t-on-click="(ev) => this.onReplyAll(ev, state.selectedMessage)">
                                                    <i class="fa fa-reply-all"></i> Trả lời tất cả
                                                </button>
                                                <button class="action-btn forward" t-on-click="(ev) => this.onForward(ev, state.selectedMessage)">
                                                    <i class="fa fa-share"></i> Chuyển tiếp
                                                </button>
                                            </div>
                                        </t>
                                        <t t-if="!state.selectedMessage">
                                            <div class="no-message">
                                                <div class="no-message-icon">
                                                    <i class="fa fa-envelope-o"></i>
                                                </div>
                                                <p>Không có cuộc trò chuyện nào được chọn.</p>
                                                <p>Hãy chọn một email để xem chi tiết.</p>
                                            </div>
                                        </t>
                                                    </div>
                                                </div>
                                            </div>
                                    </div>

                            </div>
         </div>
        <!-- Compose Modal -->
        <t t-if="state.showComposeModal">
            <div class="compose-modal">
                <div class="compose-modal-header">
                    <h3>Thư mới</h3>
                    <div class="header-actions">
                        <button style="font-size: 30px;">−</button>
                        <button style="font-size: 30px;">↗</button>
                        <button t-on-click="onCloseCompose" style="font-size: 30px;">×</button>
                    </div>
                </div>
                <div class="compose-modal-body">
                    <div class="compose-field">
                        <label>Đến</label>
                        <input type="text" class="compose-input to" name="to"/>
                        <div class="cc-bcc">Cc Bcc</div>
                    </div>
                    <div class="compose-field">
                        <label>Tiêu đề</label>
                        <input type="text" class="compose-input subject" name="subject"/>
                    </div>
                    <div class="compose-textarea-container">
                        <textarea id="compose_body" class="compose-textarea"></textarea>
                    </div>
                </div>
                <div class="compose-modal-footer">
                    <div class="left-buttons">
                        <button class="send-btn" t-on-click="onSendEmail">Gửi</button>
                    </div>
                    <button class="trash-icon" t-on-click="onCloseCompose">
                        <i class="fa fa-trash"></i>
                    </button>
                </div>
            </div>
        </t>
    </div>
`;
