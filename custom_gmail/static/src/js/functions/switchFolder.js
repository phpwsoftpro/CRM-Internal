/** @odoo-module **/
export function switchFolder(folder) {
    this.state.activeFolder = folder;
    const acc = this.state.accounts.find(a => a.id === this.state.activeTabId);
    if (!acc) return;
    this.loadMessages(acc.email);
  }
  