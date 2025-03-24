/** @odoo-module **/

import { NotificationBell } from "@custom_email_marketing/js/notification_widget";
import { registry } from "@web/core/registry";
import { WebClient } from "@web/webclient/webclient";

WebClient.components = {
    ...WebClient.components,
    NotificationBell,
};

registry.category("main_components").add("web_client", {
    Component: WebClient,
});