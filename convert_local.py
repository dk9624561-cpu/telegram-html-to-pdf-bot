import os
import sys
import glob
from converter import convert_html_to_pdf

def convert_single_file(html_path: str):
    if not os.path.exists(html_path):
        print(f"❌ File not found: {html_path}")
        return
    
    base_name = os.path.splitext(html_path)[0]
    out_pdf = base_name + ".pdf"
    print(f"🔄 Converting: {os.path.basename(html_path)}...")
    success, pages, title = convert_html_to_pdf(html_path, out_pdf)
    if success:
        print(f"✅ Created: {out_pdf} ({pages} pages, Title: '{title}')")
    else:
        print(f"❌ Failed to convert: {html_path}")

def convert_directory(folder_path: str):
    html_files = glob.glob(os.path.join(folder_path, "*.html")) + glob.glob(os.path.join(folder_path, "*.htm"))
    if not html_files:
        print(f"No HTML files found in: {folder_path}")
        return
    print(f"Found {len(html_files)} HTML files in {folder_path}...")
    for f in html_files:
        convert_single_file(f)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        target = sys.argv[1]
        if os.path.isdir(target):
            convert_directory(target)
        else:
            convert_single_file(target)
    else:
        # Default test
        sample = r"c:\Users\Welcome\Downloads\Telegram Desktop\Economics Class 15 Summary.html"
        print(f"No file path provided. Testing with sample file:\n{sample}\n")
        convert_single_file(sample)
