odoo.define('custom_email_marketing.notification_project_tab', function (require) {
    "use strict";

    const { patch } = require('web.utils');
    const MessagingMenu = require('mail.MessagingMenu');

    patch(MessagingMenu.prototype, 'custom_project_tab', {
        setup() {
            this._super(...arguments);

            this.projectNotifications = [];
            this.loadProjectNotifications();
        },

        async loadProjectNotifications() {
            this.projectNotifications = await this.rpc({
                route: '/project/notifications',
            });
            this.render(); // re-render menu
        },

        renderTabs() {
            const $tabs = this._super(...arguments);
            $tabs.append(`<li class="o_mail_tab_project">Project</li>`);
            return $tabs;
        },

        renderContent() {
            const $content = this._super(...arguments);

            const $projectTab = $('<div class="o_mail_tab_content_project d-none">');
            this.projectNotifications.forEach(msg => {
                const html = `<div class="o_mail_notification_item">
                    <div><strong>${msg.subject}</strong></div>
                    <div>${msg.body}</div>
                    <div style="font-size: 11px;">${msg.date} - ${msg.author}</div>
                </div>`;
                $projectTab.append(html);
            });
            $content.append($projectTab);
            return $content;
        },

        _onClickTab(ev) {
            this._super(...arguments);
            const tab = $(ev.currentTarget).text().trim();
            $('.o_mail_tab_content_project').toggleClass('d-none', tab !== 'Project');
        }
    });
});
