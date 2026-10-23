import os
import sys
import time
import json
import logging
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import fitz

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

# In-memory storage for merge sessions: chat_id -> dict
USER_MERGE_SESSIONS = {}

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
    print("Please set TELEGRAM_BOT_TOKEN environment variable or update config.json")
    print("=" * 60)
    sys.exit(1)

bot = telebot.TeleBot(bot_token)

def make_merge_keyboard():
    markup = InlineKeyboardMarkup()
    btn_done = InlineKeyboardButton("🚀 Merge Now (/done)", callback_data="action_done")
    btn_cancel = InlineKeyboardButton("❌ Cancel (/cancel)", callback_data="action_cancel")
    markup.row(btn_done, btn_cancel)
    return markup

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        "👋 *Namaste!*\n\n"
        "Main aapka *All-in-One Lecture HTML & PDF Bot* hoon.\n\n"
        "✨ *Kya-kya kar sakta hoon:*\n\n"
        "1️⃣ *HTML to 1-2 Page PDF:*\n"
        "• Koi bhi Lecture Summary `.html` file bhejiye.\n"
        "• Main turant usko clean 2-column compact 1-2 page PDF me convert kar dunga.\n\n"
        "2️⃣ *Multiple PDFs Merge Karna:*\n"
        "• Command bhejiye: **/merge**\n"
        "• Fir apni saari PDF files ek-ek karke send kijiye.\n"
        "• Sabhi bhej lene ke baad command bhejiye: **/done**\n"
        "• Main sabhi PDFs ko jodkar ek single PDF bana dunga!\n\n"
        "🚀 *Commands:*\n"
        "• `/merge` - PDF merge mode shuru karein\n"
        "• `/done` - Sabhi bheji gayi PDFs ko merge karein\n"
        "• `/cancel` - Merge mode cancel karein\n"
        "• `/help` - Help message dekhein"
    )
    bot.reply_to(message, welcome_text, parse_mode="Markdown")

@bot.message_handler(commands=['merge', 'startmerge'])
def start_merge_mode(message):
    chat_id = message.chat.id
    # Clean up previous session if any
    if chat_id in USER_MERGE_SESSIONS:
        cleanup_session(chat_id)

    USER_MERGE_SESSIONS[chat_id] = {
        "files": [],
        "names": [],
        "total_pages": 0
    }

    text = (
        "📥 *PDF Merge Mode ON ho gaya hai!*\n\n"
        "Ab aap jin PDF files ko merge karna chahte hain, unhe **ek-ek karke send kijiye**.\n\n"
        "Jab aap saari PDFs bhej lein, tab **/done** send karein ya neeche diye gaye button par click karein.\n\n"
        "❌ Cancel karne ke liye: **/cancel**"
    )
    bot.reply_to(message, text, parse_mode="Markdown", reply_markup=make_merge_keyboard())

@bot.message_handler(commands=['cancel'])
def cancel_merge_mode(message):
    chat_id = message.chat.id
    if chat_id in USER_MERGE_SESSIONS:
        count = len(USER_MERGE_SESSIONS[chat_id]["files"])
        cleanup_session(chat_id)
        bot.reply_to(message, f"❌ *PDF Merge Mode cancel kar diya gaya.* ({count} files cleared).", parse_mode="Markdown")
    else:
        bot.reply_to(message, "Koi active merge session nahi hai. Start karne ke liye `/merge` bhejiye.", parse_mode="Markdown")

