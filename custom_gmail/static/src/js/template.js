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
                                        <span class="icon reply" title="Reply"><i class="fa fa-reply"></i></span>
                                    </div>
                                </td>
                            </tr>
                        </t>
                    </tbody>
                </table>
            </div>

            <!-- Right Pane (Message Detail) -->
            <t t-if="state.selectedMessage">
                <div class="gmail-message-detail thread-view">
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
                            <span class="detail-to">To: <t t-esc="state.selectedAccount.email"/></span> <!-- Thêm To field -->
                            <span class="detail-date">Date: <t t-esc="state.selectedMessage.date_received"/></span>
                        </div>
                    </div>
                    <div class="detail-body">
                        <div class="message-content">
                            <p><t t-esc="state.selectedMessage.gmail_body"/></p>
                        </div>
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