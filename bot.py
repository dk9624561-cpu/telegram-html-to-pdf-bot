import os
import sys
import json
import logging
import telebot

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass
from converter import convert_html_to_pdf

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger("HtmlToPdfBot")

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.json")
TEMP_DIR = os.path.join(os.path.dirname(__file__), "temp")
os.makedirs(TEMP_DIR, exist_ok=True)

def get_bot_token():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if token:
        return token
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                token = data.get("bot_token", "").strip()
                if token and token != "YOUR_TELEGRAM_BOT_TOKEN_HERE":
                    return token
        except Exception as e:
            logger.error(f"Error reading config.json: {e}")
    return None

bot_token = get_bot_token()

if not bot_token:
    print("=" * 60)
    print("⚠️  TELEGRAM BOT TOKEN NOT CONFIGURED!")
    print("Please open config.json and enter your Telegram Bot Token")
    print("obtained from @BotFather in Telegram.")
    print("=" * 60)
    user_token = input("Or paste your Bot Token here now (press Enter to exit): ").strip()
    if user_token:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump({"bot_token": user_token}, f, indent=4)
        bot_token = user_token
    else:
        sys.exit(1)

bot = telebot.TeleBot(bot_token)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        "👋 *Namaste!*\n\n"
        "Main aapka *Lecture Summary HTML to PDF Bot* hoon.\n\n"
        "📌 *Kaise use karein?*\n"
        "1. Mujhe koi bhi Lecture Summary `.html` file bhejiye.\n"
        "2. Main turant usko ek ultra-clean, stylish *1 ya 2 page ke A4 PDF* me convert karke bhej dunga.\n\n"
        "✨ *Features:*\n"
        "• Modern 2-Column Compact Layout\n"
        "• Crisp Hindi Devanagari typography\n"
        "• Topic badges aur timestamps highlight\n"
        "• Exactly 1-2 pages me print-ready fit\n\n"
        "Bas abhi koi bhi `.html` file send kijiye! 🚀"
    )
    bot.reply_to(message, welcome_text, parse_mode="Markdown")

@bot.message_handler(content_types=['document'])
def handle_document(message):
    file_name = message.document.file_name or "summary.html"
    if not (file_name.lower().endswith(".html") or file_name.lower().endswith(".htm")):
        bot.reply_to(
            message,
            "⚠️ Kripya valid `.html` ya `.htm` file bhejiye jo lecture summary ho.",
            parse_mode="Markdown"
        )
        return

    status_msg = bot.reply_to(
        message,
        "📥 *File prapt hui!* HTML process ho rahi hai aur 2-column PDF banayi ja rahi hai... ⏳",
        parse_mode="Markdown"
    )

    input_file_path = None
    output_pdf_path = None

    try:
        # Download the file
        file_info = bot.get_file(message.document.file_id)
        downloaded_bytes = bot.download_file(file_info.file_path)

        base_clean_name = os.path.splitext(file_name)[0]
        input_file_path = os.path.join(TEMP_DIR, f"{message.chat.id}_{message.message_id}_{file_name}")
        output_pdf_path = os.path.join(TEMP_DIR, f"{message.chat.id}_{message.message_id}_{base_clean_name}.pdf")

        with open(input_file_path, "wb") as f:
            f.write(downloaded_bytes)

        # Convert to 2-page PDF
        success, pages, title = convert_html_to_pdf(input_file_path, output_pdf_path)

        if not success or not os.path.exists(output_pdf_path):
            bot.edit_message_text(
                "❌ PDF convert karne me koi samasya aayi. Kripya check karein ki HTML file sahi hai.",
                chat_id=message.chat.id,
                message_id=status_msg.message_id
            )
            return

        # Send the PDF document
        caption = (
            f"✅ *{title}*\n"
            f"📄 *Total Pages:* {pages} Page(s)\n"
            f"⚡ Clean 2-Column High-Yield Print Layout"
        )

        with open(output_pdf_path, "rb") as pdf_file:
            bot.send_document(
                chat_id=message.chat.id,
                document=pdf_file,
                visible_file_name=f"{base_clean_name}_Summary.pdf",
                caption=caption,
                parse_mode="Markdown",
                reply_to_message_id=message.message_id
            )

        # Delete the temporary status message
        try:
            bot.delete_message(chat_id=message.chat.id, message_id=status_msg.message_id)
        except Exception:
            pass

    except Exception as e:
        logger.error(f"Error handling document: {e}", exc_info=True)
        bot.edit_message_text(
            f"❌ Error: {str(e)[:200]}",
            chat_id=message.chat.id,
            message_id=status_msg.message_id
        )

    finally:
        # Cleanup temporary files
        if input_file_path and os.path.exists(input_file_path):
            try:
                os.remove(input_file_path)
            except Exception:
                pass
        if output_pdf_path and os.path.exists(output_pdf_path):
            try:
                os.remove(output_pdf_path)
            except Exception:
                pass

if __name__ == "__main__":
    print(f"🤖 Bot is starting up... Connected to Telegram.")
    try:
        bot_info = bot.get_me()
        print(f"✅ Bot Online: @{bot_info.username} ({bot_info.first_name})")
        print("Waiting for .html files from users...")
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except Exception as e:
        print(f"❌ Could not connect bot: {e}")
        print("Please verify your bot token in config.json")