@bot.message_handler(commands=['done', 'mergenow'])
def perform_merge(message):
    chat_id = message.chat.id
    if chat_id not in USER_MERGE_SESSIONS or not USER_MERGE_SESSIONS[chat_id]["files"]:
        bot.reply_to(
            message,
            "⚠️ Merge karne ke liye koi PDF nahi mili!\n\nPehle `/merge` likhiye, fir kam se kam 2 PDFs send kijiye.",
            parse_mode="Markdown"
        )
        return

    session = USER_MERGE_SESSIONS[chat_id]
    files = session["files"]
    names = session["names"]

    if len(files) < 2:
        bot.reply_to(
            message,
            f"⚠️ Merge karne ke liye kam se kam 2 PDF files chahiye. Abhi sirf {len(files)} file prapt hui hai.\n\nAgli PDF send kijiye ya cancel karne ke liye `/cancel` likhein.",
            parse_mode="Markdown",
            reply_markup=make_merge_keyboard()
        )
        return

    status_msg = bot.reply_to(
        message,
        f"⏳ *Merging {len(files)} PDF files...* Kripya intazar karein.",
        parse_mode="Markdown"
    )

    merged_output_path = os.path.join(TEMP_DIR, f"{chat_id}_Merged_{int(time.time())}.pdf")

    try:
        merged_doc = fitz.open()
        for f_path in files:
            sub_doc = fitz.open(f_path)
            merged_doc.insert_pdf(sub_doc)
            sub_doc.close()

        merged_doc.save(merged_output_path)
        total_pages = len(merged_doc)
        merged_doc.close()

        file_list_str = "\n".join([f"• `{name}`" for name in names[:10]])
        if len(names) > 10:
            file_list_str += f"\n• ...aur {len(names) - 10} aur files"

        caption = (
            f"✅ *All PDFs Merged Successfully!*\n\n"
            f"📁 *Combined Files:* {len(files)}\n"
            f"📄 *Total Pages:* {total_pages}\n\n"
            f"📋 *Files list:*\n{file_list_str}"
        )

        with open(merged_output_path, "rb") as out_f:
            bot.send_document(
                chat_id=chat_id,
                document=out_f,
                visible_file_name=f"Merged_{len(files)}_Documents.pdf",
                caption=caption,
                parse_mode="Markdown",
                reply_to_message_id=message.message_id
            )

        try:
            bot.delete_message(chat_id=chat_id, message_id=status_msg.message_id)
        except Exception:
            pass

    except Exception as e:
        logger.error(f"Error merging PDFs: {e}", exc_info=True)
        bot.edit_message_text(
            f"❌ PDF merge karne me error aayi: {str(e)[:200]}",
            chat_id=chat_id,
            message_id=status_msg.message_id
        )
    finally:
        cleanup_session(chat_id)
        if os.path.exists(merged_output_path):
            try:
                os.remove(merged_output_path)
            except Exception:
                pass

@bot.callback_query_handler(func=lambda call: call.data in ["action_done", "action_cancel"])
def handle_callback(call):
    chat_id = call.message.chat.id
    bot.answer_callback_query(call.id)
    if call.data == "action_done":
        perform_merge(call.message)
    elif call.data == "action_cancel":
        cancel_merge_mode(call.message)

def cleanup_session(chat_id):
    if chat_id in USER_MERGE_SESSIONS:
        session = USER_MERGE_SESSIONS[chat_id]
        for f in session.get("files", []):
            if os.path.exists(f):
                try:
                    os.remove(f)
                except Exception:
                    pass
        del USER_MERGE_SESSIONS[chat_id]

