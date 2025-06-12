import json
import re
from pathlib import Path
from bs4 import BeautifulSoup

INPUT = "discourse_threadsV3.json"
OUTPUT = "dis_chunks.jsonl"

def clean_text(html):
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(separator=" ").strip()
    return re.sub(r'\s+', ' ', text)

def extract_images(html):
    soup = BeautifulSoup(html, "html.parser")
    images = []
    for img in soup.find_all("img"):
        src = img.get("src")
        alt = img.get("alt", "")
        if src:
            images.append({"alt": alt, "src": src})
    return images

def main():
    with open(INPUT, "r") as f:
        topics = json.load(f)

    with open(OUTPUT, "w") as out:
        for topic in topics:
            topic_id = topic.get("topic_id")
            topic_title = topic.get("topic_title", "")
            posts = topic.get("posts", [])

            for post in posts:
                html = post.get("cooked", "")
                cleaned = clean_text(html)
                if not cleaned:
                    continue

                chunk = {
                    "text": cleaned,
                    "metadata": {
                        "topic_id": topic_id,
                        "url": f"https://discourse.onlinedegree.iitm.ac.in{post.get('post_url', '')}",
                        "author": post.get("display_username", post.get("username")),
                        "created_at": post.get("created_at"),
                        "topic_title": topic_title,
                        "images": extract_images(html),
                    }
                }
                out.write(json.dumps(chunk, ensure_ascii=False) + "\n")

if __name__ == "__main__":
    main()
