/** @odoo-module **/

odoo.define('custom_email_marketing.notification_bell', function (require) {
    "use strict";

    const WebSocketBus = require('@web/core/websocket_bus/websocket_bus').WebSocketBus;
    const store = require('custom_email_marketing.notification_store');

    const wsBus = new WebSocketBus();
    wsBus.addEventListener("custom_notify", ({ detail }) => {
        store.notifications.unshift(detail.message);
        store.unreadCount++;
        store.updateUnreadCountDisplay();
    });
    wsBus.start();
});
