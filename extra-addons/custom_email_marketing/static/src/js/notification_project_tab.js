/** @odoo-module **/

import { MessagingMenu } from "@mail/components/messaging_menu/messaging_menu";
import { onWillStart, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { patch } from "@web/core/utils/patch";

patch(MessagingMenu.prototype, {
    setup() {
        super.setup();
        this.rpc = useService("rpc");
        this.projectState = useState({ messages: [] });

        onWillStart(async () => {
            this.projectState.messages = await this.rpc("/project/notifications");
        });
    },

    get tabs() {
        return [
            ...super.tabs,
            {
                id: "project",
                name: "Project",
                hasUnseen: false,
            },
        ];
    },

    get currentTabMessages() {
        if (this.currentTab === "project") {
            return this.projectState.messages;
        }
        return super.currentTabMessages;
    },

    // Ghi đè để render đúng nội dung cho tab "project"
    _renderTabContent() {
        if (this.currentTab === "project") {
            return this.projectState.messages.map((msg) => ({
                id: msg.id,
                author: msg.author,
                body: msg.body,
                subject: msg.subject,
                date: msg.date,
            }));
        }
        return super._renderTabContent();
    },
});
