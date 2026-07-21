import os
import requests
import uuid
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.environ.get("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام! 👋\n"
        "برای ساخت کانفیگ سریع، فقط کافیه **API Key کلادفلر** خودت رو اینجا بفرستی:"
    )

async def handle_api_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    api_token = update.message.text.strip()
    
    # پیام اولیه
    status_msg = await update.message.reply_text("⚡ در حال بررسی کلادفلر و دریافت اطلاعات...")

    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }

    try:
        # ۱. دریافت اطلاعات دامنه از کلادفلر
        res = requests.get("https://api.cloudflare.com/client/v4/zones", headers=headers, timeout=10)
        data = res.json()

        if res.status_code == 200 and data.get("success") and len(data["result"]) > 0:
            # برداشتن اولین دامنه فعال ثبت‌شده
            domain = data["result"][0]["name"]
            user_uuid = str(uuid.uuid4()) # ساخت شناسه اختصاصی کانفیگ

            # ۲. ساخت لینک کانفیگ vless با پروتکل gRPC برای حداکثر سرعت
            vless_config = (
                f"vless://{user_uuid}@{domain}:443?"
                f"encryption=none&security=tls&type=grpc&serviceName=grpc&sni={domain}#CF-Fast-gRPC"
            )

            response_text = (
                f"✅ **اتصال با موفقیت انجام شد!**\n\n"
                f"🌐 **دامنه شناسایی‌شده:** `{domain}`\n"
                f"⚡ **پروتکل:** VLESS + gRPC (TLS)\n\n"
                f"👇 **لینک کانفیگ اختصاصی شما:**\n"
                f"`{vless_config}`\n\n"
                f"💡 *نکته:* هر زمان آی‌پی تمیز کلادفلر پیدا کردی، می‌تونی توی نرم‌افزارت (مثل v2rayN یا Hiddify) بخش Address/IP رو روی اون آی‌پی جدید بگذاری تا سرعت چند برابر بشه."
            )
            await status_msg.edit_text(response_text, parse_mode="Markdown")

        else:
            await status_msg.edit_text("❌ کلید کلادفلر معتبر نیست یا هیچ دامنه‌ای روی این اکانت وجود نداره. لطفاً مجدداً بررسی کن.")

    except Exception as e:
        await status_msg.edit_text(f"❌ خطایی در ارتباط رخ داد: {str(e)}")

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_api_key))
    app.run_polling()
