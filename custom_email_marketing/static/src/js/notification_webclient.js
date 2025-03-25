/** @odoo-module **/

import { NotificationInit } from "@custom_email_marketing/js/notification_init";
import { WebClient } from "@web/webclient/webclient";

console.log("📡 Notification WebClient loaded");

// ✅ Gắn NotificationInit vào WebClient mà KHÔNG override registry
WebClient.components = {
    ...WebClient.components,
    NotificationInit,
};
