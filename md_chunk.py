import json
import re
from pathlib import Path

INPUT_FOLDER = "tds_pages_md"
OUTPUT_FILE = "md_chunks.jsonl"

def clean_text(text):
    # Replace multiple whitespace/newlines with single space, strip leading/trailing
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_image_urls(md_text):
    # Match markdown image syntax ![alt](url)
    pattern = r'!\[[^\]]*\]\(([^)]+)\)'
    return re.findall(pattern, md_text)

def main():
    folder = Path(INPUT_FOLDER)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as out_file:
        for md_file in sorted(folder.glob("*.md")):
            raw_text = md_file.read_text(encoding='utf-8')
            cleaned_text = clean_text(raw_text)
            if not cleaned_text:
                continue

            image_urls = extract_image_urls(raw_text)

            chunk = {
                "text": cleaned_text,
                "metadata": {
                    "filename": md_file.name,
                    "filepath": str(md_file),
                    "images": image_urls,
                }
            }
            out_file.write(json.dumps(chunk, ensure_ascii=False) + "\n")

if __name__ == "__main__":
    main()
