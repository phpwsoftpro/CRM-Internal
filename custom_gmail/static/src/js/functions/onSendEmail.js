/** @odoo-module **/

export function onSendEmail() {
    const composeData = this.state.composeData || {};
   
    const thread_id = composeData.thread_id || null; 
    const message_id = composeData.message_id || null; 
    
    const to = document.querySelector('.compose-input.to').value;
    const subject = document.querySelector('.compose-input.subject').value;
    let body = window.editorInstance ? window.editorInstance.getData() : '';

    body = body.replace(/<table/g, '<table border="1" cellspacing="0" cellpadding="4" style="border-collapse:collapse;"');
    const splitIndex = body.indexOf('<div class="reply-quote">');
    const cleanBody = splitIndex !== -1 ? body.slice(0, splitIndex) : body;

    if (!to) {
        alert("Vui lòng nhập địa chỉ email.");
        return;
    }

    const emailData = {
        to: to,
        subject: subject,
        body_html: cleanBody,
        thread_id: thread_id,  
        message_id: message_id 
    };
    console.log("📤 Email sending data:", emailData); 
    // Gửi email với dữ liệu đã kiểm tra
    fetch('/api/send_email', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
        },
        body: JSON.stringify(emailData)
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
        alert("Có lỗi xảy ra khi gửi email.");
        console.log(err);
    });
}
