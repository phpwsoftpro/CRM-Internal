/** @odoo-module **/

export function onSendEmail() {
    const to = document.querySelector('.compose-input.to').value;
    const subject = document.querySelector('.compose-input.subject').value;
    let body = window.editorInstance ? window.editorInstance.getData() : '';

    // Fix bảng không có border
    body = body.replace(/<table/g, '<table border="1" cellspacing="0" cellpadding="4" style="border-collapse:collapse;"');

    if (!to) {
        alert("Vui lòng nhập địa chỉ email.");
        return;
    }

    fetch('/api/send_email', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest', // Odoo expects this
        },
        body: JSON.stringify({
            to: to,
            subject: subject,
            body_html: body,
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            alert("Đã gửi email thành công!");
            this.state.showComposeModal = false;

            if (window.editorInstance) {
                window.editorInstance.destroy();
                window.editorInstance = null;
            }

            document.querySelector('.compose-input.to').value = '';
            document.querySelector('.compose-input.subject').value = '';
        } else {
            throw new Error(data.message || 'Gửi mail thất bại');
        }
    })
    .catch(err => {
        console.error("Lỗi khi gửi email:", err);
        alert("Có lỗi xảy ra khi gửi email.");
    });
}
