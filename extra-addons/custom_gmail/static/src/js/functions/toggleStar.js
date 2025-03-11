/** @odoo-module **/

export function toggleStar(msg) {
    msg.starred = !msg.starred;
    this.saveStarredState();
    this.render();
}