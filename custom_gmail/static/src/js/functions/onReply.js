export function onReply(ev, selectedMessage) {
    ev.stopPropagation();

    const message = selectedMessage.thread_id
        ? selectedMessage : "";

    const originalContent = message.body || '';
    const quoted = `
        <div class="reply-quote" style="margin-top:20px; padding-top:10px; border-top:1px solid #ccc;">
            <p>On ${message.date}, "${message.author}" wrote:</p>
            <blockquote>${originalContent}</blockquote>
        </div>
    `;

    this.openComposeModal("reply", {
        ...message,
        body: '', // ✅ để nội dung chính trống
        quote: quoted // bạn có thể chèn quote vào editor khi mở modal
    });
}
