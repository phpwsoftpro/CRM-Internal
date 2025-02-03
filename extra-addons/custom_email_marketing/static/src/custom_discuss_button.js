odoo.define('your_module.CustomDiscussButton', function (require) {
    "use strict";

    const DiscussSidebar = require('mail.DiscussSidebar');
    const { patch } = require('web.utils');

    patch(DiscussSidebar.prototype, 'your_module.CustomDiscussButton', {
        on_custom_button_click() {
            this.do_notify('Custom Button', 'You clicked the custom button!');
        },
    });
});
