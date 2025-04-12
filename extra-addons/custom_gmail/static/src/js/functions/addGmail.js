/** @odoo-module **/

export async function addGmailAccount() {
    try {
        const response = await fetch('/web/dataset/call_kw/mail.message/action_redirect_gmail_auth', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest',
            },
            body: JSON.stringify({
                params: {
                    model: 'mail.message',
                    method: 'action_redirect_gmail_auth',
                    args: [],
                    kwargs: {},
                },
            }),
        });

        const data = await response.json();
        if (data?.result?.type === 'ir.actions.act_url') {
            const popup = window.open(data.result.url, '_blank');
            
            // Kiểm tra khi popup đã hoàn tất
            const checkEmail = setInterval(async () => {
                const res = await fetch('/gmail/current_user_info', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest',
                    },
                    body: JSON.stringify({
                        jsonrpc: "2.0",
                        method: "call",
                        params: {},
                    }),
                });

                const json = await res.json();

                if (json.status === 'success') {
                    clearInterval(checkEmail);
                    addGmailTab(json.email, true);  // 👉 true để tự động chuyển sang tab mới
                }
            }, 3000);

            // Kiểm tra nếu cửa sổ popup bị đóng
            popup.onbeforeunload = function () {
                clearInterval(checkEmail);
            };
        }
    } catch (error) {
        console.error('Lỗi khi thêm Gmail:', error);
    }
}

// 👉 Hàm tạo tab mới Gmail
function addGmailTab(email, focus = false) {
    const tabContainer = document.querySelector('.gmail-tabs');
    if (!tabContainer) return;

    const existingTab = tabContainer.querySelector(`.tab[data-email="${email}"]`);
    if (existingTab) {
        if (focus) activateTab(existingTab);
        return;
    }

    const tab = document.createElement('div');
    tab.className = 'tab';
    tab.setAttribute('data-email', email);
    tab.innerHTML = `<i class="fa fa-inbox"></i> ${email}`;
    tab.onclick = () => activateTab(tab);

    const plusTab = tabContainer.querySelector('.add-tab');
    if (plusTab) {
        tabContainer.insertBefore(tab, plusTab);
    } else {
        tabContainer.appendChild(tab);
    }

    if (focus) activateTab(tab);
}

// 👉 Hàm chuyển tab và reset nội dung
function activateTab(tabElement) {
    document.querySelectorAll('.gmail-tabs .tab').forEach(tab => {
        tab.classList.remove('active');
    });
    tabElement.classList.add('active');

    const inboxContainer = document.getElementById('gmail-inbox-container');
    if (inboxContainer) inboxContainer.innerHTML = '';  // ✅ Clear nội dung
}

// Export ra global để dùng trong HTML
window.addGmailAccount = addGmailAccount;
