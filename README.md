# 📚 Lecture HTML to 1-2 Page PDF Telegram Bot

Yeh bot aapki lecture summary HTML files (jaise `Economics Class 15 Summary.html`) ko ek ultra-clean, stylish, 2-column compact **1 ya 2 page ke print-ready PDF** me convert karta hai.

---

## 🚀 Quick Setup & Kaise Use Karein

### Step 1: Telegram Bot Token Daalein
1. Telegram me `@BotFather` ke paas jayein aur `/newbot` likhkar apna ek bot banayein (ya apna existing bot token use karein).
2. [config.json](file:///C:/Users/Welcome/.gemini/antigravity-ide/scratch/telegram-html-to-pdf-bot/config.json) file open karein aur apna token paste karein:
   ```json
   {
       "bot_token": "YOUR_ACTUAL_BOT_TOKEN"
   }
   ```

### Step 2: Bot Start Karein
- Simply [run_bot.bat](file:///C:/Users/Welcome/.gemini/antigravity-ide/scratch/telegram-html-to-pdf-bot/run_bot.bat) par double-click karein, ya command prompt me run karein:
  ```powershell
  python bot.py
  ```

### Step 3: Telegram par File Bhejiye
1. Apne Telegram bot par `/start` bhejiye.
2. Koi bhi `.html` summary file bot ko send karein.
3. Bot turant 2 second me aapko **1 ya 2 page ki clean PDF** return kar dega!

---

## 💻 Local Conversion (Bina Bot ke bhi convert karein)

Aap kisi bhi HTML file ya poore folder ko direct convert kar sakte hain:

```powershell
# Single File Convert:
python convert_local.py "C:\Users\Welcome\Downloads\Telegram Desktop\Economics Class 15 Summary.html"

# Poora Folder Ek Saath Convert:
python convert_local.py "C:\Users\Welcome\Downloads\Telegram Desktop"
```

---

## 🎨 Key Features & Styling:
- **2-Column Layout:** Saara lecture content bina cut kiye compact format me aayega.
- **Strictly 1-2 Pages:** Long summaries 2 pages me aur short summaries 1 page me fit hoti hain.
- **Hindi Typography:** Nirmala UI & Devanagari fonts se saaf Hindi rendering bina kisi matra bug ke.
- **Smart Highlighting:**
  - Topic headers & timestamps red badges me
  - Sub-points & definitions blue badges me
  - Dark slate header banner with notes badge
