/** @odoo-module **/

import { rpc } from "@web/core/network/rpc";

export async function onAnalyze(ev, msg) {
    const body = msg?.body || "";
    if (!body) {
        console.warn("⚠️ Không có nội dung email để phân tích.");
        return;
    }

    const final_prompt = `
        📩 Đây là nội dung email:
        ---
        ${body}
        ---

        🎯 Hãy phân tích email trên và trả về một bản tóm tắt ngắn gọn (mặc định tiếng Việt),
        nêu rõ yêu cầu hoặc hành động chính).
    `;


    console.log("📨 Gửi nội dung cho DeepSeek:", body);

    try {
        const result = await rpc("/deepseek/analyze_gmail_body", { body });  // ✅ dùng rpc
        console.log("🧠 AI Trả về:", result.ai_summary || result.message);
    } catch (error) {
        console.error("❌ Lỗi khi gọi DeepSeek:", error);
    }
}
