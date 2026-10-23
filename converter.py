import os
import subprocess
import tempfile
import fitz
from bs4 import BeautifulSoup

def get_browser_path():
    env_bin = os.environ.get("CHROME_BIN")
    if env_bin and os.path.exists(env_bin):
        return env_bin
        
    candidates = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser",
        "/usr/bin/google-chrome",
        "/usr/bin/google-chrome-stable"
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return "chromium"

BROWSER_PATH = get_browser_path()

def transform_html_for_print(raw_html: str, font_size_pt: float = 8.1) -> str:
    soup = BeautifulSoup(raw_html, "html.parser")
    
    # 1. Extract Title
    h1 = soup.find("h1")
    if h1:
        title = h1.get_text(strip=True)
    else:
        title_tag = soup.find("title")
        title = title_tag.get_text(strip=True) if title_tag else "Class Summary"
        
    # 2. Extract Date
    date_text = ""
    for p in soup.find_all("p"):
        p_str = p.get_text(strip=True)
        if "Date:" in p_str:
            date_text = p_str.replace("Date:", "").strip()
            p.decompose()
            break

    # 3. Extract Tiger Header / Subtitle
    header_tag = soup.find(class_="tiger-header")
    subtitle = header_tag.get_text(strip=True) if header_tag else "⚡ QUICK REVISION SUMMARY ⚡"
    
    # Clean old headers
    if header_tag:
        header_tag.decompose()
    if h1:
        h1.decompose()
    for h2 in soup.find_all("h2"):
        if "Lecture Summary" in h2.get_text():
            h2.decompose()
            
    # Locate container or body
    container = soup.find(class_="container")
    content_root = container if container else soup.find("body")
    if not content_root:
        content_root = soup

    # Remove empty tags
    for tag in content_root.find_all(["p", "div", "span"]):
        if not tag.get_text(strip=True) and not tag.find("img"):
            tag.decompose()

    # Identify and style section headers
    for p in content_root.find_all("p"):
        p_text = p.get_text(strip=True)
        if any(marker in p_text for marker in ["PM", "AM", "---", "–", "TOPICS FOR THE NEXT CLASS"]):
            strong_tag = p.find(["strong", "b"])
            if strong_tag or len(p_text) < 110:
                p['class'] = p.get('class', []) + ['section-header']
                
    # Style list items & bold sub-headers
    for li in content_root.find_all("li"):
        style = li.get("style", "")
        if "bold" in style.lower():
            li['class'] = li.get('class', []) + ['sub-header-item']
        else:
            first_strong = li.find(["strong", "b"])
            if first_strong and li.text.strip().startswith(first_strong.text.strip()):
                first_strong['class'] = first_strong.get('class', []) + ['term-title']

    body_html = "".join(str(c) for c in content_root.contents)
    date_badge = f'<span class="badge">📅 {date_text}</span>' if date_text and date_text != "N/A" else '<span class="badge">📖 Quick Notes</span>'

    final_html = f"""<!DOCTYPE html>
<html lang="hi">
<head>
<meta charset="utf-8">
<title>{title}</title>
<style>
@page {{
    size: A4 portrait;
    margin: 6mm 8mm 6mm 8mm;
}}

* {{
    box-sizing: border-box;
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
}}

body {{
    font-family: 'Nirmala UI', 'Segoe UI', 'Noto Sans Devanagari', -apple-system, sans-serif;
    color: #1e293b;
    background: #ffffff;
    margin: 0;
    padding: 0;
    font-size: {font_size_pt}pt;
    line-height: 1.32;
}}

/* Top Banner Header */
.header-banner {{
    background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
    color: #ffffff;
    border-radius: 5px;
    padding: 5px 10px;
    margin-bottom: 6px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-left: 4px solid #dc2626;
}}

.header-tag {{
    font-size: 6.8pt;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    color: #f87171;
    font-weight: 700;
}}

.header-title {{
    font-size: 11.5pt;
    font-weight: 800;
    color: #ffffff;
    margin: 1px 0 0 0;
    line-height: 1.15;
}}

.header-badges {{
    display: flex;
    gap: 5px;
    align-items: center;
}}

.badge {{
    background: rgba(255, 255, 255, 0.12);
    border: 1px solid rgba(255, 255, 255, 0.25);
    padding: 2px 7px;
    border-radius: 10px;
    font-size: 7.2pt;
    font-weight: 600;
}}

.badge-accent {{
    background: #dc2626;
    border: 1px solid #b91c1c;
    color: #ffffff;
}}

/* 2-Column Content Flow */
.columns-flow {{
    column-count: 2;
    column-gap: 12px;
    column-rule: 1px solid #e2e8f0;
}}

/* Section Header (like topics with timestamp) */
.section-header, p.section-header {{
    background: #f8fafc;
    border-left: 3px solid #dc2626;
    border-top: 1px solid #e2e8f0;
    border-right: 1px solid #e2e8f0;
    border-bottom: 1px solid #e2e8f0;
    padding: 2.5px 6px;
    margin: 5px 0 2.5px 0;
    border-radius: 3px;
    font-size: {font_size_pt + 0.3}pt;
    font-weight: 700;
    color: #991b1b;
    break-after: avoid;
    break-inside: avoid;
}}

.section-header strong, .section-header b {{
    color: #991b1b;
    font-weight: 700;
}}

/* Lists and Items */
ul {{
    margin: 0 0 3px 0;
    padding-left: 12px;
    list-style-type: square;
}}

li {{
    margin-bottom: 2px;
    color: #334155;
    text-align: justify;
    break-inside: avoid;
}}

li strong, li b {{
    color: #991b1b;
    font-weight: 700;
}}

/* Subheader inside list items */
li.sub-header-item {{
    list-style-type: none;
    margin-left: -12px;
    margin-top: 4px;
    margin-bottom: 2px;
    break-after: avoid;
    break-inside: avoid;
}}

li.sub-header-item strong, li.sub-header-item b {{
    display: inline-block;
    color: #1e40af;
    background: #eff6ff;
    border-left: 2.5px solid #3b82f6;
    padding: 1px 4px;
    border-radius: 0 3px 3px 0;
    font-size: {font_size_pt}pt;
    font-weight: 700;
}}

.term-title {{
    color: #1e40af !important;
}}

p {{
    margin: 0 0 2.5px 0;
    break-inside: avoid;
}}
</style>
</head>
<body>
    <div class="header-banner">
        <div>
            <div class="header-tag">{subtitle}</div>
            <div class="header-title">{title}</div>
        </div>
        <div class="header-badges">
            {date_badge}
            <span class="badge badge-accent">High-Yield Notes</span>
        </div>
    </div>

    <div class="columns-flow">
        {body_html}
    </div>
</body>
</html>
"""
    return final_html, title

