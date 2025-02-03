odoo.define('your_module.DiscussCustomButton', function (require) {
    "use strict";

    const DiscussSidebar = require('mail.DiscussSidebar');
    const { patch } = require('web.utils');

    patch(DiscussSidebar.prototype, 'your_module.DiscussCustomButton', {
        on_custom_button_click() {
            this.do_notify('Custom Button', 'You clicked the custom button!');
        },

        _renderSidebar() {
            // Gọi hàm gốc
            this._super(...arguments);

            // Thêm nút mới
            const customButton = $('<button>', {
                text: 'Custom Button',
                class: 'btn btn-primary',
                click: () => this.on_custom_button_click(),
            });
            this.$('.o_mail_discuss_sidebar').append(customButton);
        },
    });
});
