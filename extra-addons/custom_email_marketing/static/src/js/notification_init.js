/** @odoo-module **/

import { Component, onMounted } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

console.log("📡 Notification INIT loaded");

function setupNotificationBus(bus, uid, dbname) {
    const channel = [dbname, "notification_channel", uid];
    bus.addChannel(channel);
    console.log("📡 Added channel:", channel);

    bus.on("notification", null, (notificationsList) => {
        console.log("📨 bus.on('notification') triggered:", notificationsList);
        for (const notif of notificationsList) {
            const [db, chan, user_id] = notif.channel;
            if (chan === "notification_channel" && user_id === uid) {
                const msg = notif.message.message;

                window.latestNotifications = window.latestNotifications || [];
                window.latestNotifications.unshift(msg);

                const dot = document.getElementById("notify_dot");
                if (dot) dot.style.display = "block";

                console.log("🔔 New Notification:", msg);
            }
        }
    });
}


export class NotificationInit extends Component {
    setup() {
        const bus = useService("bus");
        const user = useService("user");
        const session = useService("session");

        onMounted(() => {
            const uid = user.userId;
            const dbname = session.db;
        
            setupNotificationBus(bus, uid, dbname);
        
            // 👇 Gọi lấy thông báo lưu từ server
            odoo.rpc({
                route: "/notification/list",
                params: {},
            }).then((result) => {
                console.log("📋 Lịch sử thông báo từ server:", result);
        
                window.latestNotifications = result;
        
                const dot = document.getElementById("notify_dot");
                if (dot && result.length > 0) dot.style.display = "block";
            });
        });
        
    }
}

NotificationInit.template = "custom_email_marketing.NotificationInit";