def convert_html_to_pdf(input_html_path: str, output_pdf_path: str) -> tuple[bool, int, str]:
    """
    Converts an input HTML file into a clean, compact 1-2 page PDF.
    Returns: (success: bool, page_count: int, title: str)
    """
    browser_bin = get_browser_path()
        
    with open(input_html_path, "r", encoding="utf-8", errors="ignore") as f:
        raw_html = f.read()
        
    font_size = 8.1
    best_page_count = 999
    title = "Summary"
    
    for attempt in range(2):
        styled_html, title = transform_html_for_print(raw_html, font_size_pt=font_size)
        
        temp_html_path = output_pdf_path + f".temp_{attempt}.html"
        with open(temp_html_path, "w", encoding="utf-8") as f:
            f.write(styled_html)
            
        cmd = [
            browser_bin,
            "--headless",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--no-pdf-header-footer",
            f"--print-to-pdf={output_pdf_path}",
            temp_html_path
        ]
        
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        if os.path.exists(temp_html_path):
            try:
                os.remove(temp_html_path)
            except Exception:
                pass
                
        if os.path.exists(output_pdf_path):
            try:
                doc = fitz.open(output_pdf_path)
                page_count = len(doc)
                doc.close()
                best_page_count = page_count
                if page_count <= 2:
                    break
                else:
                    font_size = 7.7
            except Exception:
                best_page_count = 1
                break
                
    success = os.path.exists(output_pdf_path)
    return success, best_page_count, title
