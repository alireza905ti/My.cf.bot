import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# توکن به صورت امن از سرویس رندر دریافت خواهد شد
import os
TELEGRAM_BOT_TOKEN = os.getenv('BOT_TOKEN', 'YOUR_TELEGRAM_BOT_TOKEN')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام! برای ثبت رکورد DNS کلادفلر، اطلاعات را به شکل زیر بفرستید:\n\n"
        "`API_KEY|ZONE_ID|DOMAIN_NAME|IP`\n\n"
        "مثال:\n"
        "`c2548...|a1b2c3...|sub.example.com|1.2.3.4`",
        parse_mode='Markdown'
    )

async def handle_setup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    try:
        api_token, zone_id, domain, ip = [x.strip() for x in text.split('|')]
        await update.message.reply_text("⏳ در حال تنظیم رکورد DNS در کلادفلر...")
        
        url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records"
        headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "type": "A",
            "name": domain,
            "content": ip,
            "ttl": 1,
            "proxied": True
        }
        
        response = requests.post(url, json=payload, headers=headers)
        res_data = response.json()
        
        if res_data.get("success"):
            await update.message.reply_text(
                f"✅ **با موفقیت انجام شد!**\n\n"
                f"🔹 دامنه: `{domain}`\n"
                f"🔹 آی‌پی: `{ip}`\n"
                f"🔹 ابر کلادفلر: روشن (Proxied)\n\n"
                f"حالا می‌توانید کانفیگ مربوط به این دامنه را استفاده کنید.",
                parse_mode='Markdown'
            )
        else:
            errors = res_data.get("errors", [{}])[0].get("message", "خطای نامشخص")
            await update.message.reply_text(f"❌ **خطا در کلادفلر:**\n{errors}")

    except ValueError:
        await update.message.reply_text("⚠️ فرمت ورودی اشتباه است.\nالگو: `API_KEY|ZONE_ID|DOMAIN_NAME|IP`", parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"❌ خطا: {str(e)}")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_setup))
    app.run_polling()
