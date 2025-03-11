/** @odoo-module **/

export function onReply(ev, msg) {
    ev.stopPropagation();
    this.openComposeModal("reply", msg);
}