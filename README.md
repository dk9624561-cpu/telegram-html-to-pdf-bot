# 📚 Lecture HTML to 1-2 Page PDF & PDF Merger Bot

Yeh bot do kaam karta hai:
1. **HTML to 1-2 Page PDF:** Lecture summary HTML files ko clean, 2-column compact 1-2 page print PDF me convert karta hai.
2. **Multiple PDFs Merge:** Multiple PDF files ko aapas me jodkar ek single PDF banata hai.

---

## 🚀 Telegram Commands & Usage

### 1️⃣ HTML to 1-2 Page PDF:
- Bas koi bhi `.html` file bot ko send karein.
- Bot turant 2-column compact layout me 1-2 page ki PDF return karega.

### 2️⃣ PDF Merge Kaise Karein:
1. Bot ko **/merge** command bhejiye.
2. Jin-jin PDFs ko jodna hai, unhe **ek-ek karke send karein**.
3. Sabhi PDFs bhej lene ke baad **/done** bhejiye (ya "🚀 Merge Now" button dabayein).
4. Bot sabhi PDFs ko jodkar ek single combined PDF bhej dega!
5. Agar beech me cancel karna ho: **/cancel**

---

## 💻 Local Conversion (CLI)
```powershell
# Single File Convert:
python convert_local.py "path/to/summary.html"

# Batch Folder Convert:
python convert_local.py "path/to/folder"
```

---

## 🚂 Railway Deployment
Repo already Dockerfile aur railway.json ke sath configured hai:
1. GitHub repo ko Railway me connect karein.
2. Automatically build & 24/7 run hoga.
