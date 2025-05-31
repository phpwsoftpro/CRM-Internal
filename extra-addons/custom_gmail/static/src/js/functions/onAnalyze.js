//** @odoo-module **/

import { rpc } from "@web/core/network/rpc";

export async function onAnalyze(ev, msg) {
    const body = msg?.body || "";
    const body_html = msg?.body_html || body;
    const email_from = msg?.sender || "Unknown Sender";
    const subject = msg?.subject || "No Subject";

    if (!body) {
        console.warn("⚠️ Không có nội dung email để phân tích.");
        return;
    }

    const final_prompt = `
        This is the content of the email:
        ---
        ${body}
        ---

        Please analyze the email above and provide a brief summary, clearly stating the main request or action.

        Translate to English.
    `;

    console.log("📨 Gửi nội dung cho DeepSeek:", body);




    try {
        const result = await rpc("/deepseek/analyze_gmail_body", {
            body: final_prompt,
            subject,
            email_from,
            body_html,

        });


        console.log("🧠 AI Trả về:", result.ai_summary || result.message);
    } catch (error) {
        console.error("❌ Lỗi khi gọi DeepSeek:", error);
    }
}
