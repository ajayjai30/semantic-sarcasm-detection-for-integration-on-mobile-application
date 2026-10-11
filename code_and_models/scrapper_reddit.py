from curl_cffi import requests
import json
import time
import re
from urllib.parse import urlparse

# ============================================================
# CONFIGURATION & AUTHENTICATION
# ============================================================
REDDIT_SESSION_COOKIE = "eyJhbGciOiJSUzI1NiIsImtpZCI6IlNIQTI1NjpsVFdYNlFVUEloWktaRG1rR0pVd1gvdWNFK01BSjBYRE12RU1kNzVxTXQ4IiwidHlwIjoiSldUIn0.eyJzdWIiOiJ0Ml8xNnVuZndlc2xtIiwiZXhwIjoxODA2Mzk2MDIyLjA2MTAxOCwiaWF0IjoxNzkwNzU3NjIyLjA2MTAxOCwianRpIjoib2tRTTNOUmNNQjVGMWJfc2lvNUZZck1HQ1dGN3d3IiwiYXQiOjEsImNpZCI6ImNvb2tpZSIsImxjYSI6MTcyMzg5NDIxMDIwMCwic2NwIjoiZUp3QUFnRDlfMXRkQXdBQkZRQzUiLCJmbG8iOjMsImFtciI6WyJzc28iXX0.fNJ3kRzE1IJII3nCscY0M-FdrzzBiMWlKOOha5bIXHoTxTeURZslCfDozdnlu-Y989rQl6LX68UL7DHQV98CjNVdpItNt3sFS0y4Ub5aG7SvdJtbnMQII0CAEqRHLHw1iAyGAjr_on9lR-aRvkqmYZIAD9FufVw4pZkPNgoyithUzgIZQ1bYkZBlB-07rGX6l_2dfdpDeJ8ycgFNiURPhO-amLo3RvbDaUOSdw5CDZXE_F45Bdouomr0Q_nP14dPa23sKExJ2A6-_eNRk6AwC1bXkqo7m0zcvYhmiadeNHFzyzrgVV_ZZR_NfTPrlNNWNzcicfHvPGpKr852XHvFIg"

COOKIES = {
    "reddit_session": REDDIT_SESSION_COOKIE
}

# 1. Your 12 specific gold discussion threads
SPECIFIC_THREAD_URLS = [
    "https://www.reddit.com/r/JKreacts/s/dInEGRAvDP",
    "https://www.reddit.com/r/pj_explained/s/Hs7KKcUq8b",
    "https://www.reddit.com/r/KollyCircleJerk/s/f0nWdBD1pM",
    "https://www.reddit.com/r/tamilmemes/s/Y3c3Y8XASC",
    "https://www.reddit.com/r/IndianMemeTemplates/s/A8LIgBbSLo",
    "https://www.reddit.com/r/KollyGossips/s/X0lez6GHxM",
    "https://www.reddit.com/r/TamilCollegeRant/s/ESMlNR2r5I",
    "https://www.reddit.com/r/MemeVideos/s/luQAULPDvg",
    "https://www.reddit.com/r/superheroes/s/KmLRJQuz53",
    "https://www.reddit.com/r/kollywood/s/7DUws1Z45A",
    "https://www.reddit.com/r/tamilmemes/s/hkUxQ9Pp4q",
    "https://www.reddit.com/r/tamilyapping/s/h9ZaxmPU4R",
]

# 2. Target subreddits to stream live conversational feeds from
STREAM_SUBREDDITS = [
    "TamilCollegeRant",
    "tamilyapping",
    "chennai",
    "indiasocial",
    "developersIndia",
    "tamilmemes",
    "KollyCircleJerk",
    "JKreacts"
]

TARGET_PER_STREAM_SUB = 1500

