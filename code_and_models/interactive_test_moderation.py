"""
Interactive CLI REPL for live moderation testing, latency profiling,
and edge-case verification for Tamil and Tanglish text.
"""

import os
import sys
import time
import joblib
import ahocorasick
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import FeatureUnion

STAGE1_TRIE_FILE = "stage1_trie.joblib"
STAGE2_MODEL_FILE = "stage2_classifier.joblib"


def is_boundary_match(text: str, start_idx: int, end_idx: int) -> bool:
    """Validates word boundary on both sides using alphanumeric & Tamil character checks."""
    def is_word_char(c: str) -> bool:
        return c.isalnum() or ("\u0b80" <= c <= "\u0bff")

    if start_idx > 0 and is_word_char(text[start_idx - 1]):
        return False
    if end_idx + 1 < len(text) and is_word_char(text[end_idx + 1]):
        return False
    return True


def load_pipeline():
    if not os.path.exists(STAGE1_TRIE_FILE) or not os.path.exists(STAGE2_MODEL_FILE):
        print("[!] Error: Required .joblib artifacts missing. Please train or provide models.")
        sys.exit(1)

    trie = joblib.load(STAGE1_TRIE_FILE)
    clf = joblib.load(STAGE2_MODEL_FILE)
    return trie, clf


def evaluate(text: str, trie, clf, threshold: float = 0.50):
    t0 = time.perf_counter()
    clean = text.strip().lower()

    # Stage 1: Deterministic Aho-Corasick Scan (< 25 µs)
    matches = []
    for end_idx, matched_word in trie.iter(clean):
        start_idx = end_idx - len(matched_word) + 1
        if is_boundary_match(clean, start_idx, end_idx):
            matches.append(matched_word)

    t1 = time.perf_counter()
    stage1_us = (t1 - t0) * 1_000_000

    if matches:
        return {
            "is_blocked": True,
            "stage": 1,
            "reason": f"STAGE_1_EXPLICIT_SLUR: {list(set(matches))}",
            "probability": 1.0,
            "stage1_latency_us": round(stage1_us, 2),
            "stage2_latency_us": 0.0,
            "total_latency_us": round(stage1_us, 2)
        }

    # Stage 2: Sarcasm / Mock-Praise Classifier (< 250 µs)
    t2 = time.perf_counter()
    prob = float(clf.predict_proba([text])[0][1])
    t3 = time.perf_counter()
    stage2_us = (t3 - t2) * 1_000_000

    is_blocked = prob >= threshold
    reason = "STAGE_2_HOSTILITY_OR_SARCASM" if is_blocked else "CLEAN_CONVERSATION"

    return {
        "is_blocked": is_blocked,
        "stage": 2,
        "reason": reason,
        "probability": round(prob, 4),
        "stage1_latency_us": round(stage1_us, 2),
        "stage2_latency_us": round(stage2_us, 2),
        "total_latency_us": round(stage1_us + stage2_us, 2)
    }


def main():
    print("=" * 65)
    print("  Tamil / Tanglish Low-Latency Content Moderation Engine")
    print("=" * 65)
    trie, clf = load_pipeline()
    print("[*] Pipeline ready. Enter message to test ('exit' to quit).\n")

    while True:
        try:
            line = input("[Message] > ").strip()
            if not line:
                continue
            if line.lower() in ("exit", "quit", "q"):
                break

            res = evaluate(line, trie, clf)
            print("-" * 65)
            print(f"Blocked      : {res['is_blocked']}")
            print(f"Stage        : {res['stage']}")
            print(f"Reason       : {res['reason']}")
            print(f"Probability  : {res['probability']}")
            print(f"Total Latency: {res['total_latency_us']} µs (S1: {res['stage1_latency_us']} µs, S2: {res['stage2_latency_us']} µs)")
            print("-" * 65)
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            break


if __name__ == "__main__":
    main()
