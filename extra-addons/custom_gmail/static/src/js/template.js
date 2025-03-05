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
                <button class="compose-btn">
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

            <!-- Main Content (Message List) -->
            <div class="gmail-content">
                <div class="gmail-content-header">
                    <!-- Dropdown Filters -->
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

                    <!-- Actions -->
                    <div class="email-actions">
                        <button class="icon-btn-reload" t-on-click="onRefresh"><i class="fa fa-refresh"></i></button>

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

                    <!-- Pagination -->
                    <div class="email-pagination">
                        <span><t t-esc="state.range_display"/></span>
                        <button class="icon-btn" t-on-click="prevPage" t-att-disabled="state.currentPage === 1">◀</button>
                        <button class="icon-btn" t-on-click="nextPage" t-att-disabled="state.currentPage === state.totalPages">▶</button>
                    </div>
                </div>
                <div class="content-container">
                    <!-- Email List -->
                    <div class="email-list">
                        <t t-foreach="state.messages" t-as="msg" t-key="msg.id">
                            <div class="email-item"
                                t-att-class="msg.unread ? 'email-row unread' : 'email-row'"
                                t-on-click="() => this.onMessageClick(msg)"
                                t-on-mouseenter="() => this.showIcons(msg)"
                                t-on-mouseleave="() => this.hideIcons(msg)">

                                <!-- Checkbox -->
                                <div class="email-checkbox">
                                    <input type="checkbox" t-att-checked="msg.selected" t-on-click.stop="() => this.toggleSelect(msg)" />
                                </div>

                                <!-- Email Info -->
                                <div class="email-info">
                                    <div class="email-header">
                                        <div class="email-from"><t t-esc="msg.email_sender"/></div>
                                        <div class="email-actions" t-attf-class="{{msg.showIcons ? 'visible' : 'hidden'}}">
                                            <span class="icon archive" title="Archive"><i class="fa fa-archive"></i></span>
                                            <span class="icon delete" title="Delete"><i class="fa fa-trash"></i></span>
                                            <span class="icon mark-read" title="Mark as Read"><i class="fa fa-envelope"></i></span>
                                            <span class="icon reply" title="Reply"><i class="fa fa-clock-o"></i></span>
                                        </div>
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
                    <div class="gmail-message-detail thread-view">
                        <t t-if="state.selectedMessage">
                            <div class="detail-header">
                                <h2><t t-esc="state.selectedMessage.subject"/></h2>
                                <div class="detail-actions">
                                    <button class="action-btn" t-on-click="(ev) => this.onReply(ev, state.selectedMessage)">
                                        <span class="action-icon">↩</span> Reply
                                    </button>
                                    <button class="action-btn" t-on-click="(ev) => this.onReplyAll(ev, state.selectedMessage)">
                                        <span class="action-icon">↩↩</span> Reply All
                                    </button>
                                    <button class="action-btn" t-on-click="(ev) => this.onForward(ev, state.selectedMessage)">
                                        <span class="action-icon">↪</span> Forward
                                    </button>
                                </div>
                                <div class="detail-meta">
                                    <span class="detail-from">From: <t t-esc="state.selectedMessage.email_sender"/> &lt;<t t-esc="state.selectedMessage.email"/>&gt;</span>
                                    <span class="detail-to">To: <t t-esc="state.selectedAccount.email"/></span>
                                    <span class="detail-date">Date: <t t-esc="state.selectedMessage.date_received"/></span>
                                </div>
                            </div>
                            <div class="detail-body">
                                <div class="message-content">
                                    <p><t t-esc="state.selectedMessage.gmail_body"/></p>
                                </div>
                            </div>
                        </t>
                        
                        <!-- Nếu không có email nào được chọn, hiển thị thông báo -->
                        <t t-if="!state.selectedMessage">
                            <div class="no-message">
                                <p>Không có cuộc trò chuyện nào được chọn.</p>
                            </div>
                        </t>
                    </div>
                </div>
            </div>
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