/** @odoo-module **/

export function onSendEmail() {
    console.log("Email Content:", this.state.emailBody);
    alert("Email Sent!");
    this.state.showComposeModal = false;
}