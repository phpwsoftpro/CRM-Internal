/** @odoo-module **/

export function saveStarredState() {
    const starredEmails = this.state.messages
        .filter(msg => msg.starred)
        .map(msg => msg.id);
    localStorage.setItem("starredEmails", JSON.stringify(starredEmails));
}

export function loadStarredState() {
    const starredEmails = JSON.parse(localStorage.getItem("starredEmails")) || [];
    this.state.messages.forEach(msg => {
        msg.starred = starredEmails.includes(msg.id);
    });
}