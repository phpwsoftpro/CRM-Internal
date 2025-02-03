odoo.define('your_module.CustomDiscussButton', function (require) {
    "use strict";

    // Kiểm tra các module phụ thuộc
    const DiscussSidebar = require('mail.DiscussSidebar');
    const { patch } = require('web.utils');

    if (!DiscussSidebar || !patch) {
        console.error("Missing dependencies: mail.DiscussSidebar or web.utils");
        return;
    }

    // Thêm hành động tùy chỉnh
    patch(DiscussSidebar.prototype, 'your_module.CustomDiscussButton', {
        on_custom_button_click() {
            this.do_notify('Custom Button', 'You clicked the custom button!');
        },
    });
});