@bot.message_handler(content_types=['document'])
def handle_document(message):
    chat_id = message.chat.id
    file_name = message.document.file_name or "document"
    file_name_lower = file_name.lower()

    # Case 1: User is sending PDF files
    if file_name_lower.endswith(".pdf"):
        if chat_id in USER_MERGE_SESSIONS:
            try:
                file_info = bot.get_file(message.document.file_id)
                downloaded_bytes = bot.download_file(file_info.file_path)

                file_idx = len(USER_MERGE_SESSIONS[chat_id]["files"]) + 1
                pdf_path = os.path.join(TEMP_DIR, f"{chat_id}_merge_{file_idx}_{file_name}")

                with open(pdf_path, "wb") as f:
                    f.write(downloaded_bytes)

                # Check validity with fitz
                doc = fitz.open(pdf_path)
                p_count = len(doc)
                doc.close()

                USER_MERGE_SESSIONS[chat_id]["files"].append(pdf_path)
                USER_MERGE_SESSIONS[chat_id]["names"].append(file_name)
                USER_MERGE_SESSIONS[chat_id]["total_pages"] += p_count

                total_files = len(USER_MERGE_SESSIONS[chat_id]["files"])
                total_p = USER_MERGE_SESSIONS[chat_id]["total_pages"]

                reply_txt = (
                    f"📄 *File #{total_files} Add ho gayi!*\n"
                    f"• *Name:* `{file_name}`\n"
                    f"• *Pages:* {p_count} (Total Pages: {total_p})\n\n"
                    f"Agli PDF bhejiye ya sabhi ko jodne ke liye **/done** bhejiye."
                )
                bot.reply_to(message, reply_txt, parse_mode="Markdown", reply_markup=make_merge_keyboard())
            except Exception as e:
                logger.error(f"Error processing PDF in merge mode: {e}")
                bot.reply_to(message, f"❌ Is PDF ko add karne me samasya aayi: {e}")
        else:
            # Inform user how to merge
            bot.reply_to(
                message,
                "📄 *Aapne PDF file bheji hai.*\n\n"
                "Agar aap multiple PDF files ko jodkar 1 PDF banana chahte hain, toh pehle **/merge** command send kijiye!",
                parse_mode="Markdown"
            )
        return

    # Case 2: User is sending HTML files (HTML to 1-2 page PDF)
    if not (file_name_lower.endswith(".html") or file_name_lower.endswith(".htm")):
        bot.reply_to(
            message,
            "⚠️ Kripya `.html` (Lecture Summary) ya `.pdf` (Merge ke liye) file bhejiye.",
            parse_mode="Markdown"
        )
        return

    status_msg = bot.reply_to(
        message,
        "📥 *HTML File prapt hui!* Clean 2-column PDF banayi ja rahi hai... ⏳",
        parse_mode="Markdown"
    )

    input_file_path = None
    output_pdf_path = None

    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded_bytes = bot.download_file(file_info.file_path)

        base_clean_name = os.path.splitext(file_name)[0]
        input_file_path = os.path.join(TEMP_DIR, f"{chat_id}_{message.message_id}_{file_name}")
        output_pdf_path = os.path.join(TEMP_DIR, f"{chat_id}_{message.message_id}_{base_clean_name}.pdf")

        with open(input_file_path, "wb") as f:
            f.write(downloaded_bytes)

        # Convert to 1-2 page PDF
        success, pages, title = convert_html_to_pdf(input_file_path, output_pdf_path)

        if not success or not os.path.exists(output_pdf_path):
            bot.edit_message_text(
                "❌ PDF convert karne me koi samasya aayi. Kripya check karein ki HTML file valid hai.",
                chat_id=chat_id,
                message_id=status_msg.message_id
            )
            return

        caption = (
            f"✅ *{title}*\n"
            f"📄 *Total Pages:* {pages} Page(s)\n"
            f"⚡ Clean 2-Column High-Yield Print Layout"
        )

        with open(output_pdf_path, "rb") as pdf_file:
            bot.send_document(
                chat_id=chat_id,
                document=pdf_file,
                visible_file_name=f"{base_clean_name}_Summary.pdf",
                caption=caption,
                parse_mode="Markdown",
                reply_to_message_id=message.message_id
            )

        try:
            bot.delete_message(chat_id=chat_id, message_id=status_msg.message_id)
        except Exception:
            pass

    except Exception as e:
        logger.error(f"Error handling HTML document: {e}", exc_info=True)
        bot.edit_message_text(
            f"❌ Error: {str(e)[:200]}",
            chat_id=chat_id,
            message_id=status_msg.message_id
        )
    finally:
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
        print("Ready for HTML-to-PDF and PDF-Merge tasks...")
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except Exception as e:
        print(f"❌ Could not connect bot: {e}")
        print("Please verify your bot token in config.json")
