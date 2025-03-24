/** @odoo-module **/

import { busService } from "@bus/services/bus_service";
import { Component, onMounted } from "@odoo/owl";
import { registry } from "@web/core/registry";

if (!registry.category("services").contains("bus_service")) {
    registry.category("services").add("bus_service", busService);
}

function setupNotificationBus(env) {
    const bus = env.services.bus_service;
    bus.addChannel("notification_channel");

    bus.on("notification", null, (notificationsList) => {
        for (const notif of notificationsList) {
            if (notif.type === "notification" && notif.payload && notif.payload.message) {
                const dot = document.getElementById("notify_dot");
                if (dot) dot.style.display = "block";
                console.log("🔔 Realtime from bus:", notif.payload.message);
                document.dispatchEvent(new CustomEvent("bus_notification", { detail: notif.payload }));
            }
        }
    });
}

export const NotificationInit = class extends Component {
    setup() {
        onMounted(() => {
            setupNotificationBus(this.env);
        });
    }
};

NotificationInit.template = "<div></div>";
registry.category("main_components").add("NotificationInit", {
    Component: NotificationInit,
});