# ============================================================
# CLEANING & TEXT VALIDATION
# ============================================================
def clean_text(text: str) -> str:
    text = re.sub(r"https?://\S+", "", text)
    text = re.sub(r"^>.*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"\[.*?\]\(.*?\)", "", text)
    return " ".join(text.split())

def is_chat_syntax(text: str) -> bool:
    words = text.split()
    # Filter strictly for chat-length dialogue
    if not (2 <= len(words) <= 14):
        return False
    blocklist = ["[deleted]", "[removed]", "automoderator", "bot", "discord.gg"]
    return not any(b in text.lower() for b in blocklist)

# ============================================================
# PART 1: EXTRACT SPECIFIC THREADS (FULL RECURSIVE TREE)
# ============================================================
def resolve_share_link(url: str) -> str:
    """Resolves Reddit mobile /s/ share link to canonical .json endpoint."""
    try:
        res = requests.get(
            url,
            cookies=COOKIES,
            impersonate="chrome120",
            allow_redirects=True,
            timeout=12
        )
        parsed = urlparse(res.url)
        path_parts = parsed.path.strip("/").split("/")
        if "comments" in path_parts:
            c_idx = path_parts.index("comments")
            sub_name = path_parts[1]
            post_id = path_parts[c_idx + 1]
            return f"https://old.reddit.com/r/{sub_name}/comments/{post_id}.json"
    except Exception as e:
        print(f"Error resolving {url}: {e}")
    return None

def recurse_comment_tree(nodes: list, out_list: list):
    """Walks the full nested comment tree down to 1-on-1 replies."""
    for node in nodes:
        if node.get("kind") != "t1":
            continue
        data = node.get("data", {})
        cleaned = clean_text(data.get("body", ""))
        if is_chat_syntax(cleaned):
            out_list.append(cleaned)
        
        replies = data.get("replies")
        if isinstance(replies, dict):
            sub_children = replies.get("data", {}).get("children", [])
            recurse_comment_tree(sub_children, out_list)

def scrape_thread(json_url: str) -> list[str]:
    results = []
    try:
        res = requests.get(json_url, cookies=COOKIES, impersonate="chrome120", timeout=12)
        if res.status_code == 200:
            data = res.json()
            if len(data) >= 2:
                top_comments = data[1].get("data", {}).get("children", [])
                recurse_comment_tree(top_comments, results)
    except Exception as e:
        print(f"Error reading thread {json_url}: {e}")
    return results

# ============================================================
# PART 2: STREAM RECENT SUBREDDIT COMMENTS
# ============================================================
def stream_subreddit_feed(sub_name: str, target_count: int) -> list[str]:
    collected = []
    after_token = None
    print(f"\n[Stream] Harvesting r/{sub_name} comments feed...")

    while len(collected) < target_count:
        url = f"https://old.reddit.com/r/{sub_name}/comments.json?limit=100"
        if after_token:
            url += f"&after={after_token}"
            
        try:
            res = requests.get(url, cookies=COOKIES, impersonate="chrome120", timeout=12)
            if res.status_code == 429:
                print("Rate limited (429). Sleeping 10s...")
                time.sleep(10)
                continue
            elif res.status_code != 200:
                print(f"HTTP {res.status_code} received. Skipping to next subreddit.")
                break

            payload = res.json().get("data", {})
            children = payload.get("children", [])
            if not children:
                break

            for child in children:
                raw_body = child.get("data", {}).get("body", "")
                cleaned = clean_text(raw_body)
                if is_chat_syntax(cleaned):
                    collected.append(cleaned)

            after_token = payload.get("after")
            print(f" -> r/{sub_name}: {len(collected)} / {target_count} comments gathered.")
            time.sleep(1.8)

            if not after_token:
                break
        except Exception as e:
            print(f"Connection issue on r/{sub_name}: {e}")
            break

    return collected[:target_count]

# ============================================================
# MAIN ORCHESTRATOR
# ============================================================
def main():
    master_corpus = []
    start_time = time.time()

    print("=====================================================")
    print("PHASE 1: SCRAPING SPECIFIC TARGET DISCUSSION THREADS")
    print("=====================================================")
    for idx, share_url in enumerate(SPECIFIC_THREAD_URLS, 1):
        print(f"[{idx}/{len(SPECIFIC_THREAD_URLS)}] Resolving: {share_url}")
        json_url = resolve_share_link(share_url)
        if json_url:
            comments = scrape_thread(json_url)
            print(f" -> Harvested {len(comments)} comments from thread.")
            master_corpus.extend(comments)
        time.sleep(1.5)

    print("\n=====================================================")
    print("PHASE 2: STREAMING LIVE FEEDS FROM TARGET SUBREDDITS")
    print("=====================================================")
    for sub in STREAM_SUBREDDITS:
        stream_comments = stream_subreddit_feed(sub, TARGET_PER_STREAM_SUB)
        master_corpus.extend(stream_comments)

    # De-duplicate across both streams
    unique_corpus = list(dict.fromkeys(master_corpus))
    duration = time.time() - start_time

    print("\n" + "=" * 65)
    print(f"SCRAPING COMPLETE in {duration / 60:.1f} minutes!")
    print(f"Total Unique Conversational Lines Gathered: {len(unique_corpus):,}")
    print("=" * 65)

    output_filename = "unified_reddit_chat_corpus.json"
    with open(output_filename, "w", encoding="utf-8") as f:
        json.dump(unique_corpus, f, ensure_ascii=False, indent=2)

    print(f"Saved complete unified dataset to '{output_filename}'.")

if __name__ == "__main__":
    main()