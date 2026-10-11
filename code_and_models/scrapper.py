from playwright.sync_api import sync_playwright
import json
import time
import re

SUBREDDITS = ["chennai", "kuttichevuru"]
collected = []

def clean_body(text: str) -> str:
    text = re.sub(r"https?://\S+", "", text)
    text = re.sub(r"^>.*$", "", text, flags=re.MULTILINE)
    return " ".join(text.split())

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    )
    page = context.new_page()

    for sub in SUBREDDITS:
        print(f"\n[Browser] Navigating to r/{sub}/comments...")
        # Old reddit HTML is lightweight and clean to parse
        page.goto(f"https://old.reddit.com/r/{sub}/comments/", wait_until="domcontentloaded")
        
        for page_num in range(5):  # Paginate through 5 pages per sub
            comments = page.query_selector_all("div.entry div.usertext-body div.md")
            for c in comments:
                txt = clean_body(c.inner_text().strip())
                words = txt.split()
                if 2 <= len(words) <= 12 and not any(b in txt.lower() for b in ["[deleted]", "[removed]"]):
                    collected.append(txt)
            
            # Click the 'next' button on old.reddit
            next_btn = page.query_selector("span.next-button a")
            if next_btn:
                print(f" -> Page {page_num + 1} scraped. Total collected: {len(collected)}")
                next_btn.click()
                page.wait_for_load_state("domcontentloaded")
                time.sleep(2.0)
            else:
                break

    browser.close()

unique_dataset = list(dict.fromkeys(collected))
print(f"\nCollected {len(unique_dataset):,} samples via headless browser.")

with open("scraped_reddit_browser.json", "w", encoding="utf-8") as f:
    json.dump(unique_dataset, f, ensure_ascii=False, indent=2)