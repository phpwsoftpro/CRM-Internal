/** @odoo-module **/

export function onForward(ev, msg) {
    ev.stopPropagation();
    this.openComposeModal("forward", msg);
}